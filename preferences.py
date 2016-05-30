from gi.repository import Gtk

class Pref (object):

    



    def __init__(self):
        self.builder = Gtk.Builder()
        self.running = False
        
        

    def run(self, games, streams):
        self.running = True
        self.builder.add_from_file("preferences.glade")
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("prefWindow")
        self.numGamesInput = self.builder.get_object("numGamesInput")
        self.numStreamsInput = self.builder.get_object("numStreamsInput")
        self.frame = self.builder.get_object("frame1")
        self.radioStreamer = self.builder.get_object("radioStreamer")
        self.radioBrowser = self.builder.get_object("radioBrowser")


        #print self.radioBrowser.get_active()
        self.numGamesInput.set_value(games)
        self.numStreamsInput.set_value(streams)
        #debug
        print (games)
        print (streams)
        self.window.show_all()
        Gtk.main()


    def on_buttonOK_clicked(self, *args):
        nG =  self.numGamesInput.get_value_as_int()
        nS = self.numStreamsInput.get_value_as_int()
        header = "[default]"
        complete = header + '\n' + "num_games=" + `nG` + '\n'+ "num_streams= " + `nS`

        f = open('default.cfg','w')
        f.write(complete)
        self.on_prefWindow_destroy()

    def kill(self):
        Gtk.main_quit()


    def on_prefWindow_destroy(self, *args):
        print ("set to FALSE")
        self.running = False
        self.window.hide()
        Gtk.main_quit()
        #self.running = False
