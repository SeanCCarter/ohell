#!/usr/bin/python

###################################################
# Oh-hell server
###################################################

import sys, time, string, random, os
from select import select
from socket import socket, AF_INET, SOCK_STREAM
from card import *
from GameState import *

def now():
  return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


#####################################
#####################################
class OhHellServer:
  """
  Oh Hell server class
 
  Attributes:
    serverAddress
      address of server

    serverPort
      port server is listening on

    serverSocket
      socket that server uses for listening to incoming connections

    sockets
      list of all sockets maintained by server

    players
      list of players (Player instances)

    numReadyPlayers
      number of players ready to play

    numPlayers
      number of players in game

    state
      state of game, one of:
        REGISTRATION - new game, waiting for all players to register
        RESTART      - recovering and restarting old game, waiting for players
        PLAYING      - game is under way

    gameState
      state of the game, really a history of the hands

    trickNums
      a list of the num of tricks for each hand to play

    numHands
      how many hands to play

    handNum
      the number of the current hand

    dealer
      the index of the dealer for the current hand

    trump
      the trump for the current hand

    deck
      the deck of cards for the current hand
  """
  
  def __init__(self, port = 7000):
    """
    Constructor
    Parameter:
      port - TCP port for server to listen on
    """
    self.serverAddress = ''
    self.serverPort = port
    self.players = []
    self.numReadyPlayers = 0

  #
  # start a brand new game
  # Parameter:
  #   numPlayers - number of players in game
  #
  def newGame( self, numPlayers ):
    
    print 'New Game of', numPlayers, 'players'
    
    self.gameState = GameState()
    self.gameState.init_new(numPlayers, now())
    
    self.state = 'REGISTRATION'
    self.findXMLFileName()
    self.mainloop(numPlayers)

  #
  # restart a game
  # Parameter:
  #   fileName - name of file with state of old game (in XML)
  #
  def restart( self, fileName ):
    parser = GameXMLParser()
    self.xmlFileName = fileName
    self.gameState = parser.parse(fileName)
    self.incomingPlayers = self.gameState.getPlayers()
    
    for p in self.incomingPlayers:
      self.players.append( Player(None, p[1]) )
      
    self.state = 'RESTART'
    self.mainloop(len(self.incomingPlayers))
      
  #
  # the main loop for the game
  # Parameter:
  #   numPlayers - number of players in game
  #
  def mainloop(self, numPlayers):
    self.numPlayers = numPlayers
    self.serverSocket = socket(AF_INET, SOCK_STREAM)
    self.serverSocket.bind((self.serverAddress, self.serverPort))
    self.serverSocket.listen(5)
    self.sockets = [ self.serverSocket, ]
    
    print 'Server initialized'
    try:
      
      while 1:
        
        readable, writeable, exceptable = select( self.sockets, [], [] )
        
        for sock in readable:
          
          if sock is self.serverSocket:
            newSock, address = self.serverSocket.accept()
            
            print 'Connect:', address, id(newSock)
            
            self.sockets.append(newSock)
            
          else:
            tokens = self.readClientMessage(sock)
            if tokens is not None:
              self.processClientMessage(sock,tokens)

    finally:
      for sock in self.sockets:
        sock.close()

  #
  # Read a message from client
  # The message is split into tokens using whitespace as delimiters
  #
  # Parameter:
  #   socket - socket to read from
  # Return value:
  #   list of tokens or None on error
  #
  def readClientMessage(self, socket):
    
    data = socket.recv(1024)
    
    if not data:
      socket.close()
      self.sockets.remove(socket)
      return None
    
    else:
      print '\tRead:', data, 'on', id(socket)
      tokens = string.split(data)
      return tokens

  #
  # process message from client
  # Parameters:
  #   socket - socket for client
  #   tokens - tokens of message from client
  # Notes:
  #   Also starts game when all players have registered.
  #   Should this be changed??
  #
  def processClientMessage(self, socket, tokens):
    
    if tokens[0] == 'LOGOUT':
      self.logoutPlayer(socket)
      
    elif self.state == 'REGISTRATION' or self.state == 'RESTART':
      print "Registration state."
      
      if tokens[0] == 'LOGIN':
        print 'Login: ', tokens[1]
        
        self.loginPlayer(socket, tokens[1])
        
        if self.numReadyPlayers == self.numPlayers:
          print "Players Ready."

          # if new game
          if self.state == 'REGISTRATION':
            self.playGame(0, -1)

          else: # restarting interrupted game
            scores = self.gameState.currentScores()
            
            for i in range(self.numPlayers):
              self.players[i].score = scores[i]
              
            self.playGame( self.gameState.numHands(),
                           self.gameState.nextDealer())
          raise 'End server'
    else:
      print 'Error'
      socket.send('ERROR Unknown\n')

  #
  # logs out player
  # Parameter:
  #   socket - socket of player
  #
  def logoutPlayer( self, socket ):
    
    player = findPlayer(socket)
    
    if player is not None:
      i = self.players.index(player)
      del self.players[i]
      player.sendMessage('OK')
    else:
      socket.send('ERROR\n')

  #
  # broadcast a message to all players
  # Parameter:
  #   msg - text of message
  #
  def broadcastMessage( self, msg ):
    for player in self.players:
      player.sendMessage(msg)

  #
  # make a list of numbers of tricks for each hand
  # Parameter:
  #   handNum - number of the hand to start with (0 = first)
  # Return value:
  #   a list of the number of tricks for each hand
  #
  def makeTrickNums(self, handNum):
    trickNums = []
    
    for i in range(10,1,-1):
      trickNums.append(i)
      
    for i in range(self.numPlayers):
      trickNums.append(1)
      
    for i in range(2,11):
      trickNums.append(i)
      
    return trickNums[handNum:]

  #
  # start game
  # Parameters:
  #   handNum - number of hand to start with (0 = first)
  #   dealer  - index of player to start dealing (-1 to pick randomly)
  #
  def startGame(self, handNum, dealer):
    print 'startGame()'
    startMessage = 'START_GAME ' + str(self.numPlayers) + ' '
    id = 0
    for player in self.players:
      startMessage = startMessage + player.name + ' ' + str(player.score) + ' '
      if handNum == 0:
        self.gameState.addPlayer( id, player.name, None)
      id = id + 1
    self.broadcastMessage(startMessage)
    self.trickNums = self.makeTrickNums(handNum)

    self.handNum = 0

    self.numHands = 18 + self.numPlayers - self.handNum
    
    if dealer < 0:
      self.dealer = random.randrange(self.numPlayers)
    else:
      self.dealer = dealer
    print 'Initial dealer:', self.dealer

  #
  # calculate index of next player in sequence
  # Parameter:
  #   playerNum - current player
  # Return value:
  #   index of next player
  #
  def nextPlayer(self, playerNum ):
    return (playerNum + 1) % self.numPlayers

  #
  # start playing hand
  # creates new deck, deals cards and picks trump (if necessary)
  #
  def startHand(self):
    print 'startHand()'
    self.broadcastMessage('NEW_HAND %d %d' % ( self.trickNums[self.handNum],
                          self.dealer))
    self.deck = Deck()
    for player in self.players:
      player.reset()
    playerNum = self.nextPlayer(self.dealer)
    for trick in range(self.trickNums[self.handNum]):
      for player in range(self.numPlayers):
        card = self.deck.draw()
        self.players[playerNum].drawCard(card)
        playerNum = self.nextPlayer(playerNum)
    if self.trickNums[self.handNum] != 10:
      self.trump = self.deck.draw()
    else:
      self.trump = -1
    self.broadcastMessage('DEAL_OVER %d' % self.trump)

  #
  # logins in player
  # Parameters:
  #   sock - socket for player
  #   name - requested name for player
  #
  def loginPlayer(self, sock, name):
    lname = string.lower(name)
    if self.state == 'REGISTRATION':
      for player in self.players:
        if string.lower(player.name) == lname:
          sock.send('ERROR Name already logged in\n')
          return 1
      sock.send('OK\n')
      self.broadcastMessage('NEW_PLAYER ' + name)
      self.players.append(Player(sock, name))
    else:
      found = 0
      for i in range(len(self.players)):
        if (string.lower(self.players[i].name) == lname
            and self.players[i].socket is None):
          sock.send('OK\n')
          self.broadcastMessage('NEW_PLAYER ' + self.players[i].name)
          self.players[i].socket = sock
          found = 1
      if not found:
        sock.send('ERROR Name not found or already logged in\n')
        return 1
    print 'Adding player:', name
    self.numReadyPlayers = self.numReadyPlayers + 1

  #
  # ends game
  # finds winner and closes connections
  #
  def endGame(self):
    winnerNum = 0
    bestScore = self.players[0].score
    for i in range(1,self.numPlayers):
      if self.players[i].score > bestScore:
        winnerNum = i
        bestScore = self.players[i].score
    # look for ties!
    self.broadcastMessage('GAME_OVER %d' % winnerNum)
    for player in self.players:
      player.close()
    self.players = []
    self.sockets = [self.serverSocket, ]
    self.state = 'REGISTRATION'
      
    
  #
  # plays entire game
  # Parameters:
  #   handNum - number of hand to start with (0 = first)
  #   dealer  - index of initial dealer (-1 to pick randomly)
  #
  def playGame( self, handNum, dealer ):

    print 'XML log file is', self.xmlFileName
    self.state = 'PLAYING'
    self.startGame( handNum, dealer)
    
    for i in range(len(self.trickNums)):
      self.handNum = i
      self.startHand()
      self.getBids()
      self.playHand()
      self.dealer = self.nextPlayer(self.dealer)
      
    self.endGame()

  #
  # get bids from players
  #
  def getBids( self ):
    playerNum = self.nextPlayer(self.dealer)
    bidTotal = 0
    
    for player in range(self.numPlayers-1):
      bid = self.players[playerNum].getBid()
      bidTotal = bidTotal + bid
      self.players[playerNum].sendMessage('OK')
      self.broadcastMessage('BID_ANNOUNCE %d %d' % (playerNum, bid) )
      playerNum = self.nextPlayer(playerNum)
      
    while 1:
      bid = self.players[self.dealer].getBid()
      
      if bid + bidTotal != self.trickNums[self.handNum]:
        self.players[self.dealer].sendMessage('OK')
        self.broadcastMessage('BID_ANNOUNCE %d %d' % (playerNum, bid) )
        break
      else:
        self.players[self.dealer].sendMessage('BADBID %d' % bid)

  #
  # play a hand
  #
  def playHand( self ):
    hand = HandState(len(self.players), self.trickNums[self.handNum],
                     self.trump, self.dealer)
    for i in range(len(self.players)):
      cards = []
      for c in range(52):
        if self.players[i].hasCard(c):
          cards.append(c)
      hand.setHand(i, cards)
      hand.setBid(i, self.players[i].bid)
    playerNum = self.nextPlayer(self.dealer)
    for i in range(self.trickNums[self.handNum]):
      winnerNum, trick = self.playTrick(playerNum)
      hand.addTrick(trick)
      self.players[winnerNum].wonTrick()
      playerNum = winnerNum
      self.broadcastMessage( 'TRICK_WINNER %d' % winnerNum)

##    if self.trump == -1:
##      trumpSuite = None
##    else:
##      trumpSuite = cardSuit(self.trump)

    for i in range(len(self.players)):
      hand.setTricksMade(i, self.players[i].numTricks)
    self.gameState.addHand(hand)
    
    xmlFile = open(self.xmlFileName, "w")
    xmlFile.write( self.gameState.generateXML() )
    xmlFile.close()
    
    deltas = self.updateScores()
    message = 'END_HAND '
    for delta in deltas:
      message = message + '%d ' % delta
    self.broadcastMessage(message)

  #
  # play a trick of a hand
  # Parameter:
  #   leadPlayerNum - index of player to lead
  #
  def playTrick(self, leadPlayerNum):
    playerNum = leadPlayerNum
    firstCard = -1
    cards = []
    trick = TrickState()
    for i in range(self.numPlayers):
      player = self.players[playerNum]
      cardOK = 0
      while not cardOK:
        card = self.playCard(player, firstCard)
        cardOK = card >= 0
      if firstCard == -1:
        firstCard = card
      self.broadcastMessage('CARD_PLAYED %d %d' % (playerNum, card))
      cards.append( (playerNum, card) )
      trick.addCard( playerNum, card )
      playerNum = self.nextPlayer(playerNum)
    return self.findWinner(cards), trick

  #
  # play a card in a trick
  # Parameters:
  #   player    - player to play card
  #   firstCard - index of first card played in trick (-1 if player is leading)
  # Return value:
  #   index of card played or -1 if illegal card played
  #
  def playCard( self, player, firstCard):
    card = player.getCard()
    valid = 0
    if player.hasCard(card):
      if firstCard == -1:
        valid = 1
      else:
        if cardSuit(firstCard) == cardSuit(card):
          valid = 1
        elif not player.hasSuit( cardSuit(firstCard) ):
          valid = 1
    if valid:
      player.sendMessage('OK')
      player.removeCard(card)
      return card
    else:
      player.sendMessage('ERROR Improper card')
      return -1
  
  #
  # finds winner of trick
  # Parameter:
  #   cards - list of (player index, card) ordered pairs
  # Return value:
  #   index of winning player
  #
  def findWinner( self, cards ):
    winnerNum, bestCard = cards[0]
    for info in cards[1:]:
      playerNum, card = info
      if ( cardSuit(bestCard) == cardSuit(card)
           and cardValue(card) > cardValue(bestCard) ):
        winnerNum, bestCard = info
      elif ( cardSuit(bestCard) != cardSuit(self.trump)
             and cardSuit(card) == cardSuit(self.trump) ):
        winnerNum, bestCard = info
    return winnerNum

  #
  # update the scores based on current hand
  # Return value:
  #   a list of the changes in score of the players
  #
  def updateScores( self ):
    deltas = []
    for p in self.players:
      if p.bid == p.numTricks:
        delta = 10 + p.bid**2
      elif p.bid > p.numTricks:
        delta = -5*(p.bid - p.numTricks)
      else:
        delta = 0
      deltas.append(delta)
      p.score = p.score + delta
      p.reset()
    return deltas
        

  #
  # find an used file name for the XML log file
  # Return value:
  #   used file name for XML log file
  #
  def findXMLFileName( self ):
    fileName = time.strftime("%Y-%m-%d", time.localtime(time.time())) + '-game.xml'
    
    number = 2
    while os.access(fileName, os.F_OK):
      fileName = time.strftime("%Y-%m-%d", time.localtime(time.time())) + ('-g%d-game.xml'%number)
      number = number + 1
      
    self.xmlFileName = fileName

    


############################
# Player class
############################

#
# finds player from its socket
# Parameter:
#   socket - socket of player
# Return value:
#   corresponding player instance or None
#
def findPlayer( socket ):
  try:
    return Player.socketDictionary[socket]
  except:
    return None


#
# Player class
# Represents an Oh-Hell player
#
class Player:

  #
  # Dictionary that maps sockets to players
  #
  socketDictionary = { }

  #
  # Constructor
  # Parameters:
  #   socket - socket of player
  #   name   - name of player
  #
  def __init__(self, socket, name = ""):
    self.name = name
    self.socket = socket
    self.score = 0
    self.reset()
    Player.socketDictionary[socket] = self

  #
  # sends a message to player
  # Parameter:
  #   msg - text of message
  #
  # Note: This method automatically adds \n to end of msg
  #
  def sendMessage( self, msg):
    if self.socket is not None:
      self.socket.send(msg + '\n')

  #
  # draws a card for player
  # Parameter:
  #   card - card drawn by player
  #
  def drawCard( self, card):
    self.socket.send('DRAW %d\n' % card )
    self.cards.addCard(card)

  #
  # resets player for new hand
  #
  def reset( self ):
    self.cards = CardList()
    self.bid = 0
    self.numTricks = 0

  #
  # gets a bid from player
  #
  def getBid( self ):
    self.sendMessage('BID')
    response = self.socket.recv(1024)
    tokens = string.split(response)
    if tokens[0] != 'BID':
      self.sendMessage('ERROR Illegal command')
      return -1
    self.bid = int(tokens[1])
    return self.bid

  #
  # gets a card from player
  #
  def getCard( self ):
    self.sendMessage('GET_CARD')
    response = self.socket.recv(1024)
    tokens = string.split(response)
    if tokens[0] != 'PLAY_CARD':
      self.sendMessage('ERROR Illegal command')
      return -1
    return int(tokens[1])

  #
  # does player have card?
  # Parameters:
  #   card - card to check
  # Return value:
  #   1 if has card, else 0
  #
  def hasCard( self, card ):
    return self.cards.hasCard(card)

  #
  # removes card from card list of player
  # Parameter:
  #   card - index of card to remove
  #
  def removeCard( self, card ):
    self.cards.removeCard(card)

  #
  # does player have suit?
  # Parameter:
  #   suit - index of suit
  # Return value:
  #   1 if player has at least one card in suit, else 0
  #
  def hasSuit( self, suit):
    return self.cards.hasSuit(suit)

  #
  # called when player won a trick
  #
  def wonTrick( self ):
    self.numTricks = self.numTricks + 1

  #
  # closes socket of player
  #
  def close(self):
    self.socket.close()

###############################################################
# program code
###############################################################
import sys

def printUsage():
  print 'Usage: server.py -n <num_players> | -f <xml-recovery-file>'
  sys.exit(1)
  

if __name__ == '__main__':
  import getopt

  try:
    flags, args = getopt.getopt( sys.argv[1:], 'n:f:')
    if len(flags) != 1:
      printUsage()
  except getopt.GetoptError:
    printUsage()
    
  if flags[0][0] == '-n':
    try:
      numPlayers = int(flags[0][1])
    except ValueError:
      print 'Illegal parameter:', flags[0][1]
      sys.exit(1)
  elif flags[0][0] == '-f':
    fileName = flags[0][1]

  try:
    server = OhHellServer()
    if flags[0][0] == '-f':
      server.restart(fileName)
    else:
      server.newGame(numPlayers)
  except:
    info = sys.exc_info()
    print str(info[0])
    print str(info[1])
    print str(info[2])

#  server.serverSocket.shutdown(2)
                      
    


