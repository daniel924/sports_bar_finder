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
		search_val = self.request.get("value").lower()
		bars = Bar.query(
			ndb.OR(Bar.name == search_val, Bar.teams == search_val)
			).fetch()
		if not bars:
			self.response.out.write("Could not find results for: " + search_val)
			return
		for bar in bars:
			info = bar.name.title() + ":" 
			info += ','.join(bar.teams).title()
			self.response.out.write(info)


class Populate(webapp2.RequestHandler):
	def get(self):
		bar_name = self.request.get("bar").lower().lstrip().rstrip()
		bar_teams = self.request.get("teams")
		# Do not add the same bar twice.
		bar = Bar.query(Bar.name == bar_name).fetch()
		teams = []
		for team in bar_teams.split(','):
			if team and team.lstrip().rstrip():
				teams.append(team.lower().lstrip().rstrip())
		if not bar:
			bar = Bar(name=bar_name, teams=teams)
		else:
			bar = bar[0]
			bar.teams = list(set(teams) | set(bar.teams))
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
