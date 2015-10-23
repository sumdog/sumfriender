sumfriender
===========

Sumfriender is a script designed to query a user's Facebook friend list and detect when friends
have been removed or deactivated.

Update
======
**As of May 1, 2015, this script no longer works. Facebook changed their API so apps could only list friends who used the same app. They added _taggable friends_ to their API, but my attempts to use it inplace of the current implementation have failed.**

Usage
=====

You will need to create a Facebook application with an API key and secret. You will also need to 
place the fb_token.html on a web server somewhere and set the URL to that file in your Facebook
app's Valid OAuth redirect URIs (in the Advanced section). 

Once you have the API keys setup, run `sumfriends.py` and a web browser will be opened to request
your OAuth token. Once you approve the request, store that OAuth token in the configuration file.

Subsequent calls to `sumfriends.py` will append the `friends.txt` and `status.txt` with your 
friends lists and changes to that list respectively. The data written to `status.txt` will
be sent to standard out as well. If no changes occur, there will be no output. 

You can combine sumfriender with an e-mail script to e-mail you notifications on changes:

http://penguindreams.org/scripts/rubyemailscript/
