import collections
import json
import time
import webapp2

import foursquare_scraper
import lib
import bar_model

from google.appengine.ext import ndb


class Address(ndb.Model):
	address = ndb.StringProperty()
	city = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


class SearchHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/plain'
		search_val = lib.sanitize(self.request.get("value"))
		city = lib.sanitize(self.request.get("city"))
		bars = bar_model.search(search_val, city)
		if not bars:
			self.response.out.write('')
			return
		bars_json = collections.defaultdict(list)
		for bar in bars:
			bars_json['bars'].append({
				'name': bar.name.title(),
				'teams': [t.title() for t in bar.teams],
				'city': bar.city.title(),
				'address': bar.address.title()})
		self.response.out.write(json.dumps(bars_json))


class Insert(webapp2.RequestHandler):
	def get(self):
		name = self.request.get("bar")
		team_list = self.request.get("teams").split(',')
		address = self.request.get("address")
		city = self.request.get("city")

		bar_model.insert(name, team_list, address, city)


class Reset(webapp2.RequestHandler):
	def get(self):
		bars = bar_model.Bar.query().fetch()
		ndb.delete_multi([bar.key for bar in bars])

class Pow(webapp2.RequestHandler):
	def get(self):
		start = time.time()
		bars = Bar.query(Bar.city == 'new york').fetch()
		existing_bar_map = {bar.name: bar for bar in bars}
		local_bars = foursquare_scraper.FindLocalBars(
			city='new york', existing_bar_map=existing_bar_map)
		for name, teams, address, city in local_bars:
			insert(name, teams, address, city)

		print "\n\n\nTime: " + str((time.time() - start)) + "\n\n\n"



application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/search', SearchHandler),
    ('/insert', Insert),
    ('/reset', Reset),
    ('/pow', Pow),
], debug=True)
