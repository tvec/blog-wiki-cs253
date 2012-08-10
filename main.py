#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import re
import cgi
import random
import utils
import blog
import asciichan
import wiki
from lib.db import User
from handlers import Handler

from google.appengine.ext import db
            
class SignupHandler(Handler):
    def render_signup(self, uname="", email = "", uname_err="",pw_err="",vpw_err="",email_err=""):
        self.render("signup.html", uname=uname, email=email, uname_err=uname_err, pw_err = pw_err, vpw_err=vpw_err, email_err=email_err)
    def get(self):
        self.render_signup()
    def post(self):
        user_username = self.request.get("username")
        user_password = self.request.get("password")
        user_verify = self.request.get("verify")
        user_email = self.request.get("email")
        
        uname = user_username
        email = user_email
        
        uname_err = utils.check_username(user_username)
        pw_err=""
        vpw_err=""
        email_err=""
        
        Success= True
        
        if uname_err != "":
            Success= False
            
        if utils.check_password(user_password)==False:
            pw_err="That's not a valid password."
            Success= False
        
        if utils.verify_password(user_password, user_verify)==False:
            vpw_err="Your passwords didn't match."
            Success= False
        if len(email) != 0:
            if utils.check_email(user_email)==False:
                email_err="That's not a valid email."
                Success= False
        
        if Success:
            x = utils.make_pw_hash(uname, user_password)
            saltedPass = x.split("|")[0]
            salt = x.split("|")[1]
            
            if len(email) != 0:
                newUser = User(key_name = uname, username = uname, email=email, password = saltedPass, salt = salt)
            else:
                newUser = User(key_name = uname, username = uname, password = saltedPass, salt = salt)
            newUser.put()
            setUser = "user=" + uname
            self.response.headers.add_header('Set-Cookie', setUser.encode())
            self.redirect("/")
        else:
            self.render_signup(uname, email,uname_err, pw_err, vpw_err,email_err)

class LoginHandler(Handler):
    def render_login(self, error=""):
        self.render("login.html", invalid=error)
    def get(self, redirect_url=""):
        if redirect_url is None:
            redirect_url = "/welcome"
        u = self.request.cookies.get('user', '')
        if u == '':
            self.render_login()
        else:
            self.render_login()
    def post(self, redirect_url="/"):
        user_username = self.request.get("username")
        user_password = self.request.get("password")
        
        res = db.Query(User).filter("username =",user_username).get()
        
        if res == None:
            err="Invalid Login"
            self.render_login(error=err)
        else:
            password = res.password
            salt = res.salt
            verify = password +"|"+salt
            
            if utils.valid_pw(user_username, user_password, verify):
                setUser = "user=" + user_username+"; Path=/"
                self.response.headers.add_header('Set-Cookie', setUser.encode())
                self.redirect(redirect_url)
            else:
                err="Invalid Login"
                self.render_login(error=err)

class LogoutHandler(Handler):
    def get(self, url=""):
        setUser = "user="
        self.response.headers.add_header('Set-Cookie', 'user=; Path=/')
        if url:
            self.redirect(url)
        else:
            self.redirect(url)              

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        u = self.request.cookies.get('user', '')
        if u == "":
            self.redirect("/signup")
        else:
            self.response.out.write("Welcome, "+u+"!")

class TestHandler(webapp2.RequestHandler):
    def get(self):
        q = self.request.get("username")
        self.response.out.write(q)
        
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request)

#Convert blog(s) to json
class JSONHandler(webapp2.RequestHandler):
    def get(self, blog_id=""):
        self.response.headers['Content-Type'] = 'application/json'
        if blog_id=="":
            blogs = db.GqlQuery("Select * from BlogPost Order By created DESC Limit 10")
            blogs = list(blogs)
            a= list()
            for content in blogs:
                b=dict()
                b["content"] = content.blog
                b["subject"] = content.title
                a.append(b)  
            x = json.dumps(a)
            self.response.out.write(x)
        else:
            singleblog = BlogPost.get_by_id(int(blog_id))
            b=dict()
            b["content"] = singleblog.blog
            b["subject"] = singleblog.title
            x = json.dumps([b]) 
            self.response.out.write(x)

class WikiHandler(Handler):
    def get(self):
        self.render("wikimain.html")
        
class FlushCache(Handler):
    def get(self):
        memcache.flush_all()
        self.redirect('/')
        

# BLOG being implemented       
app = webapp2.WSGIApplication([
('/', blog.BlogHandler),
('/blog.json', JSONHandler),
('/blog/(\d+).json', JSONHandler),
('/blog', blog.BlogHandler),
('/blog/(\d+)', blog.BlogPermaLink),
('/newpost', blog.NewBlogHandler),
('/.json', JSONHandler),

('/login', LoginHandler),
('/logout', LogoutHandler),
('/signup', SignupHandler),
('/flush', FlushCache),
('/testform', TestHandler),
('/welcome', WelcomeHandler)],
debug=True)

#WIKI
#PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
#('/', WikiHandler),
#('/_edit'+PAGE_RE, wiki.WikiFormHandler),
#(PAGE_RE, wiki.WikiPageHandler),
#('/login'+PAGE_RE, LoginHandler),
#('/logout'+PAGE_RE, LogoutHandler),

#ASCIICHAN
#('/', asciichan.MainHandler)
