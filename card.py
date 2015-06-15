###############################################
# card.py
###############################################

import random


class Deck:
  def __init__(self):
    self.deck = []
    cards = range(52)

    for i in range(51):
      index = random.randrange(len(cards))
      self.deck.append(cards[index])
      del cards[index]
      
    self.deck.append(cards[0])
      
##    # shuffle deck
##    for i in range(1000):
##      index = random.randrange(52)
##      card = self.deck[index]
##      del self.deck[index]
##      self.deck = [card] + self.deck

  def draw(self):
    card = self.deck[0]
    del self.deck[0]
    return card


class CardList:

  suit = [ 'Clubs', 'Diamonds', 'Hearts', 'Spades' ]
  value = [ 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight',
            'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace' ]

  def __init__(self, init=0):
    self.cards = []
    for i in range(52):
      self.cards.append(init)

  def hasCard( self, cardIndex ):
    return self.cards[cardIndex]

  def addCard( self, cardIndex ):
    self.cards[cardIndex] = 1

  def removeCard( self, cardIndex ):
    self.cards[cardIndex] = 0

  def hasSuit( self, suit ):
    for i in range(suit*13, suit*13+13):
      if self.cards[i]:
        return 1
    return 0

#
# return number of cards
#
  def numCards( self ):
    cnt = 0
    
    for i in range(52):
      if self.cards[i]:
        cnt = cnt + 1
        
    return cnt

#
# return first card found in list
#
  def getFirstCard( self ):
    for i in range(52):
      if self.cards[i]:
        return i

    return -1

def cardSuit( cardIndex ):
  return cardIndex / 13

def cardValue( cardIndex ):
  return cardIndex % 13

def cardToString( cardIndex ):
  return CardList.value[cardValue(cardIndex)] + ' of ' \
         + CardList.suit[cardSuit(cardIndex)]


if __name__ == '__main__':
  deck = Deck()
  print len(deck.deck)
  print deck.deck
