#!/usr/bin/env python

"""
PingMovingAverage
(Python 2 only -- see PingMovingAverage3 for newer, Python3 compliant version)

Continually pings a server and calculates the moving average of the last few 
pings.
"""

from collections import deque
import subprocess as sub
from threading import Timer

# http://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class PingMovingAverage (object):
  """
  The ping moving average object.
  """
  def __init__(self, callback, host, delay=1, depth=10):
    """
    __init__
    
    callback: a callback function, with the signature callback(rtt, lost)
    host: the host to ping
    delay: delay in seconds between pings
    depth: depth of the moving average in pings
    """
    self.host = host
    self.q = deque(maxlen=depth)
    self.delay = delay
    self.callback = callback

  def calc_average(self):
    """
    calc_average: calculate the average rtt and lost percent of the pings
    """
    rtt_sum = 0.
    reach_count = 0
    lost_count = 0.
    for (rtt, reachable) in self.q:
      if reachable:
        rtt_sum += rtt
        reach_count += 1
      else: lost_count += 1
    rtt_avg = rtt_sum / reach_count
    lost_avg = lost_count / len(self.q)
    return rtt_avg, lost_avg
    
  def ping(self):
    """
    ping: actually ping the host
    """
    p = sub.Popen(["ping", "-q", "-c1", self.host], stdout=sub.PIPE, stderr=sub.PIPE)
    output, _ = p.communicate()
    if 0 == p.returncode: # Reachable
      res = float(output.split("\n")[4].split(" ")[3].split("/")[0])
      self.q.append((res, True))
    elif 1 == p.returncode: # Unreachable due to packet loss
      self.q.append((0., False))
    elif 2 == p.returncode: # Unreachable due to unknown host
      self.q.append((0., False))
    _, __ = self.calc_average()
    self.callback(_, __)
    
  def start(self):
    """
    start: start pinging the host
    """
    self.timer = RepeatedTimer(self.delay, self.ping)
    self.timer.start()
    
  def stop(self):
    """
    stop: stop pinging the host
    """
    self.timer.stop()

if __name__ == "__main__":
  import os
  import signal
  from sys import argv, exit
  
  def cb(rtt, lost):
    print "%10.6f %10.6f" % (rtt, lost)

  pma = PingMovingAverage(cb, argv[1])
  pma.start()
  
  def sigint(signal, frame):
        print('Caught SIGINT. Quitting!')
        pma.stop()
        exit(0)
  signal.signal(signal.SIGINT, sigint)
