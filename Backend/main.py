import webapp2
from google.appengine.ext import ndb

class Bar(ndb.Model):
	name = ndb.StringProperty()
	teams = ndb.StringProperty(repeated=True)


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class SearchHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		search_val = self.request.get("value")
		bars = Bar.query(
			ndb.OR(Bar.name == search_val, Bar.teams == search_val)
			).fetch()
		# import pdb; pdb.set_trace()
		if not bars:
			self.response.out.write("Could not find results for: " + search_val)
			return
		for bar in bars:
			info = bar.name + ": " + ' '.join(bar.teams).rstrip(' ')
			self.response.out.write(info)
			bar
			#	self.response.headers['Content-Type'] = 'application/json'
		# 	self.response.out.write(json.dumps{'sdf':"sfdsd"})

class Populate(webapp2.RequestHandler):
	def get(self):
		bar_name = self.request.get("bar")
		bar_teams = self.request.get("teams")
		bar = Bar(name=bar_name,
				   teams=bar_teams.split(','))
		bar.put()

class Reset(webapp2.RequestHandler):
	def get(self):
		bars = Bar.query().fetch()
		for bar in bars:
			bar.key.delete()


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/search', SearchHandler),
    ('/populate', Populate),
    ('/reset', Reset),
], debug=True)
