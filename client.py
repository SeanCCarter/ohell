#!/usr/bin/python

import string, sys, debug
from card import *
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep

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
    
  #
  # start to play game
  #
  def playGame( self ):
    while 1:
      command = self.readline()
      debug.echo('Read: ' +  command)
      tokens =  string.split(command)
      if tokens[0] == 'GAME_OVER':
        winnerNum = int(tokens[1])
        print 'Player "%s" won!' % self.players[winnerNum].name
        break
      
      elif tokens[0] == 'NEW_PLAYER':
        print 'Player', tokens[1], 'has joined the game'
        
      elif tokens[0] == 'START_GAME':
        self.players = []
        numPlayers = int(tokens[1])
        for i in range(numPlayers):
          self.players.append( Player(tokens[2*i+2], int(tokens[2*i+3])) )
        print 'Game starting with players:',
        for player in self.players[:-1]:
          print player.name + ',',
        print self.players[-1:][0].name
        self.displayPlayerStats()
          
      elif tokens[0] == 'NEW_HAND':
        self.cardList = CardList()
        self.numTricks = int(tokens[1])
        print 'New hand... Tricks: ', self.numTricks, 'Dealer:', \
              self.players[int(tokens[2])].name
        
      elif tokens[0] == 'DRAW':
        card = int(tokens[1])
        debug.echo( 'Dealt ' + cardToString(card))
        self.cardList.addCard(card)
        
      elif tokens[0] == 'DEAL_OVER':
        self.trump = int(tokens[1])
        self.displayHand()
        
      elif tokens[0] == 'BID_ANNOUNCE':
        playerNum = int(tokens[1])
        bid = int(tokens[2])
        print 'Player "%s" bid %s' % (self.players[playerNum].name, bid)
        self.players[playerNum].bid = bid
        
      elif tokens[0] == 'BID':
        self.getBid()
        
      elif tokens[0] == 'CARD_PLAYED':
        player = int(tokens[1])
        card = int(tokens[2])
        print 'Player "%s" played %s' %(self.players[player].name,
                                        cardToString(card))
        
      elif tokens[0] == 'GET_CARD':
        self.playCard()
        
      elif tokens[0] == 'TRICK_WINNER':
        player = int(tokens[1])
        print 'Player "%s" won trick' % self.players[player].name
        self.players[player].wonTrick()
        
      elif tokens[0] == 'END_HAND':
        for i in range(len(self.players)):
          player = self.players[i]
          print 'Player "%s"' % player.name,
          delta = int(tokens[i+1])
          if delta > 0:
            print 'made %d points' % delta
          elif delta < 0:
            print 'went down %d points' % (-delta)
          else:
            print 'went over'
          player.score = player.score + delta
        self.displayPlayerStats()
        for p in self.players:
          p.reset()
          
      else:
        print 'Unknown command: ', command

  #
  # display cards in hand
  #
  def displayHand( self ):
    print 'Trump:',
    if self.trump >= 0:
      print cardToString(self.trump)
    else:
      print 'None'
      
    cardLetters = '23456789TJQKA'
    cardValue = 0
    
    for suit in range(4):
      print "%8s:" % CardList.suit[suit],
      
      for value in range(13):
        if self.cardList.hasCard(cardValue):
          print cardLetters[value],
        else:
          print ' ',
          
        cardValue = cardValue + 1
        
      print ''

  #
  # display player stats
  #
  def displayPlayerStats( self ):
    print '%-20.20s Bid Tricks Score' % 'Name'
    for p in self.players:
      if p.bid >= 0:
        print '%-20.20s %3d  %3d  %5d' % (p.name, p.bid, p.numTricks, p.score)
      else:
        print '%-20.20s      %3d  %5d' % (p.name, p.numTricks, p.score)
      

  #
  # print player bids
  #
  def displayBids( self ):
    print 'Player bids: ',
    for player in self.players:
      print player.name, ':',
      if player.bid >= 0:
        print player.bid, '  ',
      else:
        print 'None  ',
    print ''
    

  #
  # get bid from player and send it to server
  #
  def getBid( self ):
    self.displayBids()
    
    while 1:
      print 'Enter bid: ',
      try:
        bid = int(sys.stdin.readline())
      except ValueError:
        bid = -1
        
      if bid >= 0 and bid <= self.numTricks:
        self.send('BID %d' % bid)
        response = self.readline()
        if response == 'OK':
          break
        elif string.split(response)[0] == 'BADBID':
          print 'Illegal bid, try again'
          break
        else:
          print 'Illegal bid, try again'
      else:
        print 'Illegal bid, try again'
          
      self.displayBids()
      self.displayHand()
          
  #
  # play card and send it to server
  #
  def playCard( self ):
    cardLetters = '23456789TJQKA'
    suitLetters = 'CDHS'
    self.displayPlayerStats()
    self.displayHand()

    #
    # get valid card choice from user
    #
    cardValue = -1
    cardSuit = -1
    done = 0
    while not done:
      print 'Play card: ',
      cardStr = string.strip(string.upper(sys.stdin.readline()))
      if self.cardList.numCards() > 1:
        if len(cardStr) != 2:
          print 'Illegal card, try again'
          self.displayHand()
        
        else:
          cardValue = cardLetters.find(cardStr[0])
          cardSuit = suitLetters.find(cardStr[1])
        
          if cardValue < 0 or cardSuit < 0:
            print 'Illegal card, try again'
            self.displayHand()
          
          else:
            card = cardSuit*13 + cardValue
          
            if self.cardList.hasCard(card):
              done = 1
            else:
              print 'You don\'t have that card!'
              self.displayHand()
      else:
        card = self.cardList.getFirstCard()
        done = 1

    #
    # send choice to server
    #
    self.send('PLAY_CARD %d' % card)
    response = self.readline()
    if response == 'OK':
      self.cardList.removeCard(card)
    else:
      print 'Illegal card, try again'

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
      print 'Logged out'
    else:
      print 'Login error!'


#
# Oh Hell player class
#
# Attributes:
#   name
#     name of player
#
#   score
#     score of player
#
#   bid
#     player's bid
#
#   numTricks
#     number of tricks taken by player
#
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

#
# main program
#
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
  client.play()


