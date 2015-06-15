#!/usr/local/bin/python

class Debug:
  def __init__(self):
    self.on = 1

  def turnOn(self):
    self.on = 1

  def turnOff(self):
    self.on = 0

  def echo(self, msg):
    if self.on:
      print msg

if __name__ == '__main__':
  debug = Debug()
  debug.echo("test 1")
      
