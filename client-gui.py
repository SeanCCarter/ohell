#!/usr/bin/python
#Credit to Allan Lavell for his blackjack program,
#The basic window and card GUI are adapted from it.
#and Paul Carter for the actual ohell game


import os

import pygame
from pygame.locals import *
import string, sys, debug
from card import *
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep
pygame.font.init()
pygame.mixer.init()

debug = debug.Debug()

screen = pygame.display.set_mode((1200, 760))
clock = pygame.time.Clock()
BACKGROUND = (0,0,0)

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
#   log
#     list of information to be displayed
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
    self.log = []

  def test_gui(self):
    #Initialization
    textFont = pygame.font.Font(None, 28)
    # This sets up the background image, and its container rect
    background, backgroundRect = imageLoad("background.jpg", 0)
    exiting = False
    while not exiting:
      screen.blit(background, backgroundRect)
      exiting = checkExit()


  def displayStats(self, font):
    stats = createStatsString()
    stats = displaytext(font, stats)
    screen.blit(stats, 1030,170)

  def displayLog(self, font):
    log = ""
    for line in self.log:
      log += "\n" + line
    log = displaytext(font, log)
    screen.blit(log, 1030, 600)

  def log( self, line ):
    self.log.append(line)
    if len(self.log) > 10:
      self.log = self.log[1:]

  def createStatsString( self ):
    """ Creates the string that can be displayed
        to inform players about what's going on
        in the game.
    """
    stats = ""
    stats += '%-20.20s Bid Tricks Score' % 'Name' + '/n'
    for p in self.players:
      if p.bid >= 0:
        self.stats += '%-20.20s %3d  %3d  %5d' % (p.name, p.bid, p.numTricks, p.score) + '/n'
      else:
        self.stats += '%-20.20s      %3d  %5d' % (p.name, p.numTricks, p.score) + '/n'
    return stats

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

  def getBid( self ):
    pass

  def playGame( self ):
    #Initialization
    textFont = pygame.font.Font(None, 28)
    # This sets up the background image, and its container rect
    background, backgroundRect = imageLoad("background.jpg", 0)
    exiting = False
    while not exiting:
      command = self.readline()
      debug.echo('Read: ' +  command)
      tokens =  string.split(command)
      if tokens[0] == 'GAME_OVER':
        winnerNum = int(tokens[1])
        gameOver(self.players[winnerNum].name)
        break

      elif tokens[0] == 'NEW_PLAYER':
        self.log('Player', tokens[1], 'has joined the game')

      elif tokens[0] == 'START_GAME':
        self.players = []
        numPlayers = int(tokens[1])
        for i in range(numPlayers):
          self.players.append( Player(tokens[2*i+2], int(tokens[2*i+3])) )
        self.log( 'Game starting with players:' ),
        for player in self.players[:-1]:
          log(player.name)
        log(self.players[-1:][0].name)

      elif tokens[0] == 'NEW_HAND':
        self.cardList = CardList()
        self.numTricks = int(tokens[1])
        self.log('New hand... Tricks: ', self.numTricks, 'Dealer:', \
              self.players[int(tokens[2])].name)

      elif tokens[0] == 'DRAW':
        card = int(tokens[1])
        debug.echo( 'Dealt ' + cardToString(card))
        self.cardList.addCard(card)

      elif tokens[0] == 'DEAL_OVER':
        self.trump = int(tokens[1])
      
      elif tokens[0] == 'BID_ANNOUNCE':
        playerNum = int(tokens[1])
        bid = int(tokens[2])
        log('Player "%s" bid %s' % (self.players[playerNum].name, bid))
        self.players[playerNum].bid = bid

      elif tokens[0] == 'BID':
        self.getBid()











def gameOver( self, winner ):
  start_time = pygame.time.get_ticks()
  delay = 3*1000 #Number of seconds, times 1000, because the program returns in miliseconds
  endText = game_over_font.render(winner + " won!", 1, (0,0,0))
  while pygame.time.get_ticks() < (start_time + delay):
    display.fill(BACKGROUND)
    display.blit(endText, (470, 100))
    pygame.display.flip()
    clock.tick(60)

  class View:

    def __init__(self):
      #Initialization
      textFont = pygame.font.Font(None, 28)
      # This sets up the background image, and its container rect
      background, backgroundRect = imageLoad("background.jpg", 0)
      exiting = False


###### SYSTEM FUNCTIONS BEGIN #######
def imageLoad(name, card):
  """ Function for loading an image. Makes sure the game is compatible across multiple OS'es, as it
  uses the os.path.join function to get the full filename. It then tries to load the image,
  and raises an exception if it can't, so the user will know specifically what's going if the image loading
  does not work. 
  """

  if card:
      fullname = os.path.join("./images/cards/", name)
  else: fullname = os.path.join('./images', name)

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

def displaytext(font, sentence):
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
###### SPRITE FUNCTIONS END #######


###### MAIN GAME FUNCTIONS BEGIN #######
def checkExit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            return True
    return False




def mainLoop():
  client = Client("Test Client", )

###### MAIN GAME FUNCTIONS END #########

if __name__ == '__main__':
  if len(sys.argv) > 2:
    print 'Usage: client.py [server]'
    sys.exit(1)
  elif len(sys.argv) == 2:
    server = sys.argv[1]
  else:
    server = ''

  debug.turnOff()
  print 'Enter name: ',
  name = sys.stdin.readline()

  client = Client(name, server)
  client.test_gui()
  