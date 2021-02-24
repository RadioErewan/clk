import sys
import time
import datetime 
import numpy as np
import cv2 as cv
import NDIlib as ndi
from PIL import ImageFont, ImageDraw, ImageColor, Image
from ics import Calendar
import requests
import arrow
import textwrap

#ICS URL - ICS has to be accessible to anyone (might be read only) as we are not doing any preauth on google
icsurl = "./basic.ics"

## Font paths preconfiguration
fontpath1 = "./jb.ttf"   
fontpath2 = "./jb.ttf"  
fontpath3 = "./jb.ttf"
fontpath4 = "./jb.ttf"
fontpath5 = "./jb.ttf"
    

font1 = ImageFont.truetype(fontpath1, 115)
font2 = ImageFont.truetype(fontpath2, 65)
font3 = ImageFont.truetype(fontpath3, 30)
font4 = ImageFont.truetype(fontpath4, 25)
font5 = ImageFont.truetype(fontpath3, 40)

color1 = ImageColor.getrgb("#ff0000ff")
color2 = ImageColor.getrgb("#ffffffff")
color3 = ImageColor.getrgb("#00ff00ff")

#showing clock face
showclockface = False
#showing sides
showsides = True

#red color with alpha
b,g,r,a = 255,0,0,255
#Rundown switch
emptyrundown = True
# loading logo
logo = Image.open("./image/add.png")

#tables align
lefttable = 10
righttable = 1500
# Finding width of 
def textwidth(ffont, ftext):
    width = ffont.getsize(ftext)[0]
       
    return width
def inits():
    
    pass

def main(): 

## do we have ndi sdk? if no, there is no reason to run
    if not ndi.initialize():
        return 0
    inits()

## preconfig of ndi_send object
    send_settings = ndi.SendCreate()
    send_settings.ndi_name = 'NDI-clock'
    ndi_send = ndi.send_create(send_settings)
    video_frame = ndi.VideoFrameV2()

    currenttime = datetime.datetime.today()
    seconds = currenttime.timetuple()[5]
## Giving "alive" feedback
    print ('Initialising\t{:02d}:{:02d}:{:02d}'.format(currenttime.timetuple()[3],currenttime.timetuple()[4],currenttime.timetuple()[5]))

## loading image zegarxx.png where xx is number of seconds elapsed in current minute
    img = cv.imread('./image/zegar{:02d}.png'.format(seconds),cv.IMREAD_UNCHANGED)
    img = cv.cvtColor(img, cv.COLOR_BGRA2RGBA)
    video_frame.data = img
## we are using RGBA wideo frame (including alpha channel)
    video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_RGBA

    thetime = datetime.datetime.today()
    entrytime = thetime.timetuple()[5]
    f = open(icsurl, "r")
    icscalendar = Calendar(f.read())
    icstimeline = icscalendar.timeline

    while True:
    #peek current time
        thetime = datetime.datetime.today()     
        #if seconds differ with last load   
        if thetime.timetuple()[5] != entrytime :
            if showclockface:
            #read the clock face
                img = cv.imread('./image/zegar{:02d}.png'.format(thetime.timetuple()[5]),cv.IMREAD_UNCHANGED)
            else:
                img = np.zeros((1080,1920,4), np.uint8)
                            #convert color to rgba (with alpha)
            img = cv.cvtColor(img, cv.COLOR_BGRA2RGBA)  

            #if seconds equals 0 (new minute) reload ics 
            if thetime.timetuple()[5] == 0:
                f = open(icsurl, "r")
                icscalendar = Calendar(f.read())
                icstimeline = icscalendar.timeline
        # printing current minute as a way of showing we are alive (happens once a minute)
                print ('Still alive\t{:02d}:{:02d}:{:02d}'.format(thetime.timetuple()[3],thetime.timetuple()[4],thetime.timetuple()[5]))
        #some bitmap procesing using PIL
            img_pil = Image.fromarray(img)
        #centering time on the image
            text = '{:02d}:{:02d}:{:02d}'.format(thetime.timetuple()[3],thetime.timetuple()[4],thetime.timetuple()[5])
            x = int((1920-textwidth(font1,text))/2)
            draw = ImageDraw.Draw(img_pil)
            draw.text((x, 400),  text, font = font1, fill = color1)
            #select events happening now
            events = icstimeline.now()
            eventlist=list(events)
            if len(eventlist) >0 :
                emptyrundown = False
            else:
                emptyrundown = True
        #paste logo

            if showsides:

            #if there is somethnig happening now
                if len(eventlist) >0 :
                #rundown is not empty
                    emptyrundown = False
                #name of event in center clock    
                    draw.text((x, 540),  textwrap.shorten(eventlist[0].name.upper(), width=22, placeholder="..."), font = font5, fill = color1)   
                #current event duration
                    eventduration = eventlist[0].end.timestamp - eventlist[0].begin.timestamp
                    eventarrow = arrow.get(eventduration)
                #Labeling right table    
                    draw.text((righttable, 50),  "Duration:".upper(), font = font4, fill = color2)  
                    text = '{:02d}:{:02d}:{:02d}'.format(eventarrow.time().hour,eventarrow.time().minute,eventarrow.time().second)
                    draw.text((righttable, 100),  text, font = font3, fill = color1) 
                    nowarrow = arrow.utcnow()
                    remainingarrow = arrow.get(eventlist[0].end.timestamp - nowarrow.timestamp)
                    eventelapsed = nowarrow.timestamp - eventlist[0].begin.timestamp 

                    remainingpercent = int((eventelapsed/eventduration)*100)
                    text = '{:02d}:{:02d}:{:02d}'.format(remainingarrow.time().hour,remainingarrow.time().minute,remainingarrow.time().second)
                #draw remaining time in center
                    draw.text((x, 580),  text, font = font1, fill = color1)
                #draw remaining time on right side
                    draw.text((righttable, 150),  "Remaining:".upper(), font = font4, fill = color2)  
                    draw.text((righttable, 200),  text, font = font3, fill = color1)  

                #draw logo
                    third_img = Image.open("./image/pc{:02d}.png".format(remainingpercent)) 
                    img_pil.paste(third_img, (0,0), third_img)

                else :
                    #rundown is empty
                    emptyrundown = True
    #Listing upcomming events      
                arrw =  arrow.utcnow()    
                arrwtomorrow = arrw.shift(days=+1)
                events = icstimeline.included(arrw, arrwtomorrow)
                eventlist=list(events)


                #We show green countdown   
            if len(eventlist)>0 :
                if emptyrundown :
                    nowarrow = arrow.utcnow()
                    remainingarrow = arrow.get(eventlist[0].begin.timestamp - nowarrow.timestamp)
                    text = '{:02d}:{:02d}:{:02d}'.format(remainingarrow.time().hour,remainingarrow.time().minute,remainingarrow.time().second)
                #draw remaining time in center
                    draw.text((x, 540),  textwrap.shorten(eventlist[0].name.upper(), width=22, placeholder="..."), font = font5, fill = color3)   

                    draw.text((x, 580),  text, font = font1, fill = color3)     
                else:
                                    #name of event in center clock    
                    draw.text((x, 540),  textwrap.shorten(eventlist[0].name.upper(), width=22, placeholder="..."), font = font5, fill = color1)   
                #current event duration
                    eventduration = eventlist[0].end.timestamp - eventlist[0].begin.timestamp
                    eventarrow = arrow.get(eventduration)            
 
            
#cast pil image back to ndi image buffer                
            img = np.array(img_pil)
#send it
            video_frame.data = img
            video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_RGBA            
#record second of processing
            thetime = datetime.datetime.today()
            entrytime = thetime.timetuple()[5]
#send video frame
            ndi.send_send_video_v2(ndi_send, video_frame)

        if cv.waitKey(20) & 0xFF == 27:
            break

    ndi.send_destroy(ndi_send)

    ndi.destroy()

    return 0

if __name__ == "__main__":
    sys.exit(main())
