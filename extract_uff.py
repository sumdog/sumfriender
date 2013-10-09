#!/usr/bin/env python3
#
#  extract_uff.py  -  Extracts friends/unfriends list from previous 
#                     versions of the UnfriendFinder GreaseMonkey script 
#                     and FireFox Plugin
#
#  Sumit Khanna <sumit@penguindreams.org> - http://penguindreams.org
#
#  License: Free for non-commercial use
#


import sys
import re
import json 
import time

def format_json(json_obj):
  obj = json.loads(json_obj)
  ret = []
  for f in obj.items():
    ret.append( "{0:15}  {1}".format(f[0],  str(f[1]['name'].encode('utf-8'),'ascii','ignore')   ) )
  return ret

def save(name,lst):
  print("Writing {0}".format(name))
  fd = open(name,'w')
  for i in lst:
    fd.write("{0}\n".format(i))
  fd.close()

def user_pref(key,json_obj):
  section = key.split('_')[-1:][0]
  if section == 'unfriends':
    save('unfriends.txt',format_json(json_obj))  
  if section == 'deactivated':
    save('deactivated.txt',format_json(json_obj))
  if section == 'friends':
    save('friends.txt',format_json(json_obj))


if __name__ == '__main__':

  if len(sys.argv) < 2:
    print('Usage: extract_uff.py <prefs.js|greasemonkey-prefs.uff.js>')
    exit(2)


  fd = open(sys.argv[1], "r", encoding='utf-8')

  for line in fd:
    eline = line
    if re.search('extensions.greasemonkey.scriptvals.unfriend_finder',eline):
      eval(eline.strip().split(';')[0])
      
