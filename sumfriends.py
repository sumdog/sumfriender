#!/usr/bin/env python3

import time

import configparser
import urllib.request
import urllib.parse
import webbrowser
import json
import argparse
import os
import sys

class Facebook(object):

  def __init__(self,config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    self.fb_app = config.get('FB_API','APP_ID')
    self.fb_key = config.get('FB_API','APP_KEY')
    self.redirect_uri = config.get('FB_API','REDIRECT_URI')
    self.oauth_token = config.get('FB_API','OAUTH_TOKEN')

    self.config_file = config_file
    self.config_parser = config

  def requires_auth(self):
    return self.oauth_token.strip() == '' 

  
  def __fb_url(self,path,vars):
    return 'https://graph.facebook.com/{0}?{1}'.format(
      path,
      urllib.parse.urlencode(vars))

  def __make_request(self,url):
    #print(url)
    with urllib.request.urlopen(url) as html:
      return str( html.read() , 'ascii' , 'ignore' )

  def login(self):
    webbrowser.open(self.__fb_url('oauth/authorize',
      { 'type' : 'user_agent' , 
        'client_id' : self.fb_app , 
        'redirect_uri' : self.redirect_uri,
        'response_type' : 'token' ,
        'scope' : 'user_friends'
      }
    ))

  def __friends_as_dict(self,obj):
    ret = {}
    for f in obj:
      ret[f['id']] = f['name']
    return ret

  def friend_list(self):
    obj = json.loads((self.__make_request(self.__fb_url('me/friends',
      { 'access_token' : self.oauth_token }
    ))))
    friends = self.__friends_as_dict(obj['data'])
    while 'paging' in obj and 'next' in obj['paging']:
      obj = json.loads(self.__make_request(obj['paging']['next']))
      if len(obj['data']) > 0:
        friends.update(self.__friends_as_dict(obj['data']))
    return friends

  def user_active(self,uid):
    try:
      obj = json.loads(self.__make_request(self.__fb_url(uid,
        { 'access_token' : self.oauth_token }
      )))
      return 'id' in obj
    except urllib.error.HTTPError:
      return False

  def extend_token(self):
    "Requests a new OAUTH token with extended expiration time and saves it to the config file"
    token = urllib.parse.parse_qs(self.__make_request(self.__fb_url('oauth/access_token',{
      'client_id' : self.fb_app ,
      'client_secret' : self.fb_key ,
      'grant_type' : 'fb_exchange_token' ,
      'fb_exchange_token' : self.oauth_token
    })))['access_token'][0]

    self.config_parser.set('FB_API','OAUTH_TOKEN',token)
    fd = open(self.config_file,'w+')
    self.config_parser.write(fd)
    fd.close()




def load_old_friends(data_file):
  oldfriend = open(data_file,'r')
  data = {}
  for of in oldfriend:
    parts = of.split(" ")
    data[parts[0]] = " ".join(parts[1:]).strip()
  return data

    
def save_friends(data_file,list):
  fd = open(data_file,'w')
  for f in list:
    print( "{0:15}  {1}".format(f[0],  str(f[1]['name'].encode('utf-8'),'ascii','ignore')   ) )

def save_new_friends(data):
  pass

if __name__ == '__main__':


  parser = argparse.ArgumentParser(
    description='A script to scan for changes in Facebook friend statuses',
    epilog='Copyright 2013 Sumit Khanna. Free for non-commercial use. PenguinDreams.org')
  #usage='%prog [-c config file] [-f friends file] [-s status file]'

  parser.add_argument('-v','--version', action='version', version='%(prog)s 0.1')
  parser.add_argument('-c',help='configuration file with API/AUTH keys [default: %(default)s]',
    default='sumfriender.config',metavar='config')
  parser.add_argument('-f',help='friend list db file [default: %(default)s]',
    default='friends.txt',metavar='friend_db')
  parser.add_argument('-s',help='status log file [default: %(default)s]',
    default='status.txt',metavar='status')
  
  args = parser.parse_args()

  if not os.path.exists(args.c):
    print('Configuration file {0} does not exist'.format(args.c), file=sys.stderr)
    sys.exit(2)

  fb = Facebook(args.c)
  if fb.requires_auth():
    print("You need a login key. Copy your access token to the OAUTH_TOKEN field in the configuration file.",file=sys.stderr)
    fb.login()
    sys.exit(3)
  else:

    #Let's renew our token so it doesn't expire
    fb.extend_token()

    cur_friends = fb.friend_list()  

    if not os.path.exists(args.f):
      print("{0} not found. Creating initial friends list".format(args.f))
      save_friends(args.f,cur_friends)
    else:

      old_friends = load_old_friends('friends.txt')

      status_out = open(args.s,'wa')

      for uid in old_friends:
        if uid not in cur_friends:
          status = 'is no longer in your friends list' if fb.user_active(uid) else 'has been deactivated'
          output = "Friend {0} ({1}) {2}".format(old_friends[uid],uid,status)

          print(output)
          status_out.write(output)

      status_out.close()
      save_friends(cur_friends,args.f)