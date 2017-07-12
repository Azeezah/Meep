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
import jinja2
import os
import webapp2
import logging

from google.appengine.ext import ndb

list_of_students = []

jinja_environment = jinja2.Environment(
	loader=jinja2.FileSystemLoader(
		os.path.dirname(__file__)))

class User(ndb.Model):
	username = ndb.StringProperty()

class Post(ndb.Model):
	poster = ndb.StringProperty()
	text = ndb.StringProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class FeedHandler(webapp2.RequestHandler):
	def get(self):
		posts = Post.query().fetch(limit=10)
		template = jinja_environment.get_template('feed.html')
		self.response.write(template.render({'posts':posts}))

class WriteHandler(webapp2.RequestHandler): #redirect to feed
	def get(self):
		self.response.write(jinja_environment.get_template('write.html').render())

	def post(self):
		username = self.request.get('username')  #must be verified
		text = self.request.get('text')[:140:] #limits to 140 chars
		logging.debug(username + ' ' + text)
		new_post = Post(text=text, poster=username)
		new_post.put()
		posts = Post.query().fetch(limit=10)  #order by timestamp
		template = jinja_environment.get_template('feed.html')
		self.response.write(template.render({'posts':posts}))

class DeleteHandler(webapp2.RequestHandler):
	def post(self):
		post_id = self.request.get('post_id')
		Post.get_by_id(int(post_id)).delete()
		posts = Post.query().fetch(limit=10)  #order by timestamp
		template = jinja_environment.get_template('feed.html')
		self.response.write(template.render({'posts':posts}))

class ViewHandler(webapp2.RequestHandler):
	def get(self):
		post_id = self.request.get('post_id')
		post = Post.get_by_id(int(post_id))
		template = jinja_environment.get_template('view.html')
		self.response.write(template.render({'post':post}))

app = webapp2.WSGIApplication([
    ('/', FeedHandler),
    ('/view', ViewHandler),
    ('/write', WriteHandler),
    ('/delete', DeleteHandler)

], debug=True)
