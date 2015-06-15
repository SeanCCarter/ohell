""" Script that tests the Fisher-Yates shuffling algorithm. """

import random

deck = range(1,4)

combos = {(3,1,2): 0, (3,2,1): 0, (2,3,1): 0, (2,1,3): 0, (1,2,3): 0, (1,3,2): 0}

n = 2
loop = 1

while loop <= 600000:
    while n >= 0:
        k = random.randint(0, n)
        deck[k], deck[n] = deck[n], deck[k]
        checkDeck = tuple(deck)
        combos[checkDeck] += 1
        loop += 1
        n -= 1
    n = 2

print combos.values()
