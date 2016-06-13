#this is an application to browse and watch (via livestreamer) twitch.tv steams
#it is under development at the moment
#the code is free, feel free to contribute



from gi.repository import Gtk, Gdk
from gi.repository import GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf as Pix

import urllib2
import json
import cStringIO
from PIL import Image
import numpy
import array
import cv2
import subprocess
from thread import start_new_thread

import ConfigParser, os
import threading
import time


#preference window
from preferences import Pref





#TODO: add function to create or delete more tabs/streams on the fly when
#preferences get changed

class Streamerino (object):
    num_tabs = 20
    num_streams = 15

    tabLabels = [] #contains the Gameinfo
    games = [] #contains the names of the games
    viewers = [] # contains the viewer count per game
    containers = [] #contains the subsites
    captions = [] 
    gamePics = [] #contains the url of the game pics
    currentTab=0
    content_pics_games = []
    livestreamerOutputLabels = []

    #cursor for mouse over pic
    cursor = Gdk.Cursor(Gdk.CursorType.HAND1)
    
    
    #moved to init, need to do it after config was read
    #content_labels = [[0 for x in range(num_streams)] for y in range(num_tabs)] 
    #content_pics = [[0 for x in range(num_streams)] for y in range(num_tabs)] 
    #urls = [[0 for x in range(num_streams)] for y in range(num_tabs)]

    old_data = None #needed to remove color from unactive subsites

    hover_color = '#FF3FFC'
    normal_color = '#EDEDED' #basic gtk color
    active_color = '#C4FF8D'

    
    #TODO is this still needed?
    load = True

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("gui.glade")
        self.builder.connect_signals(self)
        self.readConfig()
        self.content_labels = [[0 for x in range(self.num_streams)] for y in range(self.num_tabs)] 
        self.content_pics = [[0 for x in range(self.num_streams)] for y in range(self.num_tabs)] 
        self.urls = [[0 for x in range(self.num_streams)] for y in range(self.num_tabs)]



    #fills self.games and self.viewers, self.gamePics with data
    def get_live_games(self):
        self.games = []
        self.viewers = []
        self.gamePics = []
        url = 'https://api.twitch.tv/kraken/games/top?limit=' + str(self.num_tabs)
        contents = urllib2.urlopen(url)
        decoded = json.loads(contents.read())
        for i in range(0,self.num_tabs):
            buf = json.dumps(decoded['top'][i]['game']['name'],sort_keys=True, indent=4)
            buf = buf[1:-1]
            print buf
            self.games.append(buf)
            buf2 = json.dumps(decoded['top'][i]['viewers'],sort_keys=True, indent=4)
            print buf2
            self.viewers.append(buf2)
            buf3 = json.dumps(decoded['top'][i]['game']['box']['small'],sort_keys=True, indent=4)
            print buf3
            self.gamePics.append(buf3)


    def run(self):
        self.get_live_games()
        self.window = self.builder.get_object("mainWindow")
        self.mainBox = self.builder.get_object("mainBox")
        self.progressbar = self.builder.get_object("progressbarMain")
        self.buttonRefreshGames = self.builder.get_object("buttonRefreshGames")
        self.spinnerGames = self.builder.get_object("spinnerGames")
        self.aboutdialog = self.builder.get_object("aboutdialog")
        self.scrollGames = self.builder.get_object("scrollGames")
        self.textInfo = self.builder.get_object("textInfo")

        self.modifyColor(self.buttonRefreshGames,self.hover_color,Gtk.StateFlags.PRELIGHT)


    

        

        self.prefWindow = Pref()

        

        #create tabs
        self.createSubsites()

        #new code
        self.createGameList()
        
        #set welcome page
        self.createWelcomePage()

        #fill games tabs with data
        self.on_buttonRefreshGames_clicked()



        self.window.show_all()
        #self.gameTabs.set_current_page(0);
        self.load = False
        Gtk.main()


    def createWelcomePage(self):

        self.builderWelcome = Gtk.Builder()
        self.builderWelcome.add_from_file("welcome.glade")
        self.builderWelcome.connect_signals(self)


        path = which("livestreamer")
        
        if path is None:
            #TODO react to it
            msg="<span size='16000' color='red'>unable to find livestreamer\nonly browser backend supported</span>"
        else:
            msg="<span size='16000' color='green' font_desc='Gentium Book'> " + u'\u2713' + "livestreamer found: " + path +"</span>"

        welcomeContainer = self.builderWelcome.get_object("box1")
        lblLivestreamerInfo = self.builderWelcome.get_object("lblLivestreamerInfo")
        lblStreamsInfo = self.builderWelcome.get_object("lblStreamsInfo")


        lblLivestreamerInfo.set_markup(msg)
    
        buf = str(self.num_tabs) + " Games will be loaded\n"
        buf += str(self.num_streams) + " Streams per Game will be loaded"
        constInfo = formatString(buf,"16000","purple")
        lblStreamsInfo.set_markup(constInfo)


        
        
        self.last = welcomeContainer
  
    
        self.mainBox.add(welcomeContainer)
   
   


    def createGameList(self):
        vbox = Gtk.VBox(False,25)
        self.scrollGames.add_with_viewport(vbox)
        #dummy box
        self.last_box = None
        for i in range(0,self.num_tabs):
            hbox = Gtk.HBox(False,25)
            buf = (Gtk.Label())
            buf.set_use_markup(True)
            buf.set_alignment(xalign=0,yalign=0.5)
            self.tabLabels.append(buf)
            #on_buttonRefreshGames_clicked does that now
            #self.updateLabel(i)
            eventbox = Gtk.EventBox()
            
            #self.modifyColor(eventbox,self.hover_color,Gtk.StateFlags.NORMAL)
            eventbox.connect('button-press-event',self.switchTab,i)
            self.modifyWidgetStateBehaviour(eventbox,self.normal_color,Gtk.StateType.NORMAL)
            
            
            #self.modifyWidgetStateBehaviour(hbox,self.normal_color,Gtk.StateType.NORMAL)
            eventbox.add(self.tabLabels[i])
            
            self.content_pics_games.append(Gtk.Image())
            hbox.pack_start(self.content_pics_games[i],False,False,0)
            hbox.pack_start(eventbox,False,False,0)
         
            vbox.pack_start(hbox,False,False,0)
            
        


        
        

    def switchTab(self, w, e, data):
        print self
        print w
        if self.last_box is not None:
            self.modifyWidgetStateBehaviour(self.last_box,self.normal_color,Gtk.StateType.NORMAL)
        self.last_box = w
        self.mainBox.remove(self.last)
        self.modifyWidgetStateBehaviour(w,self.active_color,Gtk.StateType.NORMAL)
        self.mainBox.add(self.containers[data])
        self.last = self.containers[data]
        self.currentTab = data
        self.containers[data].show_all()
        self.mainBox.show_all()



    def modifyWidgetStateBehaviour(self, w, cHex, stateType):
        rgba = Gdk.RGBA()
        rgba.parse(cHex)
        color = rgba.to_color()
        w.modify_bg(stateType,color)

    def modifyColor(self,w,cHex,stateFlag):
        rgba = Gdk.RGBA()
        rgba.parse(cHex)
        w.override_color(stateFlag,rgba)


    #fills tabLabel[index] with formatted data
    def updateLabel(self, index):
        markupstring = "<span foreground='purple' size='12000' font_desc='Sans Normal'>"
        markupstring += self.games[index] + "</span>" + "\n"
        markupstring +=  "<span foreground='purple' size='9500' font_desc='Sans Normal'>" + "Viewers: " + self.viewers[index] + "</span>"
        self.tabLabels[index].set_markup(markupstring)

    def startStream(self,widget,event, data =None):
        tab = self.currentTab
        print ("Starting " + self.urls[tab][data])

        process = subprocess.Popen(["livestreamer",self.urls[tab][data],"best"], stdout = subprocess.PIPE)
        threading.Thread(target=self.getLivestreamerOutput, args=[process]).start()
        

    def getLivestreamerOutput(self,process):
        while (process.poll() is None):
            #this is blocking if no data is awailable
            out = process.stdout.readline()
            self.say(out)
            #time.sleep(3)
        print "Process ended"

    def say(self, msg):
        textBuffer = self.textInfo.get_buffer()
        textBuffer.insert(textBuffer.get_end_iter(),msg)
        self.textInfo.set_buffer(textBuffer)

        


    def createSubsites(self):
        for i in range (0,self.num_tabs):
            scrolled_window = Gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
            scrolled_window.set_policy(Gtk.PolicyType.ALWAYS,
                    Gtk.PolicyType.ALWAYS)
            vbox = Gtk.VBox(False,25)
            vboxCap = Gtk.VBox(False,25)
            scrolled_window.add_with_viewport(vbox)
            self.captions.append(Gtk.Label("No data loaded. Click refresh to load stream data"))
            self.captions[i].set_use_markup(True)

            vboxCap.pack_start(self.captions[i],False,False,0)
            fixedContainer = Gtk.Fixed()
            
            pb = Pix.new_from_file_at_size('refresh.png', 20,20)
            refIm = Gtk.Image()
            refIm.set_from_pixbuf(pb)

            refButton = Gtk.Button(label="refresh streams", image=refIm)
            refButton.set_size_request(10,10)
            #connect button
            refButton.connect("clicked",self.on_refresh_streams_click)
            #set button color
            self.modifyColor(refButton,self.hover_color,Gtk.StateFlags.PRELIGHT)

            fixedContainer.put(refButton,10,0)

            vboxCap.pack_start(fixedContainer,False,False,0)

            vbox.pack_start(vboxCap,False,False,0)
            for s in range(0,self.num_streams):

                #test fixed container
                fixed = Gtk.Fixed()
                hbox = Gtk.HBox(False,20)
                self.content_labels[i][s] = Gtk.Label("no data")
                self.content_labels[i][s].set_use_markup(True)

                #added eventbox 
                eventbox = Gtk.EventBox()
                eventbox.connect('button-press-event',self.startStream,s)
                eventbox.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
                eventbox.connect("motion-notify-event",self.mouse_over_pic,s)
                eventbox.connect("realize",self.set_cursor)
                
                #self.gameTabs.add_events(Gdk.EventMask.SCROLL_MASK
                #self.modifyWidgetStateBehaviour(eventbox,self.active_color,Gtk.StateType.PRELIGHT)
                
                self.content_pics[i][s] = Gtk.Image()
                eventbox.add(self.content_pics[i][s])


                button = Gtk.Button("watch")
                button.connect("clicked",self.startStream, s)
                self.modifyColor(button,self.hover_color,Gtk.StateFlags.PRELIGHT)

                button.set_size_request(10,2)
                fixed.put(button,10,25)


                #hbox.pack_start(fixed,False,False,0)
                hbox.pack_start(eventbox,False,False,0)
                #hbox.pack_start(self.content_pics[i][s],False,False,0)
                hbox.pack_start(self.content_labels[i][s],False,False,0)
                vbox.pack_start(hbox,False,False,0)


            #test
            self.containers.append(scrolled_window)


    def set_cursor(self, w):
        w.get_window().set_cursor(self.cursor)

    def mouse_over_pic(self,w,e, data):

        if self.old_data is not None:
            self.modifyWidgetStateBehaviour(self.content_labels[self.currentTab][self.old_data],self.normal_color,Gtk.StateType.NORMAL)
        self.modifyWidgetStateBehaviour(self.content_labels[self.currentTab][data],self.active_color,Gtk.StateType.NORMAL)
        self.old_data = data



    def getGameInfo(self,index):
        self.spinnerGames.start()
        game = self.games[index].replace(" ", "%20")
        info = ""
        #print (game)
        self.progressbar.set_fraction(0)

        url = 'https://api.twitch.tv/kraken/streams?game=' + game

        contents = urllib2.urlopen(url)
        decoded = json.loads(contents.read())

        step = 100.0 / self.num_streams
        val = 0
        self.captions[index].set_markup('<span font_desc="Bookman Uralic Bold" size="35000" color="purple">' + self.games[index] + '</span>')
       
        for i in range(0,self.num_streams):
            pic_buf = json.dumps(decoded['streams'][i]['preview']['medium'],sort_keys=True, indent=4)
            if pic_buf is not "null":
                pic_buf = pic_buf[1:-1]
                print (pic_buf)
                file_pic = cStringIO.StringIO(urllib2.urlopen(pic_buf).read())
                img = Image.open(file_pic)

                p = self.image2pixbuf(numpy.array(img))
                scaled_buf = p.scale_simple(200,112,GdkPixbuf.InterpType.BILINEAR)
                self.content_pics[index][i].set_from_pixbuf(scaled_buf)
            


            name = json.dumps(decoded['streams'][i]['channel']['name'],sort_keys=True, indent=4)[1:-1]
            display_name = json.dumps(decoded['streams'][i]['channel']['display_name'],sort_keys=True, indent=4)[1:-1]
            viewers = json.dumps(decoded['streams'][i]['viewers'],sort_keys=True, indent=4)
            lang = json.dumps(decoded['streams'][i]['channel']['broadcaster_language'],sort_keys=True, indent=4)[1:-1]
            status = name = json.dumps(decoded['streams'][i]['channel']['status'],sort_keys=True, indent=4)[1:-1]

        
	    


            info = ""
            info = "<span color='purple' size='15000'>"
            info = info +"<b>Name:</b> " + display_name + "\n"
            info = info +"<b>Viewers:</b> " +  viewers + "\n"
            info = info + "<b>Language:</b> " + lang + "\n"
            info = info + "<b>Status:</b> " + status + "\n"
            info = info + "</span>"
            self.content_labels[index][i].set_markup(info)

            self.urls[index][i] = json.dumps(decoded['streams'][i]['channel']['url'],sort_keys=True, indent=4)[1:-1]
            val = val + step;
            print (val)
            self.progressbar.set_fraction((val/100.0)+0.1)

            
        self.spinnerGames.stop()



    #assuming self.content_pics_games was created and self.gamePics contains the
    #urls
    def get_Game_pics(self):
        for i in range (0,self.num_tabs):
            pic_buf = self.gamePics[i]
            if pic_buf is not "null":
                pic_buf = pic_buf[1:-1]
                print (pic_buf)
                file_pic = cStringIO.StringIO(urllib2.urlopen(pic_buf).read())
                img = Image.open(file_pic)

                p = self.image2pixbuf(numpy.array(img))
                #scaled_buf = p.scale_simple(200,112,GdkPixbuf.InterpType.BILINEAR)
                self.content_pics_games[i].set_from_pixbuf(p)


    def on_gameTabs_scroll(self, widget, event):
        print ("scrolled")
        if event.get_scroll_deltas()[2] < 0:
            self.gameTabs.prev_page()
        else:
            self.gameTabs.next_page()

    def readConfig(self):
        config = ConfigParser.ConfigParser()
        config.readfp(open('default.cfg'))
        self.num_streams =  config.getint('default','num_streams')
        self.num_tabs =  config.getint('default','num_games')





    def on_refresh_streams_click(self, *args):
        self.say("Refreshing " + str(self.num_streams) + " streams\n")
        if not self.load:
            start_new_thread(self.getGameInfo,(self.currentTab,))

    def on_buttonRefreshGames_clicked(self, *args):
        self.say("Refreshing " + str(self.num_tabs) + " games\n")
        start_new_thread(self.update_games_thread,(None,))

        
    def update_games_thread(self, *args):
        self.spinnerGames.start()
        print ("Refreshing")
        self.get_live_games()
        for i in range(0,self.num_tabs):
            self.updateLabel(i)
        self.get_Game_pics()

        self.spinnerGames.stop()




    def on_mainWindow_destroy(self, *args):
        self.prefWindow.kill()
        Gtk.main_quit()



    def image2pixbuf(self,im): 
        # convert image from BRG to RGB (pnm uses RGB)
        im2 = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        # get image dimensions (depth is not used)
        height, width, depth = im2.shape
        pixl = GdkPixbuf.PixbufLoader.new_with_type('pnm')
        # P6 is the magic number of PNM format, 
        # and 255 is the max color allowed
        pixl.write("P6 %d %d 255 " % (width, height) + im2.tostring())
        pix = pixl.get_pixbuf()
        pixl.close()
        return pix


    def on_aboutdialog_destroy(self, *args):
        self.aboutdialog.hide()

    def on_dialog_action_area1_destroy(self, *args):
        self.aboutdialog.hide()


    #-----Menu-Callbacks
    def on_mnuExit_activate(self, *args):
        self.on_mainWindow_destroy()

    def on_mnuInfo_activate(self, *args):
        self.aboutdialog.run()
        self.aboutdialog.hide()


    def on_mnuPref_activate(self, *args):
        print (self.prefWindow.running)
        if self.prefWindow.running == False :
            self.prefWindow.run(self.num_tabs,self.num_streams)






#------------cool helpers-----------

#thanks to stackoverflow
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def formatString(string,size,color):
    buf = "<span color='" + color +"' size='"+ size +"'>"+ string + "</span>"
    return buf


Streamerino().run()



