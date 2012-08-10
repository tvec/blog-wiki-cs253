from google.appengine.api import memcache
from xml.dom import minidom
import string
import urllib2
import json
import hashlib
import re
import random
from google.appengine.ext import db
from lib.db import User

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s|%s' % (h, salt)

def valid_pw(name, pw, h):
	salt = h.split("|")[1]
	return h==make_pw_hash(name,pw,salt)
def ROT(s):
	return s.encode('rot13')
def check_email(email):
	USER_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
	valid = USER_RE.match(email)
	if valid:
		return True
	else:
		return False

def check_password(password):
	USER_RE = re.compile(r"^.{3,20}$")
	valid = USER_RE.match(password)
	if valid:
		return True
	else:
		return False
				
def verify_password(pw1, pw2):
	if pw1 == pw2:
		return True
	else:
		return False
			
def check_username(username):
	res = db.Query(User).filter("username =",username).count()
	err=""
	if res==1:
		err = "This user already exists"
		
	USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
	valid = USER_RE.match(username)
	
	if valid:
		return err
	else:
		err = "That's not a valid username."
		return err
		
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"

def gmaps_img(points):
	markers = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
	return GMAPS_URL + markers
	
IP_URL = "http://api.hostip.info/?ip="
def get_coords(ip):
	url = IP_URL+ip
	content = None
	try:
		content = urllib2.urlopen(url).read()
	except URLError:
		return
	if content:
		d = minidom.parseString(content)
		coords = d.getElementsByTagName("gml:coordinates")
		if coords and coords[0].childNodes[0].nodeValue:
			lon, lat = coords[0].childNodes[0].nodeValue.split(",")
			return db.GeoPt(lat, lon)
