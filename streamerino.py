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

#from colors import rgb


#preference window
from preferences import Pref





#TODO: add function to create or delete more tabs/streams on the fly when
#preferences get changed

class Streamerino (object):
    num_tabs = 20
    num_streams = 15

    tabLabels = []
    games = []
    viewers = []
    containers = []
    captions = []
    currentTab=0
    #moved to init, need to do it after config was read
    #content_labels = [[0 for x in range(num_streams)] for y in range(num_tabs)] 
    #content_pics = [[0 for x in range(num_streams)] for y in range(num_tabs)] 
    #urls = [[0 for x in range(num_streams)] for y in range(num_tabs)]

    hover_color = '#FF3FFC'
    normal_color = '#EDEDED' #basic gtk color
    active_color = '#C4FF8D'

    

    load = True

    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("gui.glade")
        self.builder.connect_signals(self)
        self.readConfig()
        self.content_labels = [[0 for x in range(self.num_streams)] for y in range(self.num_tabs)] 
        self.content_pics = [[0 for x in range(self.num_streams)] for y in range(self.num_tabs)] 
        self.urls = [[0 for x in range(self.num_streams)] for y in range(self.num_tabs)]



    #fills self.games and self.viewers with data
    def get_live_games(self):
        self.games = []
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

    def run(self):
        self.get_live_games()
        self.window = self.builder.get_object("mainWindow")
        #self.gameTabs = self.builder.get_object("gameTabs")
        self.mainBox = self.builder.get_object("mainBox")
        self.progressbar = self.builder.get_object("progressbarMain")
        self.buttonRefreshGames = self.builder.get_object("buttonRefreshGames")
        self.spinnerGames = self.builder.get_object("spinnerGames")
        self.aboutdialog = self.builder.get_object("aboutdialog")
        self.scrollGames = self.builder.get_object("scrollGames")
        #self.scrollStreams = self.builder.get_object("scrollStreams")

        #self.modifyColor(self.buttonRefreshGames,'#FF0000',Gtk.StateFlags.ACTIVE)
        self.modifyColor(self.buttonRefreshGames,self.hover_color,Gtk.StateFlags.PRELIGHT)


        #set cool colors for the notebook
        #self.modifyWidgetStateBehaviour(self.gameTabs,'#C4FF8D',Gtk.StateType.ACTIVE)
        #self.modifyWidgetStateBehaviour(self.gameTabs,'#DDFFBA',Gtk.StateType.PRELIGHT)

        #self.modifyColor(self.gameTabs,'#FF3FFC',Gtk.StateFlags.ACTIVE)
        #self.modifyColor(self.gameTabs,self.hover_color,Gtk.StateFlags.PRELIGHT)

        

        self.prefWindow = Pref()

        #listen to scroll event
        #self.gameTabs.add_events(Gdk.EventMask.SCROLL_MASK |
        #        Gdk.EventMask.SMOOTH_SCROLL_MASK)
        #self.gameTabs.connect('scroll-event',self.on_gameTabs_scroll)

        

        #create tabs
        self.createSubsites()


        #old notebook code
        '''
        for i in range(0,self.num_tabs):
            buf = (Gtk.Label())
            #enbale markup
            buf.set_use_markup(True)
            #print (self.markup_start + self.games[i] + "\n" + "Viewers: " + self.viewers[i] + self.markup_end)
            #buf.set_markup(self.markup_start + self.games[i] + "\n" + "Viewers: " + self.viewers[i] + self.markup_end)
            #print buf.get_justify()
            #buf.set_justify(gtk.JUSTIFY_CENTER)
            buf.set_alignment(xalign=0,yalign=0.5)
            self.tabLabels.append(buf)
            self.updateLabel(i)
            #self.tabTextAreas.append(Gtk.TextView())
            self.gameTabs.append_page(self.containers[i],self.tabLabels[i])
        '''

        #new code
        self.createGameList()
        
        #set welcome page
        self.createWelcomePage()



        self.window.show_all()
        #self.gameTabs.set_current_page(0);
        self.load = False
        Gtk.main()


    def createWelcomePage(self):
        l = Gtk.Label()
        l.set_use_markup(True)
        l.set_markup("<span foreground='purple' size='16000' font_desc='Gentium BBook'>Welcome to Streamerino V0.8</span>")
        vbox = Gtk.VBox(False,25)
        vbox.pack_start(l,True,True,0)

        l2 = Gtk.Label()
        l2.set_use_markup(True)
        l2.set_markup("<span foreground='purple' size='16000' font_desc='Gentium BBook'>start by choosing a game</span>")
        vbox.pack_start(l2,True,True,0)
        buf = vbox
        self.last = buf
        #self.mainBox.pack_start(buf,True,True,0)
        self.mainBox.add(buf)
        #mainBox.show_all()
        #buf.show()


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
            self.updateLabel(i)
            eventbox = Gtk.EventBox()
            
            #self.modifyColor(eventbox,self.hover_color,Gtk.StateFlags.NORMAL)
            eventbox.connect('button-press-event',self.switchTab,i)
            self.modifyWidgetStateBehaviour(eventbox,self.normal_color,Gtk.StateType.NORMAL)
            
            hbox.pack_start(eventbox,False,False,0)
            #self.modifyWidgetStateBehaviour(hbox,self.normal_color,Gtk.StateType.NORMAL)
            eventbox.add(self.tabLabels[i])
            #signals
            #self.tabLabels[i].add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            #self.tabLabels[i].connect('button-press-event',self.switchTab,"data")
            #self.tabLabels[i].connect('move-cursor',self.switchTab,"data")

            vbox.pack_start(hbox,False,False,0)
            #colors
            #self.modifyWidgetStateBehaviour(self.tabLabels[i],'#DDFFBA',Gtk.StateType.ACTIVE)
            #self.modifyColor(self.tabLabels[i],'#FF3FFC',Gtk.StateFlags.PRELIGHT)
        


        
        

    def switchTab(self, w, e, data):
        print self
        print w
        if self.last_box is not None:
            self.modifyWidgetStateBehaviour(self.last_box,self.normal_color,Gtk.StateType.NORMAL)
        self.last_box = w
        self.mainBox.remove(self.last)
        self.modifyWidgetStateBehaviour(w,self.active_color,Gtk.StateType.NORMAL)
        #self.scrollStreams.remove(self.scrollStreams.get_child())
        #self.scrollStreams.add(self.containers[data])
        self.mainBox.add(self.containers[data])
        self.last = self.containers[data]
        self.currentTab = data
        self.containers[data].show_all()
        self.mainBox.show_all()



        #TODO: listen to different events(mouse buttons)
        #print e.type
        #print event
        #print w


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
        markupstring +=  "<span foreground='purple' size='8000' font_desc='Sans Normal'>" + "Viewers: " + self.viewers[index] + "</span>"
        self.tabLabels[index].set_markup(markupstring)

    def startStream(self,widget, data =None):
        tab = self.currentTab
        print ("Starting " + self.urls[tab][data])

        subprocess.Popen(["livestreamer",self.urls[tab][data],"best"])
        
        


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

            refButton = Gtk.Button("refresh streams")
            refButton.set_size_request(10,2)
            #connect button
            refButton.connect("clicked",self.on_refresh_streams_click)
            #set button color
            self.modifyColor(refButton,self.hover_color,Gtk.StateFlags.PRELIGHT)

            fixedContainer.put(refButton,10,10)

            vboxCap.pack_start(fixedContainer,False,False,0)

            vbox.pack_start(vboxCap,False,False,0)
            for s in range(0,self.num_streams):

                #test fixed container
                fixed = Gtk.Fixed()
                hbox = Gtk.HBox(False,20)
                self.content_labels[i][s] = Gtk.Label("no data")
                self.content_labels[i][s].set_use_markup(True)
                self.content_pics[i][s] = Gtk.Image()


                button = Gtk.Button("watch")
                button.connect("clicked",self.startStream, s)
                self.modifyColor(button,self.hover_color,Gtk.StateFlags.PRELIGHT)

                button.set_size_request(10,2)
                fixed.put(button,10,25)
                hbox.pack_start(fixed,False,False,0)


                hbox.pack_start(self.content_pics[i][s],False,False,0)
                hbox.pack_start(self.content_labels[i][s],False,False,0)
                vbox.pack_start(hbox,False,False,0)


            #test
            self.containers.append(scrolled_window)


    def getGameInfo(self,index):
        self.spinnerGames.start()
        game = self.games[index].replace(" ", "%20")
        info = ""
        #print (game)
        self.progressbar.set_fraction(0)

        url = 'https://api.twitch.tv/kraken/streams?game=' + game

        contents = urllib2.urlopen(url)
        decoded = json.loads(contents.read())
        #print (decoded["streams"])
        #buf = self.tabTextAreas[index].get_buffer()
        #it = buf.get_start_iter()
        #buf.set_text('')
        #self.containers[index].get_children()

        step = 100.0 / self.num_streams
        val = 0
        self.captions[index].set_markup('<b><span font_desc="Bandal" size="35000" color="purple">' + self.games[index] + '</span></b>')
       
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
            


            name = json.dumps(decoded['streams'][i]['channel']['name'],sort_keys=True, indent=4)
            display_name = json.dumps(decoded['streams'][i]['channel']['display_name'],sort_keys=True, indent=4)
            viewers = json.dumps(decoded['streams'][i]['viewers'],sort_keys=True, indent=4)
            lang = json.dumps(decoded['streams'][i]['channel']['broadcaster_language'],sort_keys=True, indent=4)
	    


            info = ""
            info = info +"<b>Name:</b> " + display_name + "\n"
            info = info +"<b>Viewers</b> " +  viewers + "\n"
            info = info + "<b>Language</b> " + lang + "\n"
            self.content_labels[index][i].set_markup(info)

            self.urls[index][i] = json.dumps(decoded['streams'][i]['channel']['url'],sort_keys=True, indent=4)[1:-1]
            val = val + step;
            print (val)
            self.progressbar.set_fraction((val/100.0)+0.1)

            
        self.spinnerGames.stop()



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
        if not self.load:
            start_new_thread(self.getGameInfo,(self.currentTab,))

    def on_buttonRefreshGames_clicked(self, *args):
        start_new_thread(self.update_games_thread,(None,))

        
    def update_games_thread(self, *args):
        self.spinnerGames.start()
        print ("Refreshing")
        self.get_live_games()
        for i in range(0,self.num_tabs):
            self.updateLabel(i)

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






Streamerino().run()




