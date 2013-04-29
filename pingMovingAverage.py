#!/usr/bin/env python

# pingMovingAverage.py
# Copywrong 2013 Alison Chan alisonc@alisonc.net
# Released under terms of the WTFPL v2, included hereunder
#
#        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#                    Version 2, December 2004 
#
# Copyright (C) 2004 Sam Hocevar <sam@hocevar.net> 
#
# Everyone is permitted to copy and distribute verbatim or modified 
# copies of this license document, and changing it is allowed as long 
# as the name is changed. 
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE 
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION 
#
#  0. You just DO WHAT THE FUCK YOU WANT TO.
#

import os
import time
import collections as coll
import subprocess as sub
from sys import argv



_, hostname, delay, depth, outfile = argv

def calcAverage(theList):
    theSum = 0
    countReachable = 0
    thePacketLossSum = 0.
    for (rtt, reachable) in theList:
        if reachable:
            theSum += rtt
            countReachable += 1
        else: thePacketLossSum += 1
    theAvg = theSum / countReachable
    thePacketLossAvg = thePacketLossSum / len(theList)
    return theAvg, thePacketLossAvg

delay = float(delay)
depth = int(depth)

#Array of tuples (rtt, reachable)
results = coll.deque(maxlen=depth)

# Initial sanity check to make sure that the host is reachable!
p = sub.Popen(["ping", "-q", "-c1", hostname], stdout=sub.PIPE, stderr=sub.PIPE)
p.communicate()
if 2 == p.returncode: # Unreachable due to unknown host
    print "Unknown host. QUITTING"
    exit(1)

while True:
    # lol i have no idea what im doing
    p = sub.Popen(["ping", "-q", "-c1", hostname], stdout=sub.PIPE, stderr=sub.PIPE)
    output, _ = p.communicate()
    if 0 == p.returncode: # Reachable
        res = float(output.split("\n")[4].split(" ")[3].split("/")[0])
        results.append((res, True))
        av, pl = calcAverage(results)
    elif 1 == p.returncode: # Unreachable due to packet loss
        results.append((0., False))
    elif 2 == p.returncode: # Unreachable due to unknown host
        results.append((0., False))
        
    averages = "%10.6f %10.6f" % (av, pl)
    f = open(outfile, 'w')
    print averages
    f.write(averages)
    time.sleep(delay)
    

