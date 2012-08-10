from handlers import Handler
from google.appengine.api import memcache
from google.appengine.ext import db
from lib.db import WikiPage, User
import time, utils

def memCacheWiki(wiki_url="", update= False):
	wiki_page = memcache.get(wiki_url)
	if update or wiki_page is None:
		wiki_cursor = WikiPage.gql("Where wiki_url = :wiki_url", wiki_url= wiki_url)
		if wiki_cursor.count() == 0:
			return ""
		elif wiki_cursor.count() == 1:
			wiki_page= wiki_cursor[0].wiki_page
			memcache.set(wiki_url, wiki_page)	
	return wiki_page

class WikiPageHandler(Handler):		
	def render_wiki(self,wiki_url=""):
		wiki = memCacheWiki(wiki_url)
		u = self.request.cookies.get('user', '')
		if wiki == '':
			
			#if u =='':
			#	self.redirect('/login/'+wiki_url)
		
			redirect = "/_edit"+wiki_url
			self.redirect(redirect)
		else:
			#self.response.out.write(u)
			self.render("wikipage.html", wiki_page = wiki, user = u, url = wiki_url)
	def get(self, wiki_url):
		self.render_wiki(str(wiki_url))
		
class WikiFormHandler(Handler):
	def render_wiki(self,wiki_url="", saved_text="", user=""):
		self.render("wikiform.html", saved_text = saved_text, url =wiki_url, user = user)
	def get(self, wiki_url):
		
		#check if logged in
		u = self.request.cookies.get('user', '')
		if u =='':
			self.redirect('/login'+wiki_url)
		else:
			wiki = memCacheWiki(wiki_url)
			self.render_wiki(saved_text = wiki, wiki_url = wiki_url, user = u)
	def post(self, wiki_url):
		#url = wiki_url
		wiki = self.request.get("content")
		
		u = self.request.cookies.get('user', '')
		if u =='':
			self.redirect('/login'+wiki_url)
		else:
			logged_user = User.get_by_key_name(u)
		if wiki:
			wp = WikiPage(key_name = wiki_url, wiki_url=wiki_url, wiki_page=wiki, user_edit = logged_user)
			wp.put()
			memCacheWiki(wiki_url=wiki_url, update=True)
			self.redirect(wiki_url)
