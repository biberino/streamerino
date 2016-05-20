#this is an application to browse and watch (via livestreamer) twitch.tv steams
#it is under development at the moment
#the code is free, feel free to contribute



from gi.repository import Gtk
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
#fuer constante


num_tabs = 10
num_streams = 15


class Streamerino (object):

    tabLabels = []
    tabTextAreas = []
    games = []
    viewers = []
    containers = []
    content_labels = [[0 for x in range(num_streams)] for y in range(num_tabs)] 
    content_pics = [[0 for x in range(num_streams)] for y in range(num_tabs)] 
    urls = [[0 for x in range(num_streams)] for y in range(num_tabs)]

    load = True
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("gui.glade")
        self.builder.connect_signals(self)



    def get_live_games(self):
        url = 'https://api.twitch.tv/kraken/games/top'
        contents = urllib2.urlopen(url)
        decoded = json.loads(contents.read())
        for i in range(0,num_tabs):
            buf = json.dumps(decoded['top'][i]['game']['name'],sort_keys=True, indent=4)
            buf = buf[1:-1]
            self.games.append(buf)
            self.viewers.append(json.dumps(decoded['top'][i]['viewers'],sort_keys=True, indent=4))

    def run(self):
        self.get_live_games()
        self.window = self.builder.get_object("mainWindow")
        self.gameTabs = self.builder.get_object("gameTabs");

        #create tabs
        self.createSubsites()

        for i in range(0,num_tabs):
            buf = (Gtk.Label(self.games[i] + "\n" +
                        "Viewers: " + self.viewers[i]))
            #print buf.get_justify()
            #buf.set_justify(gtk.JUSTIFY_CENTER)
            buf.set_alignment(xalign=0,yalign=0.5)
            self.tabLabels.append(buf)
            self.tabTextAreas.append(Gtk.TextView())
            self.gameTabs.append_page(self.containers[i],self.tabLabels[i])





        self.window.show_all()
        self.gameTabs.set_current_page(0);
        self.load = False
        Gtk.main()

    def startStream(self,widget, data =None):
        tab = self.gameTabs.get_current_page()
        print ("Starting " + self.urls[tab][data])

        subprocess.Popen(["livestreamer",self.urls[tab][data],"best"])
        
        


    def createSubsites(self):
        for i in range (0,num_tabs):
            scrolled_window = Gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
            scrolled_window.set_policy(Gtk.PolicyType.ALWAYS,
                    Gtk.PolicyType.ALWAYS)
            vbox = Gtk.VBox(homogeneous=False, spacing=0)
            scrolled_window.add_with_viewport(vbox)
            for s in range(0,num_streams):
                hbox = Gtk.HBox(homogeneous=False, spacing=0)
                self.content_labels[i][s] = Gtk.Label("jojo")
                self.content_pics[i][s] = Gtk.Image()


                button = Gtk.Button("watch")
                button.connect("clicked",self.startStream, s)
                hbox.pack_start(button,True,True,0)


                hbox.pack_start(self.content_pics[i][s],True,True,0)
                hbox.pack_start(self.content_labels[i][s],True,True,0)
                vbox.pack_start(hbox,True,True,0)


            self.containers.append(scrolled_window)


    def getGameInfo(self,index):
        game = self.games[index].replace(" ", "%20")
        #print (game)

        url = 'https://api.twitch.tv/kraken/streams?game=' + game

        contents = urllib2.urlopen(url)
        decoded = json.loads(contents.read())
        #print (decoded["streams"])
        #buf = self.tabTextAreas[index].get_buffer()
        #it = buf.get_start_iter()
        #buf.set_text('')
        #self.containers[index].get_children()
       
        for i in range(0,num_streams):
            pic_buf = json.dumps(decoded['streams'][i]['preview']['medium'],sort_keys=True, indent=4)
            if pic_buf is not "null":
                pic_buf = pic_buf[1:-1]
                print (pic_buf)
                file_pic = cStringIO.StringIO(urllib2.urlopen(pic_buf).read())
                img = Image.open(file_pic)

                p = self.image2pixbuf(numpy.array(img))
                scaled_buf = p.scale_simple(200,112,GdkPixbuf.InterpType.BILINEAR)
                self.content_pics[index][i].set_from_pixbuf(scaled_buf)
            



            info = json.dumps(decoded['streams'][i]['viewers'],sort_keys=True, indent=4) + "\n"
            info = info + json.dumps(decoded['streams'][i]['channel']['name'],sort_keys=True, indent=4)
	    self.content_labels[index][i].set_text(info)

            self.urls[index][i] = json.dumps(decoded['streams'][i]['channel']['url'],sort_keys=True, indent=4)[1:-1]
            

            #buf.insert_at_cursor("\n")



    def on_gameTabs_switch_page(self, page, content, number):
        if not self.load:
            self.getGameInfo (number)


    def on_mainWindow_destroy(self, *args):
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






Streamerino().run()



