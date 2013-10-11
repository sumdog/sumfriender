#!/usr/bin/env python3

import time

import configparser
import urllib.request
import urllib.parse
import webbrowser
import json

class Facebook(object):

  def __init__(self,config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    self.fb_app = config.get('FB_API','APP_ID')
    self.fb_key = config.get('FB_API','APP_KEY')
    self.redirect_uri = config.get('FB_API','REDIRECT_URI')
    self.oauth_token = config.get('FB_API','OAUTH_TOKEN')

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

  def get_friends(self):
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


def load_old_friends(data):
  oldfriend = open(data,'r')
  data = {}
  for of in oldfriend:
    parts = of.split(" ")
    data[parts[0]] = " ".join(parts[1:]).strip()
  return data

"""
def load_current_friends():
  fbcmd = Popen(['fbcmd','friends'],shell=False,bufsize=1,stdin=PIPE,stdout=PIPE)
  data = {}
  for line in fbcmd.stdout.readlines():
    parts = str(line,'ascii','ignore').split(" ")
    if parts[0].strip() != 'ID':
      data[parts[0]] = ' '.join(parts[1:]).strip()
  return data
  """
    
  


def sav_unfriends():
  pass

def save_new_friends():
  pass

if __name__ == '__main__':

  fb = Facebook("sumfriender.config")
  if fb.requires_auth():
    print("You need a login key. Copy your access token to the OAUTH_TOKEN field in the configuration file.")
    fb.login()
  else:
    cur_friends = fb.get_friends()  
    old_friends = load_old_friends('friends.txt')

    for uid in old_friends:
      if uid not in cur_friends:
        status = 'is no longer in your friends list' if fb.user_active(uid) else 'has been deactivated'
        print("Friend {0} ({1}) {2}".format(old_friends[uid],uid,status))
