from google.appengine.ext import db
	
class Art(db.Model):
	title = db.StringProperty(required = True)
	art = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add=True)	
	coords = db.GeoPtProperty()
	
class User(db.Model):
	username = db.StringProperty(required=True)
	password = db.StringProperty(required=True)
	salt = db.StringProperty()
	email = db.EmailProperty()

class BlogPost(db.Model):
	title = db.StringProperty(required=True)
	blog = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add= True)
	coords = db.GeoPtProperty()
	user = db.ReferenceProperty(User)

class WikiPage(db.Model):
	wiki_url = db.StringProperty(required = True)
	wiki_page = db.TextProperty(required=True) 
	user_edit = db.ReferenceProperty(User)
	#created = db.DateTimeProperty(auto_now_add= True)
	last_edit_time = db.DateTimeProperty(auto_now_add= True)
