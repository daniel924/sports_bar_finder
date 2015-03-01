import json
import webapp2

from google.appengine.ext import ndb

class Address(ndb.Model):
	address = ndb.StringProperty()
	city = ndb.StringProperty()

class Bar(ndb.Model):
	name = ndb.StringProperty()
	teams = ndb.StringProperty(repeated=True)
	address = ndb.StringProperty()
	city = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class SearchHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		search_val = self.request.get("value").lower()
		city = self.request.get("city").lower()
		bars = []
		if city:
			bars = Bar.query(
				ndb.AND(
					ndb.OR(Bar.name == search_val, Bar.teams == search_val),
					Bar.city == city)
				).fetch()
		else:
			bars = Bar.query(
				ndb.OR(
					Bar.name == search_val, 
					Bar.teams == search_val)
				).fetch()
		if not bars:
			self.response.out.write('')
			return

		bars_json = []
		for bar in bars:
			bars_json.append({
				'name': bar.name.title(),
				'teams': [t.title() for t in bar.teams],
				'city': bar.city.title(),
				'address': bar.address.title()})
		self.response.out.write(json.dumps(bars_json))


class Populate(webapp2.RequestHandler):
	def get(self):
		name = self.request.get("bar").lower().lstrip().rstrip()
		teams_str = self.request.get("teams")
		address = self.request.get("address").lower().lstrip().rstrip()
		city = self.request.get("city").lower().lstrip().rstrip()

		# Do not add the same bar twice.
		bar = Bar.query(ndb.AND(Bar.name == name, Bar.city == city)).fetch()
		teams = []
		for team in teams_str.split(','):
			if team and team.lstrip().rstrip():
				teams.append(team.lower().lstrip().rstrip())
		if not bar:
			bar = Bar(name=name, teams=teams, address=address, city=city)
		else:
			bar = bar[0]
			bar.teams = list(set(teams) | set(bar.teams))
		bar.put()


class Reset(webapp2.RequestHandler):
	def get(self):
		bars = Bar.query().fetch()
		ndb.delete_multi([bar.key for bar in bars])


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/search', SearchHandler),
    ('/populate', Populate),
    ('/reset', Reset),
], debug=True)
