##############################################################
# Name: Brian Davis and Nick Belbas
# Date: 4/22/19
# Description: This code monitors the level of ambient sound and tweets
#    every time a new "record" is set
##############################################################
import time
import spidev #library to read SPI from ADC chip
import datetime
import random
import os    #library to run shell commands in python code
from Tkinter import *
from twython import Twython  #library to send tweets using python code

from auth import (consumer_key,consumer_secret,access_token,access_token_secret)
#import keys and api tokens from auth.py file

twitter=Twython(consumer_key,consumer_secret,access_token,access_token_secret)
#create a Twython instance with the above mentioned api keys and tokens

spi_ch = 0
lastHighest=0
huskyCheers=["Dawgs Up!","Go Huskies!"] #initialize a list of cheers to append at the end of tweet
otherTeam="otherBois"
# Enable SPI
spi = spidev.SpiDev(0, spi_ch)
spi.max_speed_hz = 1200000 #set the SPI refresh rate

def tweetit():
    window.destroy()
    print "Tweeting..."
    print "\n"
    cheer=huskyCheers[random.randint(0,1)] #choose a random cheer
    currentDT = datetime.datetime.now() #get current date/time
    message = "*THIS IS AN AUTOMATED TWEET* \nA new crowd noise level was set tonight at HBU Huskies Football stadium during the game against {} at {} on {}! {}".format(otherTeam,currentDT.strftime("%I:%M %p"),currentDT.strftime("%a, %b %d, %Y"),cheer)
    print "taking photo..."
    os.system('fswebcam -r 1280x720 --no-banner image.jpg') #run terminal command to save photo from webcam
    time.sleep(4)
    print "photo taken, attaching to tweet"
    image = open('image.jpg','rb')
    response = twitter.upload_media(media=image) #upload image to twitter server
    media_id = [response['media_id']]
    print "image uploaded to twitter server, tweeting message"
    twitter.update_status(status=message,media_ids=media_id) #attach image to tweet
    print "tweet successfully sent, deleting image"
    os.system('sudo rm image.jpg') #delete image once completed
    print "image deleted, checking files"
    checkFiles = os.popen('ls').read()
    print(checkFiles)

class GUI(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master

    def setupGUI(self):
        l1 = Label(self.master, text = "Send Tweet?") #popup gui to prompt user to finalize tweet
        l1.grid(row = 0, column = 0, columnspan = 2, sticky = E+W)
        
        b1 = Button(self.master, text = "YES", bg = 'green', fg = 'black', width = 50, height = 5, command = tweetit)
        b1.grid(row = 1, column = 0)
        
        b2 = Button(self.master, text = "NO", bg = 'red', fg = 'white', width = 50, height = 5, command = window.destroy)
        b2.grid(row = 1, column = 1)

        #Creates menu commands for the window
        menu = Menu(window)
        window.config(menu = menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Exit", command=window.destroy)
        helpmenu = Menu(menu)
        menu.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About")

        #Extra info
        window.title("Twitter Bot Boi")
        window.configure(background = 'grey')

window = Tk()    #creates graphical window
t = GUI(window)
t.setupGUI()


def read_adc(adc_ch, vref = 3.3):
    ########################################
    # read_adc method provided by Sparkfun
    ########################################
    # Make sure ADC channel is 0 or 1
    if adc_ch != 0:
        adc_ch = 1

    # Construct SPI message
    #  First bit (Start): Logic high (1)
    #  Second bit (SGL/DIFF): 1 to select single mode
    #  Third bit (ODD/SIGN): Select channel (0 or 1)
    #  Fourth bit (MSFB): 0 for LSB first
    #  Next 12 bits: 0 (don't care)
    msg = 0b11
    msg = ((msg << 1) + adc_ch) << 5
    msg = [msg, 0b00000000]
    reply = spi.xfer2(msg)

    # Construct single integer out of the reply (2 bytes)
    adc = 0
    for n in reply:
        adc = (adc << 8) + n

    # Last bit (0) is not part of ADC value, shift to remove it
    adc = adc >> 1

    # Calculate voltage form ADC value
    voltage = (vref * adc) / 1024

    return voltage


# Report the channel 0 and channel 1 voltages to the terminal
otherTeam=str(raw_input("Please enter opposing team:"))

file = open("lasthighest.txt","r") #log next highest sound level from sensor to txt file
lastHighest=float(file.read())
file.close()
print "Last Highest: {}".format(lastHighest)
while True:
    adc_0 = read_adc(0)
    print("Ch 0:", round(adc_0, 2), "V")
    time.sleep(0.2)
    if(round(adc_0,2)>lastHighest): #if the latest value from the sensor is higher then the latest entry from the txt file,
        personInput = str(raw_input("New High Value detected: Save value {} and save tweet?".format(round(adc_0,2))))
        personInput=personInput.lower()
        if(personInput=="yes"): #if person types "yes" to save value, GUI pops up to ask if they want to tweet this data
            print "New High Value: {}".format(round(adc_0,2))
            file = open("lasthighest.txt","w")
            file.write(str(round(adc_0,2)))
            lastHighest=round(adc_0,2)
            file.close()
            window.mainloop()   #GUI not actually shown on the desktop until this statement

