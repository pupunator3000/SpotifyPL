from django.test import TestCase
#!/usr/bin/env python3
import spotipy
import re
from time import strftime
from datetime import date
from spotipy.oauth2 import SpotifyOAuth

# Create your tests here.
sp = spotipy.util.prompt_for_user_token()
print(sp)