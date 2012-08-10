from handlers import Handler
from google.appengine.api import memcache
from google.appengine.ext import db
from lib.db import BlogPost
import time, utils

def FrontPage(update = False):
	key = "front"
	blogs = memcache.get(key)
	if blogs is None or update:
		keytime = "front_time"
		blogs = db.GqlQuery("Select * from BlogPost Order By created DESC Limit 10")
		blogs = list(blogs)
		memcache.set(key, blogs)
		memcache.set(keytime, time.time())
	return blogs	

def PermaLinkPage(update = None, page_number=0):
	key = "page_"+ str(page_number)
	keytime = key +"_time"
	singlePost = memcache.get(key)
	if update:
		memcache.set(key, update)
		memcache.set(keytime, time.time())
	elif singlePost is None:
		singlePost = BlogPost.get_by_id(page_number)
		memcache.set(key, singlePost)
		memcache.set(keytime, time.time())
	return singlePost

def getLastQueryTime(page_number = None):
	if page_number is None:
		a = memcache.get("front_time")
		if a is None:	
			return int(time.time())
		else:
			b = time.time()
			last = b-a		
			return int(last)
	else:
		key = "page_"+ str(page_number) +"_time"
		a = memcache.get(key)
		if a is None:	
			return int(time.time())
		else:
			b = time.time()
			last = b-a		
			return int(last)
			
class BlogHandler(Handler):
	def render_bloglist(self):
		blogs = FrontPage()
		points = filter(None, (b.coords for b in blogs))
		#find which arts have coords
		#if we have any arts coords, make an image url; display
		img_url = None
		if points:
			img_url = utils.gmaps_img(points)
		querytime = getLastQueryTime()
		self.render("bloglist.html", blogs = blogs, img_url=img_url, querytime= querytime)
	def get(self):	
		self.render_bloglist()
		
class BlogPermaLink(Handler):
	def render_perma(self, blogpost):
		if blogpost:
			blog = blogpost.blog
			title=blogpost.title
			date=blogpost.created
			querytime = getLastQueryTime(blogpost.key().id())
			self.render("singleblog.html", blog=blog, title=title, date=date, querytime=querytime)
	def get(self, blog_id):
		#s = BlogPost.get_by_id(int(blog_id))
		s = PermaLinkPage(page_number = int(blog_id))
		self.render_perma(blogpost=s)
		
class NewBlogHandler(Handler):
	def render_blog(self,error= "", title=""):
		self.render("blog.html", error=error, title=title)
	def get(self):
		self.render_blog()
	def post(self):
		title = self.request.get("subject")
		blog = self.request.get("content")
		if title and blog:
			coords = utils.get_coords(self.request.remote_addr)
			newBlog = BlogPost(title=title, blog=blog, coords=coords)
			newBlog.put()
			FrontPage(update=True)
			val = newBlog.key().id()
			PermaLinkPage(update=newBlog)
			self.redirect("/blog/"+str(val))
		else:
			error = "You need a title and blog entry!"
			self.render_blog(error=error,title=title)
