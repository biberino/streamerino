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

        self.numGamesInput.set_value(games)
        self.numStreamsInput.set_value(streams)
        self.window.show_all()
        Gtk.main()


    def on_buttonOK_clicked(self, *args):
        print (self.numGamesInput.get_value_as_int())
        print (self.numStreamsInput.get_value_as_int())
        self.on_prefWindow_destroy()

    def kill(self):
        Gtk.main_quit()


    def on_prefWindow_destroy(self, *args):
        print ("set to FALSE")
        self.running = False
        self.window.hide()
        Gtk.main_quit()
        #self.running = False
