""" Script that tests the shuffle function from the python random module. """

import random

deck = range(1,4)

combos = {(3,1,2): 0, (3,2,1): 0, (2,3,1): 0, (2,1,3): 0, (1,2,3): 0, (1,3,2): 0}

n = 2
loop = 1

while loop <= 600000:
    random.shuffle(deck)
    checkDeck = tuple(deck)
    combos[checkDeck] += 1
    loop += 1
    
print combos.values()

