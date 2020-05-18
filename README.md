# Inky Nth Tweets

This app displays tweets on an e-ink display attached to a Raspberry Pi.

I made this to start to learn how to work with Python and the Inky wHAT display.

## Pre-requisites

### Hardware

- Raspberry Pi (running Raspbian Buster)
- Pimoroni Inky wHAT e-ink display

### Software

- Python 3
- [Inky Python library](https://github.com/pimoroni/inky)
- [Pillow Python library](https://pillow.readthedocs.io/en/stable/index.html)
- [Twitter Python library](https://python-twitter.readthedocs.io/en/latest/)

### Other stuff

- Access to the [Twitter Developer API](https://developer.twitter.com)

## Set up

1. Make a copy of `keys-template.py` and rename it to `keys.py`
2. Inside `keys.py` change the values to match your Twitter API keys

##  Usage

Run the code using 

```python
python inky-twitter.py
```

You can pass the following arguments to `inky-twitter.py`

- `--username`, `-u` - enter the username of the Twitter account to look for (defaults to @unsplash)
- `—nth`, `-n` - get the nth tweet from a user's feed (defaults to 1)
	- `--test`, `-t` - outputs a local PNG file `debug.png` instead of updating the Inky wHAT (defaults to False)
- `--colour`, `-c` - sets the colour of the display (defaults to yellow)
- `--help`, `-h` - runs the help

### Examples

```python
# Output the first tweet from @unsplash to the Inky wHAT display
python inky-twitter.py -u unsplash -n 1 
```

```python
# Output the 5th tweet from @twitter locally to a PNG
python inky-twitter.py -u twitter -n 5 -t True
```

## Screenshots

The code outputs two styles: text only and media only.

### Text only output

Your display should update to look something like this:

![](https://github.com/johnpeart/inky-nth-tweet/blob/master/screenshot-text.jpg)

### Media only output

Your display should update to look something like this:

![](https://github.com/johnpeart/inky-nth-tweet/blob/master/screenshot-media.jpg)

## Things to do

1. This will run just once; you'd need to set up a way for this to run on its own, probably with something like a cron job.

## Credits

Inspired by Adam Bowie's [Twitter feeds display](https://www.adambowie.com/blog/2019/09/news-twitter-feeds-and-inky-what-e-ink-display/).

Fonts are open sourced and from [iA Writer](https://github.com/iaolo/iA-Fonts).

Retweet, favourite and reply icons made by [Dave Gandy](https://www.flaticon.com/authors/dave-gandy")