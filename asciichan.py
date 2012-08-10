from handlers import Handler
from google.appengine.api import memcache
from google.appengine.ext import db
from lib.db import Art
import utils

class MainHandler(Handler):
	def render_front(self, title="", art="", error=""):
		arts = db.GqlQuery("Select * from Art Order By created DESC Limit 10")
		
		arts = list(arts)
		points = filter(None, (a.coords for a in arts))
		
		#find which arts have coords
		#if we have any arts coords, make an image url; display
		img_url = None
		if points:
			img_url = utils.gmaps_img(points)
		self.render("front.html", title=title, art=art, error=error, arts=arts, img_url=img_url)
	def get(self):
		self.render_front()
	def post(self):
		title=self.request.get("title")
		art=self.request.get("art")
		if title and art:
			coords = utils.get_coords(self.request.remote_addr)
			a = Art(title= title, art = art)
			if coords:
				a.coords = coords
			a.put()
			self.redirect("/")
		else:
			error = "we need both a title and some artwork!"
			self.render_front(title,art, error=error)
