from tkinter import Frame, Tk, Label
import tkinter.font as TkFont
import praw


class Ticker(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")
        self._offsetx = 0
        self._offsety = 0
        self.parent = parent #sets parent frame, the default TK window.
        self.parent.title("TICKER WINDOW")
        font = tkFont.Font(family="Berlin Sans FB", size=30)
        self.label = Label(self, text="", font=font, fg="#606060", bg="#646464")
        self.label.pack()
        self.configure(background="#646464")
        self.parent.overrideredirect(True)
        self.label.bind("<Button-1>", self.on_click)
        self.parent.bind("<Button-1>", self.on_click)
        self.parent.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<Button-3>", self.on_exit)
        self.parent.wm_attributes("-transparentcolor", "#646464") #sets specific color as transparent.
        #self.parent.attributes('-alpha', 0.) #sets background alpha channel
        self.pack(expand=True) #pack frame

    def on_click(self, e):
        self._offsetx = e.x
        self._offsety = e.y

    def on_drag(self, e):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.parent.geometry('+{x}+{y}'.format(x=x, y=y))

    def update_label(self, string):
        self.label.config(text=string)
        #print "called"
        self.label.pack()
        self.pack(expand=True)

    def on_exit(self, e):
        #todo exit application
        self.parent.quit()

class TextObject: #for right now this will not support URL clicking. This is just a widget for displaying the text
    index=0
    start_index=0
    str_builder=""
    def __init__(self, string, max_letters=65):
        self.string = string
        self.max_letters = max_letters
        self.index = max_letters
        self.str_builder = self.string[0:self.max_letters]

    def get_next_fragment(self): #
        if self.index < len(self.string):
            #print "%d" % self.index
            #adds chars one at a time to the str_builder string.
            # Every time it does this it also removes one from the front of the string
            self.str_builder =  self.str_builder[1:] + self.string[self.index]
            self.index += 1 #increase the string index to grab the next char
            return self.str_builder
        else:
            self.index=0
            #self.start_index=0
            #self.str_builder = " "
            return self.str_builder

def connect_to_reddit():
    r = praw.Reddit("Reddit News Ticker")
    posts = r.get_subreddit("news").get_hot(limit=3)
    title_string = ""
    for post in posts:
        title_string += post.title.upper() + u"\u25BA"
    return TextObject(title_string)


#called once every n milliseconds by the graphics thread, wakes this thread to start changing the text
def update_event():
    ticker_window.update_label(news_tick.get_next_fragment())
    ticker_window.after(400, update_event)

#start window
news_tick = connect_to_reddit()
root_frame = Tk()
root_frame.resizable(0,0)
ticker_window = Ticker(root_frame) #create instance of ticker frame window and pass in Tk root window
root_frame.after(400, update_event)
root_frame.mainloop()