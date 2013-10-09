#!/usr/bin/env python3

import time
from subprocess import Popen,PIPE

def load_old_friends(data):
  oldfriend = open(data,'r')
  data = {}
  for of in oldfriend:
    parts = of.split(" ")
    data[parts[0]] = " ".join(parts[1:]).strip()
  return data

def load_current_friends():
  fbcmd = Popen(['fbcmd','friends'],shell=False,bufsize=1,stdin=PIPE,stdout=PIPE)
  data = {}
  for line in fbcmd.stdout.readlines():
    parts = str(line,'ascii','ignore').split(" ")
    if parts[0].strip() != 'ID':
      data[parts[0]] = ' '.join(parts[1:]).strip()
  return data
    
  


def sav_unfriends():
  pass

def save_new_friends():
  pass

if __name__ == '__main__':
  
  old_friends = load_old_friends('friends.txt')
  cur_friends = load_current_friends()
  #print(old_friends)
  for uid in old_friends:
    if uid not in cur_friends:
      print("Friend {0} ({1}) is no longer in your friends list".format(old_friends[uid],uid))
