#!/usr/bin/python
#Credit to Allan Lavell for his blackjack program,
#and Paul Carter for the actual ohell game
#The basic window and card GUI are adapted from it.

import os
import sys

import pygame
from pygame.locals import *
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((800, 480))
clock = pygame.time.Clock()

#
# Oh Hell Client class
#
# Attributes:
#   name
#     name of player
#
#   buffer
#     buffer of messages from server
#
#   socket
#     socket for connection to server
#
#   players
#     list of players (Player objects)
#
#   cardList
#     list of cards held by player
#
#   trump
#     trump for hand
#
#   numTricks
#     number of tricks for hand
#
class Client:

  #
  # constructor
  # Parameters:
  #   name   - name of player
  #   server - host name (or IP) of game server
  #   port   - port to connect to
  #
  def __init__( self, name, server = '', port = 7000 ):
    self.name = name
    self.buffer = []
    self.server = server
    self.port = port

  def play( self ):
    self.socket = socket(AF_INET, SOCK_STREAM)

    try:
      self.socket.connect((self.server, self.port))
      self.send( 'LOGIN ' + name )
      reply = self.readline()
      if reply == 'OK':
        debug.echo('Logged in as ' + name)
        self.playGame()
      else:
        debug.echo('Login error! Reply: ' + reply)
    except:
      print 'Caught exception'
      error = sys.exc_info()
      print error[0], error[1]
    
    self.socket.shutdown(2)
    self.socket.close()

###### SYSTEM FUNCTIONS BEGIN #######
def imageLoad(name, card):
  """ Function for loading an image. Makes sure the game is compatible across multiple OS'es, as it
  uses the os.path.join function to get he full filename. It then tries to load the image,
  and raises an exception if it can't, so the user will know specifically what's going if the image loading
  does not work. """

  if card:
      fullname = os.path.join("images/cards/", name)
  else: fullname = os.path.join('images', name)

  try:
      image = pygame.image.load(fullname)
  except pygame.error, message:
    print 'Cannot load image:', name
    raise SystemExit, message
  image = image.convert()

    return image, image.get_rect()

def soundLoad(name):
    """ Same idea as the imageLoad function. """

    fullName = os.path.join('sounds', name)
    try: sound = pygame.mixer.Sound(fullName)
    except pygame.error, message:
        print 'Cannot load sound:', name
        raise SystemExit, message
    return sound

def display(font, sentence):
    """ Displays text at the bottom of the screen, informing the player of what is going on."""

    displayFont = pygame.font.Font.render(font, sentence, 1, (255,255,255), (0,0,0))
    return displayFont

def playClick():
    clickSound = soundLoad("click2.wav")
    clickSound.play()
###### SYSTEM FUNCTIONS END #######


##### SPRITE FUNCTIONS BEGIN ######
class cardSprite(pygame.sprite.Sprite):
    """ Sprite that displays a specific card. """

    def __init__(self, card, position):
        pygame.sprite.Sprite.__init__(self)
        cardImage = card + ".png"
        self.image, self.rect = imageLoad(cardImage, 1)
        self.position = position
    def update(self):
        self.rect.center = self.position

