#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ####################
## IMPORT MODULES ##
####################
import sys # This module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter. It is always available.
import datetime # The datetime module supplies classes for manipulating dates and times.
import argparse # Enables you to pass arguments through terminal
import keys # This module stores API credentials for use with the Twitter Developer API
import twitter # This module handles interactions with the Twitter Developer API
from PIL import Image, ImageFont, ImageDraw # This module handles creation of images and text, which are sent to the display
import requests
from StringIO import StringIO
from inky import InkyWHAT # This module makes the e-ink display work and renders the image

# Command line arguments to set display type and colour, and enter your name

parser = argparse.ArgumentParser()
parser.add_argument("--test", "-t", type=bool, choices=[True], help="Set to 'true' to output to local PNG instead of to the display")
parser.add_argument("--username", "-u", type=str, help="Your Twitter handle without the @ symbol", default="unsplash")
parser.add_argument("--nth", "-n", nargs="?", type=int, help="Get the nth latest tweet", default=1)
parser.add_argument("--colour", "-c", nargs="?", type=str, help="Set colour of the display", default="yellow")
args = parser.parse_args()

#########################################
## SET VARIABLES FROM THE COMMAND LINE ##
#########################################

twitterUsername = args.username
twitterUsernameString = "@{}".format(twitterUsername)
nthTweet = args.nth - 1 # API returns zero-based numbers, so the latest tweet to the end user would be n = 1 but should really be 0.

test = args.test

inkyColour = args.colour

##################################################
## IMPORT THE TWITTER DEVELOPER API CREDENTIALS ##
##################################################
# This sets your Twitter Developer API credentials.
# It imports the keys from 'keys.py', which is not included in the repository.
# The keys are in this format:
# 
# twitter = {
#     "consumer_key": "YOUR KEY HERE",
#     "consumer_secret": "YOUR KEY HERE",
#     "access_token_key": "YOUR KEY HERE",
#     "access_token_secret": "YOUR KEY HERE"
# }

api = twitter.Api(
    consumer_key = keys.twitter["consumer_key"],
    consumer_secret = keys.twitter["consumer_secret"],
    access_token_key = keys.twitter["access_token_key"],
    access_token_secret = keys.twitter["access_token_secret"],
    tweet_mode= 'extended' # Include this or tweets will be truncated
)

##################################
## SET UP THE INKY WHAT DISPLAY ##
##################################
# Set the display type and colour
# InkyPHAT is for the smaller display and InkyWHAT is for the larger display.
# Accepts arguments 'red', 'yellow' or 'black', based on the display you have. 
# (You can only use 'red' with the red display, and 'yellow' with the yellow; but 'black' works with either).

inky = InkyWHAT(inkyColour)

##########################
## SET GLOBAL VARIABLES ##
##########################

if test == True:
    yellow = "#9B870C"
    red = "#9B870C"
    white = "#ffffff"
    black = "#000000"
    displayHeight = 300
    displayWidth = 400
else:
    yellow = inky.YELLOW
    red = inky.RED
    white = inky.WHITE
    black = inky.BLACK
    displayHeight = inky.HEIGHT
    displayWidth = inky.WIDTH

now = datetime.datetime.now()

tweetFontSize = 16
accountFontSize = 20
statsFontSize = 24

##########################
## IMPORT FONTS FOR USE ##
##########################
# ImageFont.truetype accepts two arguments, (1, 2):
# 1. "path/to/font" - where path/to/font is the path to the .ttf file
# 2. font size - as an integer

tweetFont = ImageFont.truetype("fonts/Regular.ttf", tweetFontSize)
accountFont = ImageFont.truetype("fonts/Bold.ttf", accountFontSize)
statsFont = ImageFont.truetype("fonts/Bold.ttf", statsFontSize)

statsFontWidth, statsFontHeight = statsFont.getsize("ABCD ")

bannerHeight = 40
bannerBorderThickness = 1
bannerPadding = 5
resizedIcon = bannerHeight - (4 * bannerPadding)
iconVHeight = displayHeight - (bannerHeight / 2) - (resizedIcon / 2)
statsVHeight = displayHeight - (bannerHeight / 2) - (statsFontHeight * 2/3)

#################
## REFLOW TEXT ##
#################
# This function reflows text across multiple lines.
# It is adapted from the Pimoroni guidance for the Inky wHAT.

def reflow_text(textToReflow, width, font):
    words = textToReflow.split(" ")
    reflowed = ''
    line_length = 0

    for i in range(len(words)):
        word = words[i] + " "
        word_length = font.getsize(word)[0]
        line_length += word_length

        if line_length < width:
            reflowed += word
        else:
            line_length = word_length
            reflowed = reflowed[:-1] + "\n" + word

    return reflowed

###########################
## HUMAN READABLE NUMERS ##
###########################
# This function truncates large numbers with the 'K', 'M', 'B' and 'T' format
# representing thousands, millions, billions and trillions

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

####################
## GET THE TWEETS ##
####################
# For each account defined in 'accounts.py', this function gets the latest tweet and prepares it for rendering.

def displayTweet(handle):
    statuses = api.GetUserTimeline(screen_name=handle, exclude_replies=True, include_rts=False)
    return statuses[nthTweet].full_text, statuses[nthTweet].media, statuses[nthTweet].retweet_count, statuses[nthTweet].favorite_count

if __name__ == "__main__":
    tweet = displayTweet(twitterUsername)
    status = tweet[0]
    media = tweet[1]
    if media != None:
        if media[0].type == "photo":
            mediaURL = media[0].media_url
        else:
            media = None
    retweets = human_format(tweet[2])
    likes = human_format(tweet[3])
    print('Status: ', status, 'Media: ', media, 'Retweets: ', retweets, 'Likes: ', likes)

########################
## RENDER THE CONTENT ##
########################
# These functions:
# 1. Check to see if the tweet is text only or a media tweet
# 2. If the tweet has media is a photo, generates a full screen image of the video and discards the text
#    OR
#    If the tweet does not have media, generates a full screen stylised image of the tweet's text
# 3. Creates a bar at the bottom of the screen showing the number of retweets and favourites/likes

if media != None:
    response = requests.get(mediaURL)
    img = Image.open(StringIO(response.content))
    mediaWidth, mediaHeight = img.size
    if mediaWidth >= mediaHeight:
        mediaHeightNew = displayHeight
        mediaWidthNew = int((float(mediaWidth) / float(mediaHeight)) * mediaHeightNew)
        mediaWidthCropped = displayWidth
        img = img.resize((mediaWidthNew, mediaHeightNew), resample=Image.NEAREST)
        x0 = (mediaWidthNew - mediaWidthCropped) / 2
        x1 = x0 + mediaWidthCropped
        y0 = 0
        y1 = mediaHeightNew
    elif mediaHeight > mediaWidth:
        mediaWidthNew = displayWidth
        mediaHeightNew = int((float(mediaHeight) / float(mediaWidth)) * mediaWidthNew)
        mediaHeightCropped = displayHeight
        img = img.resize((mediaWidthNew, mediaHeightNew), resample=Image.NEAREST)
        x0 = 0
        x1 = mediaWidthNew
        y0 = (mediaHeightNew - mediaHeightCropped) / 2
        y1 = y0 + mediaHeightCropped
    img = img.crop((x0, y0, x1, y1))
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)
    img = img.convert("RGB").quantize(palette=pal_img)
else:
    img = Image.new("P", (displayWidth, displayHeight))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (displayWidth, displayHeight)], fill = white, outline=None)
    reflowed_tweet = reflow_text(tweet[0], displayWidth, tweetFont)
    draw.text((0, 0), reflowed_tweet, black, tweetFont)
    tweetTextWidth, tweetTextHeight = accountFont.getsize(reflowed_tweet)
    pal_img = Image.new("P", (1, 1))
    pal_img.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)

# This section renders the bar at the bottom of the screen

likeImage = Image.open('images/likes.png')
rtImage = Image.open('images/rt.png')
likeImage = likeImage.resize((resizedIcon, resizedIcon), resample=Image.NEAREST).convert("RGB").quantize(palette=pal_img)
rtImage = rtImage.resize((resizedIcon, resizedIcon), resample=Image.NEAREST).convert("RGB").quantize(palette=pal_img)

ImageDraw.Draw(img).rectangle([(0, displayHeight - bannerHeight), (displayWidth, displayHeight)], fill = white, outline=None)
ImageDraw.Draw(img).rectangle([(0, displayHeight - bannerHeight), (displayWidth, displayHeight - (bannerHeight - bannerBorderThickness))], fill = black, outline=None)

img.paste(rtImage, (int(bannerPadding), iconVHeight))
ImageDraw.Draw(img).text((int(bannerPadding + (resizedIcon * 1.25)), statsVHeight), str(retweets), yellow, statsFont)

img.paste(likeImage, (int((displayWidth * 1/3) + bannerPadding), iconVHeight))
ImageDraw.Draw(img).text(((displayWidth * 1/3) + bannerPadding + (resizedIcon * 1.25), statsVHeight), str(likes), yellow, statsFont)

accountFontWidth, accountFontHeight = accountFont.getsize(twitterUsernameString)
accountVHeight = displayHeight - (bannerHeight / 2) - (accountFontHeight * 0.5)

ImageDraw.Draw(img).text(((displayWidth - accountFontWidth - bannerPadding), accountVHeight), twitterUsernameString, yellow, accountFont)


########################
## FINALISE THE IMAGE ##
########################
# Set a PIL image, numpy array or list to Inky's internal buffer. The image dimensions should match the dimensions of the pHAT or wHAT you're using.
# You should use PIL to create an image. PIL provides an ImageDraw module which allow you to draw text, lines and shapes over your image. 
# See: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html

inky.set_image(img)

###############################
## SET DISPLAY BORDER COLOUR ##
###############################
# .set_border(colour) sets the colour at the edge of the display
# colour should be one of 'inky.RED', 'inky.YELLOW', 'inky.WHITE' or 'inky.BLACK' with available colours depending on your display type.

inky.set_border(white)

########################
## UPDATE THE DISPLAY ##
########################
# Once you've prepared and set your image, and chosen a border colour, you can update your e-ink display with .show()

if test == True:
    img.save("debug.png")
else:
    inky.show()