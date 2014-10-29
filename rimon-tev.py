import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENV = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'],
    autoescape = True)

# Creates an entity key based on the attorney currently logged in. 
def attorney_answers_key(attorney):
    return ndb.Key('Attorney', attorney)

# Models an individual answer.
class Answer(ndb.Model):
    attorney = ndb.UserProperty()
    answer = ndb.StringProperty(indexed = False)
    timestamp = ndb.DateTimeProperty(auto_now_add = True)
    date = ndb.DateProperty(auto_now_add = True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        current_attorney = users.get_current_user()
 
        # Checks to see if the current user is an admin. If so it will request the 
        # lookup_attorney value save it into a variable to pass into the query.
        lookup_attorney = self.request.get('lookup_attorney', current_attorney.nickname())

        # Create the datastore query based on the attorney_answers_key and sort them
        # according to their timestamp.
        answers_query = Answer.query(
            ancestor = attorney_answers_key(lookup_attorney)).order(-Answer.timestamp)
        answers = answers_query.fetch(12)

        # Create a logout url of the user.
        url = users.create_logout_url('/')
        url_linktext = 'Logout'

        # Create the dictionary with the values to pass to our template.
        template_values = {
		'answers': answers,
		'currently_viewing_attorney': lookup_attorney,
		'admin': users.is_current_user_admin(),
		'url': url,
		'url_linktext': url_linktext,
	}

        template = JINJA_ENV.get_template('index.html')
        self.response.write(template.render(template_values))

class AttorneyAnswers(webapp2.RequestHandler):
    def post(self):
        # Again check to see if the user signed in is an admin. If so get the value
        # of the lookup_attorney entry from the html template.
        current_attorney = users.get_current_user()
        
        lookup_attorney = self.request.get('lookup_attorney', current_attorney.nickname())

        answer = Answer(parent = attorney_answers_key(current_attorney.nickname()))

        answer.attorney = users.get_current_user()
        answer.answer = self.request.get('answer')
        answer.put()

        query_params = {'lookup_attorney': lookup_attorney}
        self.redirect('/main?' + urllib.urlencode(query_params))
        
class AttorneyLogin(webapp2.RequestHandler):
    def get(self):
        self.redirect(users.create_login_url('/main'))
    
application = webapp2.WSGIApplication([
    ('/', AttorneyLogin),
    ('/main', MainPage),
    ('/answers', AttorneyAnswers),
], debug = True)











