#!/usr/bin/python

from card import *

#
# Game State class
# stores the history of a game
#
class GameState:

  #
  # constructor
  #
  def __init__(self):
    self.players = []
    self.hands = []

  #
  # initialize a new empty game
  # Parameters:
  #   numPlayers - number of players
  #   time       - time of game
  #
  def init_new( self, numPlayers, time ):
    self.numPlayers = int(numPlayers)
    self.time = time

  #
  # add a player
  # Parameters:
  #   id         - index of player
  #   playerName - name of player
  #   ip         - IP number of player
  #
  def addPlayer(self, id, playerName, ip):
    self.players.append( (id, playerName, ip) )

  #
  # add a hand of cards
  # Parameter:
  #   hand - a HandState representing next hand of cards
  #
  def addHand(self, hand):
    self.hands.append(hand)

  #
  # get list of players
  # Return value:
  #   list of player ordered triplets ( PlayerID, PlayerName, PlayerIP )
  #
  def getPlayers( self ):
    return self.players

  def getHands( self ):
    return self.hands

  #
  # returns number of hands
  # Return value:
  #   number of hands
  #
  def numHands(self):
    return len(self.hands)

  #
  # returns current scores of players
  # Return value:
  #   a list of current scores of players (in same order as getPlayers()
  #   returns)
  #
  def currentScores(self):
    scores = [0] * self.numPlayers
    for hand in self.hands:
      bids = hand.getBids()
      tricks = hand.getTricksMade()
      for i in range(self.numPlayers):
        if bids[i] == tricks[i]:
          scores[i] = scores[i] + 10 + bids[i]*bids[i]
        elif tricks[i] < bids[i]:
          scores[i] = scores[i] - 5*(bids[i] - tricks[i])
    return scores

  #
  # returns dealer of next hand
  # Return value:
  #   index of the dealer for next hand of cards
  #
  def nextDealer(self):
    lastHand = self.hands[self.numHands()-1]
    return (lastHand.dealer + 1) % self.numPlayers

  #
  # generate XML representation of game
  # Return value:
  #   XML rep of game as string
  #
  def generateXML(self):
    xml = "<?xml version=\"1.0\" ?>\n"
    xml = xml + "<game numPlayers=\"" + str(self.numPlayers) + "\" >\n"
    xml = xml + "<time>" + self.time + "</time>\n"
    xml = xml + self.generatePlayerXML()
    for hand in self.hands:
      xml = xml + hand.generateXML()
    xml = xml + "</game>\n"
    return xml

  #
  # generate player info XML
  # Return value:
  #   player info XML as a string
  #
  def generatePlayerXML(self):
    xml = ""
    for player in self.players:
      xml = xml + ("<player playerID=\"" + str(player[0]) + "\" name=\""
                   + player[1] + "\" >\n")
      if player[2] is not None:
        xml = xml + "<IP> " + str(player[2]) + " </IP>\n"
      xml = xml + "</player>\n"
    return xml

  def getScoreSheet( self):
    """
      Create a score sheet for the game
      
      Returns:
        List of scores
    """
    handScores = []
    scores = [0] * self.numPlayers
    for hand in self.hands:
      bids = hand.getBids()
      tricks = hand.getTricksMade()
      handScore = []
      
      for i in range(self.numPlayers):
        if bids[i] == tricks[i]:
          scores[i] = scores[i] + 10 + bids[i]*bids[i]
        elif tricks[i] < bids[i]:
          scores[i] = scores[i] - 5*(bids[i] - tricks[i])
        handScore.append( (bids[i], tricks[i], scores[i]))
        
      handScores.append( (hand.numCards, handScore) )
    return handScores
      
 
#
# class to represent a single trick of a hand of cards
#
class TrickState:
  #
  # constructor
  #
  def __init__(self):
    self.cards = []

  #
  # add a card to the trick
  # Parameters:
  #   playerID - id of player
  #   card     - card index of card played by player
  #
  def addCard( self, playerID, card ):
    self.cards.append( (playerID, card) )

  #
  # get list of cards in trick
  # Return value:
  #   list of cards in trick
  #
  def getCards( self ):
    return self.cards

  def getWinner( self, trump):
    """
      Find the winner of a trick
      
      Parameter:
        trump - Trump card
        
      Returns:
        Winning player
    """
    winnerNum, bestCard = self.cards[0]
    for info in self.cards[1:]:
      player, card_played = info
      if ( cardSuit(bestCard) == cardSuit(card_played)
           and cardValue(card_played) > cardValue(bestCard) ):
        winnerNum, bestCard = info
      elif ( trump >= 0 and cardSuit(bestCard) != cardSuit(trump)
             and cardSuit(card_played) == cardSuit(trump) ):
        winnerNum, bestCard = info
    return winnerNum

  #
  # generate XML for trick
  # Return value:
  #   string with XML encoding of trick
  #
  def generateXML( self ):
    xml = "<trick>\n"
    for card in self.cards:
      xml = xml + ("<play playerID=\"" + str(card[0]) + "\" card=\""
                   + str(card[1]) + "\" />\n")
    xml = xml + "</trick>\n"
    return xml

#
# class to represent a single hand of game
#
class HandState:
  #
  # constructor
  # Parameters:
  #   numPlayers - number of players
  #   numCards   - number of cards in hand
  #   trump      - index of trump card
  #   dealer     - index of dealer
  #
  def __init__(self, numPlayers, numCards, trump, dealer):
    self.numPlayers = int(numPlayers)
    self.numCards = int(numCards)
    self.trump = trump
    self.dealer = int(dealer)
    self.playerInfo = []
    self.tricks = []

  #
  # get the number of cards in the hand
  # Return value:
  #   number of cards in hand
  def getNumCards(self):
    return self.numCards

  #
  # get trump card
  # Return value:
  #   index of trump card
  #
  def getTrump(self):
    return self.trump

  #
  # returns bids of players for hand
  # Return value:
  #   list of bids (in order of player id)
  #
  def getBids( self ):
    bids = [0] * self.numPlayers
    for player in self.playerInfo:
      bids[player[0]] = player[1]
    return bids

  #
  # get tricks made by players during hand
  # Return value:
  #   list of tricks mad (in order of player id)
  #
  def getTricksMade( self ):
    tricks = [0] * self.numPlayers
    for player in self.playerInfo:
      tricks[player[0]] = player[3]
    return tricks

  #
  # returns the list of tricks for hand
  # Return value:
  #  list of tricks for hand
  #
  def getTricks( self ):
    return self.tricks

  #
  # return dealer of hand
  # Return value:
  #   index of dealer of hand
  # 
  def getDealer(self):
    return self.dealer

  def getHands(self):
    hands = [0] * self.numPlayers
    for player in self.playerInfo:
      hands[player[0]] = player[2]
    return hands

  #
  # set bid of player
  # Parameters:
  #   playerID - id of player
  #   bid      - bid of player
  #
  def setBid( self, playerID, bid ):
    found = 0
    for i in range(len(self.playerInfo)):
      player = self.playerInfo[i]
      if player[0] == playerID:
        found = 1
        self.playerInfo[i] = (player[0], bid, player[2], player[3] )
        break
    if not found:
      raise "playerID (%d) not found in HandState.setBid" % playerID

  #
  # set the cards dealt to the given player for the hand
  # Parameters:
  #   playerID - id of player
  #   cards    - list of cards dealt to player
  #
  def setHand( self, playerID, cards ):
    self.playerInfo.append( (playerID, -1, cards, -1) )


  #
  # add a trick played to the hand
  # Parameters:
  #   trick - trick (TrickState) to add to hand
  #
  def addTrick( self, trick ):
    self.tricks.append(trick)
    
  #
  # set tricks made of player
  # Parameters:
  #   playerID   - id of player
  #   tricksMade - tricks made by player
  #
  def setTricksMade( self, playerID, tricksMade ):
    found = 0
    for i in range(len(self.playerInfo)):
      player = self.playerInfo[i]
      if player[0] == playerID:
        found = 1
        self.playerInfo[i] = (player[0], player[1], player[2], tricksMade )
        break
    if not found:
      raise "playerID not found in HandState.setTricksMade"

  #
  # generate XML for hand
  # Return value:
  #   XML representing hand as string
  #
  def generateXML(self):
    xml = ("<hand numCards=\"" + str(self.numCards) + "\" dealer=\""
           + str(self.dealer) + "\" >\n")
    if self.trump >= 0:
      xml = xml + "<trump> " + str(self.trump) + " </trump>\n"
    for player in self.playerInfo:
      xml = xml + "<deal playerID=\"" + str(player[0]) +"\" >\n"
      for card in player[2]:
        xml = xml + "<card value=\"" + str(card) + "\" />\n"
      xml = xml + "</deal>\n"
    for player in self.playerInfo:
      xml = xml + ("<bid playerID=\"" + str(player[0]) + "\" value=\""
                   + str(player[1]) + "\" />\n")
    for trick in self.tricks:
      xml = xml + trick.generateXML()
    for player in self.playerInfo:
      xml = xml + ("<tricks playerID=\"" + str(player[0]) + "\" value=\""
                   + str(player[3]) + "\" />\n")
    xml = xml + "</hand>\n"
    return xml
  



import xml.sax

class XMLHandler(xml.sax.handler.ContentHandler):
  def __init__(self):
    xml.sax.handler.ContentHandler.__init__(self)

  def startElement(self, name, attrs):
    if name == 'game':
      key_list = attrs.keys()
      i = key_list.index('numPlayers')
      self.numPlayers = attrs.getValue('numPlayers')
    elif name == 'player':
      key_list = attrs.keys()
      i = key_list.index('playerID')
      playerID = attrs.getValue('playerID')
      i = key_list.index('name')
      name = attrs.getValue('name')
      self.gameState.addPlayer(playerID, name, None)
    elif name == 'hand':
      numCards = attrs.getValue('numCards')
      dealer = attrs.getValue('dealer')
      self.hand = HandState(self.numPlayers, numCards, -1, dealer)
    elif name == 'bid':
      self.hand.setBid(int(attrs.getValue('playerID')),
                       int(attrs.getValue('value')))
    elif name == 'tricks':
      self.hand.setTricksMade(int(attrs.getValue('playerID')),
                              int(attrs.getValue('value')))
    elif name == 'deal':
      self.playerCards = []
      self.playerCardsID = int(attrs.getValue('playerID'))
    elif name == 'card':
      self.playerCards.append( int(attrs.getValue('value')) )
    elif name == 'trick':
      self.trick = TrickState()
    elif name == 'play':
      self.trick.addCard( int(attrs.getValue('playerID')),
                          int(attrs.getValue('card')))

  def endElement(self, name):
    if name == 'time':
      self.gameState.init_new(self.numPlayers, self.chars)
    elif name == 'trump':
      self.hand.trump = int(self.chars)
    elif name == 'hand':
      self.gameState.addHand(self.hand)
    elif name == 'deal':
      self.hand.setHand(self.playerCardsID, self.playerCards)
    elif name == 'trick':
      self.hand.addTrick(self.trick)
    self.chars = ''

  def startDocument(self):
    self.gameState = GameState()
      
  def endDocument(self):
    pass
  
  def characters(self, content):
    self.chars = content

  def getGameState(self):
    return self.gameState


class GameXMLParser:

  def __init__( self ):
    self.parser = xml.sax.make_parser()
    self.handler = XMLHandler()
    self.parser.setContentHandler(self.handler)

  def parse( self, input ):
    self.parser.parse(input)
    return self.handler.getGameState()


if __name__ == '__main__':
  import sys
  parser = GameXMLParser()
  gameState = parser.parse(sys.argv[1])
  print gameState.generateXML()

  print gameState.currentScores()
  print 'Next dealer: ', gameState.nextDealer()
 
##  state = GameState(3, "now")
  
##  state.addPlayer(1, "Paul" , "127.0.0.1")
##  state.addPlayer(2, "Anne", "192.168.1.3")
##  state.addPlayer(3, "Lester", "65.65.65.65")
  
##  hand1 = HandState(state.numPlayers, 10, None, 1)
##  hand1.setBid(2, 4)
##  hand1.setBid(3, 2)
##  hand1.setBid(1, 3)
##  hand1.setTricksMade(2, 4)
##  hand1.setTricksMade(3, 3)
##  hand1.setTricksMade(1, 3)
##  state.addHand(hand1)

##  hand2 = HandState(state.numPlayers, 9, 1, 2)
##  hand2.setBid(3, 3)
##  hand2.setBid(1, 3)
##  hand2.setBid(2, 4)
##  hand2.setTricksMade(3, 3)
##  hand2.setTricksMade(1, 2)
##  hand2.setTricksMade(2, 4)
##  state.addHand(hand2)
  
##  print state.generateXML()
  
