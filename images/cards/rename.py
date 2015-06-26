import glob
import string
import os

def rename(f, longSet, set, numAdded):
    f = f[:-7]
    print f
    f = f[len(longSet):]
    print f
    numberList = range (2, 11)
    if 'j' in f: n = set + 'j' + '.png'
    elif 'q' in f: n = set + 'q' + '.png'
    elif 'k' in f: n = set + 'k'  + '.png'
    elif 'a' in f: n = set + 'a' + '.png'
    else: 
        for num in numberList:          
            if str(num) in f:
                n = set + str(num) + '.png'
    return n, numAdded

#get all the jpg file names in the current folder
files = glob.glob("*.png") 
#sort the list
files.sort()
count = 2
n = 0
numAdded = '5'
# and rename each file
for f in files:
    count = count + 1
    if 'clubs' in f: n, numAdded = rename(f, 'clubs', 'c', numAdded)
    if 'diamonds' in f: n, numAdded = rename(f, 'diamonds', 'd', numAdded)
    if 'hearts' in f: n, numAdded = rename(f, 'hearts', 'h', numAdded)
    if 'spades' in f: n, numAdded = rename(f, 'spades', 's', numAdded)
    try:
        os.rename(f, n)
        print
    except:
        print "error: didn't rename"
