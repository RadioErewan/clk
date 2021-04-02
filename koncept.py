import sys
from PIL import ImageFont, ImageDraw, ImageColor, Image
import numpy as np
import matplotlib.pyplot as plt
import time
import NDIlib as ndi
import cv2 as cv
from time import sleep
from datetime import datetime
from rss_parser import Parser
from requests import get
import configparser



def init():
    global fontpath1, fontpath2, fontsize1, fontsize2, color1, color2 
    config = configparser.ConfigParser()
    config.read('ticker.ini')
    fontpath1 = config['fonts']['fontpath1'] 
    fontpath2 = config['fonts']['fontpath2'] 


    fontsize1 = config['fonts']['fontsize1']
    fontsize1 = config['fonts']['fontsize1']

    color1 = config['colors']['color1'] 
    color2 = config['colors']['color2'] 



fontpath1 = "/Users/radek/clk/jb.ttf"  
fontpath2 = "/Users/radek/clk/jb.ttf"  
fontpath3 = "/Users/radek/clk/jb.ttf"
fontpath4 = "/Users/radek/clk/jb.ttf"
fontpath5 = "/Users/radek/clk/fa.otf"

color1 = ImageColor.getrgb("#ffff00ff")
color2 = ImageColor.getrgb("#88888800")
color3 = ImageColor.getrgb("#00ff00ff")

fontsize1 = 40
fontsize2 = 40

init()    

font1 = ImageFont.truetype(fontpath1, int(fontsize1))
font2 = ImageFont.truetype(fontpath2, int(fontsize2))






def textwidth(ffont, ftext):
#    width = ffont.getsize(ftext)[0]
    width = len(ftext)   
    return width
def textwidth2(ffont, ftext):
    width = ffont.getsize(ftext)[0]
       
    return width

def addWord (vfont, vtext, ticker):
    ttext = vtext.upper()+" "
    graph = False

    if vtext in ("<>", "><"):
        graph = True
        if vtext == "<>":
            ttext = "\uf0a8"
        else:
            ttext = "\uf0a9"
        twidth = textwidth2(font2,ttext)
    else:
        twidth = textwidth2(vfont,ttext)

    tposition = 1920+960
    ticker.append({'text': ttext, 'width': twidth, 'position': tposition, 'graph': graph})

    return 0

def dropwords(ticker):
    new_list = []
    for word in ticker: 
        if ((int(word['position'])+int(word['width']))>960):
            new_list.append(word) 
    return new_list

def rollit(ticker, step):
    for word in ticker:
        word['position'] = int(word['position']) - step
        if (int(word['position']) + int(word['width']) < 960):
            ticker = dropwords(ticker)
    return ticker
            

def render(ticker, img_pil):
    img_pil.paste( color2, [0,0,img_pil.size[0],img_pil.size[1]])

    draw = ImageDraw.Draw(img_pil)
    y_coor = 10
    all = ""
    for word in ticker:
        all = all+word["text"] 
        if word["graph"]:
            afont = font2  
            draw.text((word["position"] , y_coor+5),  word["text"] , font = afont, fill = color1)       
        else:
            afont = font1
            draw.text((word["position"] , y_coor),  word["text"] , font = afont, fill = color1) 
    
    #draw.text((ticker[0]["position"] , y_coor),  all, font = font1, fill = color1) 
    return img_pil

def loadfeed(url):
    rss_url = url
    xml = get(rss_url)

    # Limit feed output to 5 items
    # To disable limit simply do not provide the argument or use None
    parser = Parser(xml=xml.content, limit=None)
    feed = parser.parse()

    # Print out feed meta data
    print(feed.language)
    print(feed.version)
    text = ""
    # Iteratively print feed items
    for item in feed.feed:
        text = text + item.title + " <> " + item.description + " >< "
        print(item.title)
        print(item.description)
    text = ">< "+ text
    return text
def main(): 
#    text = "Lorem ipsum dolor sit amet enim. Etiam ullamcorper. Suspendisse a pellentesque dui, non felis. Maecenas malesuada elit lectus felis, malesuada ultricies. Curabitur et ligula. Ut molestie a, ultricies porta urna. Vestibulum commodo volutpat a, convallis ac, laoreet enim. Phasellus fermentum in, dolor. Pellentesque facilisis. Nulla imperdiet sit amet magna. Vestibulum dapibus, mauris nec malesuada fames ac turpis velit, rhoncus eu, luctus et interdum adipiscing wisi. Aliquam erat ac ipsum. Integer aliquam purus. Quisque lorem tortor fringilla sed, vestibulum id, eleifend justo vel bibendum sapien massa ac turpis faucibus orci luctus non, consectetuer lobortis quis, varius in, purus. Integer ultrices posuere cubilia Curae, Nulla ipsum dolor lacus, suscipit adipiscing. Cum sociis natoque penatibus et ultrices volutpat. Nullam wisi ultricies a, gravida vitae, dapibus risus ante sodales lectus blandit eu, tempor diam pede cursus vitae, ultricies eu, faucibus quis, porttitor eros cursus lectus, pellentesque eget, bibendum a, gravida ullamcorper quam. Nullam viverra consectetuer. Quisque cursus et, porttitor risus. Aliquam sem. In hendrerit nulla quam nunc, accumsan congue. Lorem ipsum primis in nibh vel risus. Sed vel lectus. Ut sagittis, ipsum dolor quam."
    
    ticker = []
    y_coor = 10
    fromtop = 900

    text = loadfeed("https://tvn24.pl/najnowsze.xml")
    words = text.split()      
    t0= time.time()

    background = np.zeros((150, 3840, 4), np.uint8)
    frame = np.zeros((1080, 1920, 4), np.uint8)

    img_pil = Image.fromarray(background)
    frame_pil = Image.fromarray(frame)
    frame_pil.paste( color2, [0,0,frame_pil.size[0],frame_pil.size[1]])

#    plt.imshow(img_pil) 
    

    a = 50
    ## do we have ndi sdk? if no, there is no reason to run
    if not ndi.initialize():
        return 0

## preconfig of ndi_send object
    send_settings = ndi.SendCreate()
    send_settings.ndi_name = 'NDI-ticker'
    ndi_send = ndi.send_create(send_settings)
    video_frame = ndi.VideoFrameV2()
    wrd = words.pop(0)            
    addWord(font1, wrd, ticker)
    start = datetime.now().microsecond
    t1 = time.time() - t0
    print("Prep time elapsed: ", t1) # CPU seconds elapsed (floating point)
    while 1==1:
        t0= time.time()

        start = datetime.now().microsecond
        ticker = rollit(ticker,2)
        if len(ticker)==0:
            text = loadfeed("https://tvn24.pl/najnowsze.xml")
            #https://tvn24.pl/najnowsze.xml
            words = text.split()          
            wrd = words.pop(0)            
            addWord(font1, wrd, ticker)
        word = ticker[-1]
        if (int(word['position'])+int(word['width']))<=(1920+960):
            if len(words):
                wrd = words.pop(0)            
                addWord(font1, wrd, ticker)

                
            else:
                ticker = dropwords(ticker)
    
        img_pil = render(ticker, img_pil)
        region = img_pil.crop((960, 0, 1920+960, 150))
        frame_pil.paste(region, (0, fromtop))
        img = np.array(frame_pil)

# Specify the kernel size.
# The greater the size, the more the motion.
        kernel_size = 2

# Create the vertical kernel.
        kernel_h = np.zeros((kernel_size, kernel_size))

    # Fill the middle row with ones.
        kernel_h[int((kernel_size - 1)/2), :] = np.ones(kernel_size)

        # Normalize.
        kernel_h /= kernel_size



        # Apply the horizontal kernel.
        img = cv.filter2D(img, -1, kernel_h)

    #    img = cv.cvtColor(img, cv.COLOR_RGB2YUV_YV12) 
#        img = cv.cvtColor(img, cv.COLOR_RGB2BGRA) 

        video_frame.data = img
        video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_RGBA
        video_frame.frame_format_type = ndi.FRAME_FORMAT_TYPE_PROGRESSIVE     
        video_frame.frame_rate_N = 30000
        video_frame.frame_rate_D = 1200
        video_frame.picture_aspect_ratio = 16.0/9.0   
        ndi.send_send_video_v2(ndi_send, video_frame)      
#        sleep(0.05)  
       # print(ticker)
        t1 = time.time() - t0
        while t1 < 0.01:
            sleep(0.0001) 
            t1 = time.time() - t0
       # print("Time elapsed: ", t1) # CPU seconds elapsed (floating point)
    ndi.send_destroy(ndi_send)

    ndi.destroy()
    return 0

if __name__ == "__main__":
    sys.exit(main())

