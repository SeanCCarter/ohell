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
import inputbox
pygame.font.init()
pygame.mixer.init()

debug = debug.Debug()

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
    self.screen = pygame.display.set_mode((1250, 760))
    self.background = imageLoad("background.jpg", 0)
    self.clock = pygame.time.Clock()
    self.cardImages = []
    for suit in ['c', 'd', 'h', 's']:
      for card in [str(i) for i in range(2, 11)] + ['j', 'q', 'k', 'a']:
        self.cardImages.append(imageLoad(suit+card+'.png', True))
    self.handImage = imageLoad("hand.png", False)
    self.handImage.set_colorkey((0,0,0))

    self.players = [Player("Sean", 0)]
    self.playerIndex = 0

    self.trump = -1
    self.cardList = CardList()
    for card in [1,2,3,4,7,8,10]:
      self.cardList.addCard(card)
    self.playedCards = [-1]*10
    exiting = False
    while not exiting:
      self.gameOver("Sean")
      exiting = True


  def play( self ):
    self.socket = socket(AF_INET, SOCK_STREAM)
    #try:
    self.socket.connect((self.server, self.port))
    self.send( 'LOGIN ' + name )
    reply = self.readline()
    if reply == 'OK':
      debug.echo('Logged in as ' + name)
      self.playGame()
    else:
      debug.echo('Login error! Reply: ' + reply)
    # except:
    #   print 'Caught exception'
    #   error = sys.exc_info()
    #   print error[0], error[1]
    
    self.socket.shutdown(2)
    self.socket.close()

    #
  # start to play game
  #              
  def playGame( self ):
    # This sets up all necessary images
    self.screen = pygame.display.set_mode((1250, 760))
    self.background = imageLoad("background.jpg", 0)
    self.clock = pygame.time.Clock()
    self.cardImages = []
    for suit in ['c', 'd', 'h', 's']:
      for card in [str(i) for i in range(2, 11)] + ['j', 'q', 'k', 'a']:
        self.cardImages.append(imageLoad(suit+card+'.png', True))
    self.handImage = imageLoad("hand.png", False)
    self.handImage.set_colorkey((0,0,0))

    self.trump = -1
    self.cardList = CardList()
    self.playedCards = []
    self.players = [Player(self.name, 0)]
    self.playerIndex = 0

    self.updateDisplay()
    exiting = False
    while not exiting:
      command = self.readline()
      debug.echo('Read: ' +  command)
      tokens =  string.split(command)
      if tokens[0] == 'GAME_OVER':
        winnerNum = int(tokens[1])
        self.addToLog('Player "%s" won!' % self.players[winnerNum].name)
        self.gameOver(self.players[winnerNum].name)
        exiting = True

      elif tokens[0] == 'NEW_PLAYER':
        self.addToLog(('Player '+tokens[1]+' has joined the game'))

      elif tokens[0] == 'START_GAME':
        print "Starting game."
        self.players = []
        numPlayers = int(tokens[1])
        for i in range(numPlayers):
          self.players.append( Player(tokens[2*i+2], int(tokens[2*i+3])) )
          if tokens[2*i+2] == self.name:
            #Assumes no two players have the same name
            self.playerIndex = i
        self.addToLog( 'Game starting with players:' ),
        for player in self.players[:-1]:
          self.addToLog(player.name)
        self.addToLog(self.players[-1:][0].name)

      elif tokens[0] == 'NEW_HAND':
        self.cardList = CardList()
        self.numTricks = int(tokens[1])
        self.playedCards = [-1 for i in xrange(self.numTricks)]
        self.addToLog('New hand... Tricks: '+ str(self.numTricks))
        self.addToLog( 'Dealer: '+ self.players[int(tokens[2])].name)

      elif tokens[0] == 'DRAW':
        card = int(tokens[1])
        debug.echo( 'Dealt ' + cardToString(card))
        self.cardList.addCard(card)

      elif tokens[0] == 'DEAL_OVER':
        self.trump = int(tokens[1])
      
      elif tokens[0] == 'BID_ANNOUNCE':
        playerNum = int(tokens[1])
        bid = int(tokens[2])
        self.addToLog('Player "%s" bid %s' % (self.players[playerNum].name, bid))
        self.players[playerNum].bid = bid

      elif tokens[0] == 'BID':
        self.getBid()

      elif tokens[0] == 'CARD_PLAYED':
        player = int(tokens[1])
        card = int(tokens[2])
        self.addToLog('"%s" played %s' %(self.players[player].name + " ", 
                                          cardToString(card)))
        self.playedCards[player] = card

      elif tokens[0] == 'GET_CARD':
        print "\a"
        exiting = self.playCard()

      elif tokens[0] == 'TRICK_WINNER':
        player = int(tokens[1])
        self.addToLog('"%s" won trick' % self.players[player].name)
        self.updateDisplay()
        self.players[player].wonTrick()
        self.playedCards = [-1 for i in xrange(len(self.players))]
        pygame.time.delay(400)

      elif tokens[0] == 'END_HAND':
        for i in range(len(self.players)):
          player = self.players[i]
          delta = int(tokens[i+1])
          if delta > 0:
            self.addToLog(('Player "%s"' % player.name)+(' made %d points' % delta))
          elif delta < 0:
            self.addToLog(('Player "%s"' % player.name)+(' went down %d points' % (-delta)))
          else:
            self.addToLog(('Player "%s"' % player.name)+ ' went over')
          player.score = player.score + delta
        for p in self.players:
          p.reset()

      else:
        print 'Unknown command: ', command

      for event in pygame.event.get():
        exiting = checkExit(event)
        if exiting:
          print "Exiting set to true."
      self.updateDisplay()

  #
  # plays a card and checks exit, at the same time
  # returns card index, exiting
  #
  def playCard( self ):
    self.updateDisplay()

    #
    # get valid card choice from user
    #
    fontobject = pygame.font.Font(None,30)
    cards = [i for i in range(52) if self.cardList.hasCard(i)]
    cardValue = -1
    cardSuit = -1
    done = 0
    while not done:
      for event in pygame.event.get():
        if checkExit(event):
          return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
          for i, cardrect in enumerate(self.cardRects):
            coords = pygame.mouse.get_pos()
            if cardrect.collidepoint(coords[0],coords[1]):
              card = cards[i]
              done = 1
      self.screen.blit(fontobject.render("Play Card", 1, (0,0,255)), (440,390))
      self.updateDisplay()
    #
    # send choice to server
    #
    self.send('PLAY_CARD %d' % card)
    response = self.readline()
    if response == 'OK':
      self.cardList.removeCard(card)
    else:
      self.addToLog('Illegal card, try again')
      self.updateDisplay()
    return False

  def getBid( self):
    coordinates = {"x":300, "y":300, "width": 400, "height":60}
    while 1:
      self.addToLog('Enter bid: ')
      try:
        bid = int(inputbox.ask(self.screen, "What is your bid?", coordinates))
      except ValueError:
        bid = -1

      if bid >= 0 and bid <= self.numTricks:
        self.send('BID %d' % bid)
        response = self.readline()
        if response == 'OK':
          break
        elif string.split(response)[0] == 'BADBID':
          self.addToLog('Illegal bid, try again')
          break
        else:
          self.addToLog('Illegal bid, try again')
      else:
        self.addToLog('Illegal bid, try again')

  def addToLog( self, line ):
    self.log.append(line)
    if len(self.log) > 15:
      self.log = self.log[1:]

  def updateDisplay( self ):
    self.screen.blit(self.background, (0,0))
    self.displayHand(self.screen)
    self.displayPlayedCards(self.screen)
    self.displayPlayers(self.screen)
    self.displayPlayers(self.screen)
    self.displayLog(self.screen)
    self.displayStats(self.screen)
    pygame.display.flip()
    self.clock.tick(40)

  #
  # display cards in hand
  #
  def displayHand( self, screen ):
    if self.trump >= 0:
      fontobject = pygame.font.Font(None,30)
      screen.blit(fontobject.render("Trump:", 1, (255,255,255)), (30,24))
      screen.blit(self.cardImages[self.trump], (30,50))
    
    self.cardRects = []
    if True:
      cards = [i for i in range(52) if self.cardList.hasCard(i)]
      for i, card in enumerate(cards):
        position = (90 + 80/2*(10-len(cards)) + 80*i, 505)
        self.cardRects.append(self.cardImages[card].get_rect(left = 90 + 80/2*(10-len(cards)) + 80*i, top=505))
        screen.blit(self.cardImages[card], position)

  def displayPlayedCards( self, screen ):
    #This assumes that there will be no more than 5
    #people playing
    layout1 = [(450,390)]
    layout2 = [(450,390),(450, 185)]
    layout3 = [(450,390),(300,230),(600,230)]
    layout4 = [(450,390),(300,265),(450,145),(600,265)]
    layout5 = [(450,390),(300,265),(385,130),(520,130),(600,265)]
    layouts = [layout1,layout2,layout3,layout4,layout5]
    if len(self.players)>5 or len(self.players)<1:
      raise Exception('Client Gui cann only handle 1-5 players.')
    else:
      layout = layouts[len(self.players)-1]
      for i, card in enumerate(self.playedCards):
        if card >= 0:
          coords = layout[i - self.playerIndex]
          screen.blit(self.cardImages[card], coords)

  def displayPlayers( self, screen):
    fontobject = pygame.font.Font(None,30)
    layout1 = [(450,390)]
    layout2 = [(450,390),(385, 55)]
    layout3 = [(450,390),(50,240),(700,240)]
    layout4 = [(450,390),(50,240),(385, 27),(700,240)]
    layout5 = [(450,390),(50,280),(160,85),(620,85),(700,280)]
    layouts = [layout1,layout2,layout3,layout4,layout5]
    layout = layouts[len(self.players)-1]
    for i, player in enumerate(self.players):
      if i - self.playerIndex != 0:
        coords = layout[i - self.playerIndex]
        screen.blit(fontobject.render(player.name, 1, (0,0,0)), (coords[0]+20,coords[1]-25))
        screen.blit(self.handImage, coords)

  def displayStats(self, screen):
    fontobject = pygame.font.Font(None,22)
    top = '%-20.20s Bid Tricks Score' % 'Name'
    line = "-"*46
    screen.blit(fontobject.render(top, 1, (255,255,255)), (1000,100))
    screen.blit(fontobject.render(line, 1, (255,255,255)), (1000,110))
    for i, p in enumerate(self.players):
      if p.bid >= 0:
        #Have to blit individually, as letter width is inconsistant
        screen.blit(fontobject.render(p.name, 1, (255,255,255)), (1000,130 + i*17))
        screen.blit(fontobject.render(str(p.bid), 1, (255,255,255)), (1115,130 + i*17))
        screen.blit(fontobject.render(str(p.numTricks), 1, (255,255,255)), (1155,130 + i*17))
        screen.blit(fontobject.render(str(p.score), 1, (255,255,255)), (1195,130 + i*17))
      else:
        screen.blit(fontobject.render(p.name, 1, (255,255,255)), (1000,130 + i*17))
        screen.blit(fontobject.render(str(p.numTricks), 1, (255,255,255)), (1155,130 + i*17))
        screen.blit(fontobject.render(str(p.score), 1, (255,255,255)), (1195,130 + i*17))
    screen.blit(fontobject.render(line, 1, (255,255,255)), (1000,145 + i*17))

  def displayLog(self, screen):
    fontobject = pygame.font.Font(None,22)
    screen.blit(fontobject.render("Game Info:", 1, (255,255,255)), (1000,350))
    screen.blit(fontobject.render("-"*46, 1, (255,255,255)), (1000,360))
    for i, line in enumerate(self.log):
      screen.blit(fontobject.render(line, 1, (255,255,255)), (1000,375 + i*17))

  def gameOver( self, winner ):
    fontobject = pygame.font.Font(None,126)
    endText = fontobject.render(winner + " wins!", 1, (0,0,0))
    exiting = False
    self.updateDisplay()
    self.screen.blit(endText, (230, 290))
    pygame.display.flip()
    while not exiting:
      for event in pygame.event.get():
        exiting = checkExit(event)

  #
  # send message to server
  # Parameters:
  #   msg - message to send (\n is added automatically)
  #
  def send( self, msg ):
    self.socket.send( msg + '\n')

  #
  # read a line from server
  # Return value:
  #   line (e.g. message) from server
  #
  def readline( self ):
    if len(self.buffer) > 0:
      line = self.buffer[0]
      del self.buffer[0]
      if line != '':
        return line
      else:
        return self.readline()
    else:
      input = self.socket.recv(1024)
      if input == '':
        return None
      #
      # The spit below will put a '' at end of list
      # if input ends with '\n', which it almost certainly does!
      #
      self.buffer = string.split( input, '\n')
      debug.echo('buffer =' + str(self.buffer))
      if len(self.buffer) == 0:
        return None
      else:
        return self.readline()

  #
  # log off of server
  #
  def logout( self ):
    self.send( 'LOGOUT' )
    reply = self.readline()
    if reply == 'OK':
      self.addToLog('Logged out')
    else:
      self.addToLog('Login error!')


class Player:

  #
  # constructor
  # Parameters:
  #    name  - name of player
  #    score - starting score of player
  #
  def __init__(self, name, score):
    self.name = name
    self.score = score
    self.bid = -1
    self.numTricks = 0

  #
  # called to inform player they won trick
  #
  def wonTrick( self ):
    self.numTricks = self.numTricks + 1

  #
  # reset player for new hand of cards
  #
  def reset( self ):
    self.bid = -1
    self.numTricks = 0





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
  return image
###### SYSTEM FUNCTIONS END #######





###### MAIN GAME FUNCTIONS BEGIN #######
def checkExit(event):
  if event.type == pygame.QUIT:
    return True
  elif event.type == KEYDOWN and event.key == K_ESCAPE:
    return True
  else:
    return False
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
  name = sys.stdin.readline().strip()

  client = Client(name, server)
  client.play()