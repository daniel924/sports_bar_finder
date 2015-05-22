import collections
import json
import logging
import os
import threading
import time
import webapp2
import sys

import bar_model
import foursquare
import foursquare_scraper
import yelp_scraper
import lib
import settings

from google.appengine.ext import ndb


# Things to do.
# 1. Tests
# 3. Authorization
# 4. Add pow to app
# 		b. restrict user insertion?
# 5. Stop app from crashing on load
# 6. Load data in background
# 	a. maybe on app startuo load nearby bars
# 7. Maybe do a sweet loading bar - DONE
# 9. Figure out best way to structure files - DONE
# 10. Think about bars with different addresses, etc.
# 11. migrate to simplejson
# 14. use longitude / latitude to query nearby
#			a. convert this to city?
#			b. can android send city data?
#			c. pick basic radius and search ll
# 16. bars with apostrophy s are tricky, possibly check for them
# 17. in app, lat + lon is ignored at -1, -1
# 18. fix capitalization issues after ' and numbers 
#			a. just insert display name as whatever yelp said and don't capitilize
# 19. be careful with & vs ampersand - DONE
# 20. bars don't always have same name e.g. stone creek vs. stone creek bar and lounge
# 21. sometimes queries from yelp return multiple bars
# 22. lookup bar name with just city? 
# 23. do a one off batch query with all teams in teams list to prepopulate apps
# 24. have insert but do validation on it
# 25. listview map button moves off screen when bar name is long
# 26. listview just looks shitty in general
# 27. refactor foursquare scraper to be an object, and main will not create a 
#     new foursquare scraper every time. same for yelp.
# 28. Move scraper credentials to config
# 29. android - if there is already a bar showing, a new search doesn't clear it


FOURSQUARE_CLIENT = None

class Address(ndb.Model):
	address = ndb.StringProperty()
	city = ndb.StringProperty()


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello, World!')


def PushLocalBars(ll):
	bars = bar_model.searchByLocation('new york')
	existing_bar_map = {bar.name: bar for bar in bars}
	t = threading.Thread(
			target=foursquare_scraper.FindLocalBars,
			args=[FOURSQUARE_CLIENT], 
			kwargs={"ll": ll, "existing_bar_map": existing_bar_map})
	t.setDaemon(True)
	t.start()

class SearchHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers['Content-Type'] = 'application/json'
		search_val = lib.sanitize(self.request.get('value'))
		city = lib.sanitize(self.request.get('city'))
		ll = lib.sanitize(self.request.get('ll'))

		logging.info('Searching for %s where city=%s, ll=%s',
									search_val, city, ll)
		bars_json = collections.defaultdict(list) # Will load bars here.
		bars = bar_model.search(search_val, city)
		# Bar is in our database.
		if bars:
			logging.info('Found bars in local db')
			for bar in bars: 
				bars_json['bars'].append(lib.BarToJson(bar))
			self.response.out.write(json.dumps(bars_json))
		
		# Bar is not in our db; try to find it.
		else:	
			logging.info('Bar not in local db.')
			if not ll and not city: 
				logging.info('No location given; terminating')
				self.response.out.write('')
				return

			# First, get bars from yelp. These don't have teams.
			bars = yelp_scraper.FindBarByLocation(search_val, ll)
			if not bars:
				logging.info('No bars found in yelp; terminating')
				self.response.out.write('')
				return
	
			new_bars_found = []
			for bar in bars:
				# Next, validate these are bars and populate teams by 
				# getting the tags from foursquare.
				teams, is_bar = foursquare_scraper.GetTeamsForBar(FOURSQUARE_CLIENT, bar.name, ll=ll)
				if not is_bar: 
					logging.info('Bar %s not found in foursquare.', bar.name)
					continue
				if not teams:
					logging.info('Bar %s found but had no teams from foursquare', bar.name)
					# Foursquare often does not have tag data, so if the value submitted was
					# a team, then just return the yelp bar anyway.
					teams_map = lib.BuildTeamsList(settings.TEAMS_FILE)
					if search_val in teams_map: teams = [teams_map[search_val]]
				logging.info('Teams found for bar %s', bar.name)
				bar.teams = teams
				new_bars_found.append(bar)
				bars_json['bars'].append(lib.BarToJson(bar))
			self.response.out.write(json.dumps(bars_json))
			
			# TODO(ladenheim): Figure out why this doesn't run in the background aka why
			# it doesn't return and then spawn the task
			# Response has been given, now insert bar.
			for bar in new_bars_found:
				logging.info('Inserting bar %s to local DB', bar.name)
				bar_model.insert(
						bar.name, bar.teams, bar.address, bar.city, bar.lat, bar.lon)
			# if ll: PushLocalBars(ll)


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
		self.response.out.write('Database reset')


class Pow(webapp2.RequestHandler):
	def get(self):
		start = time.time()
		# bars = bar_model.searchByLocation('new york')
		# existing_bar_map = {bar.name: bar for bar in bars}
		# foursquare_scraper.FindLocalBars(
		#	 city='new york', existing_bar_map=existing_bar_map)
	 	# foursquare_scraper.FindLocalBars(
		#		ll="40.712,-74.005", existing_bar_map=existing_bar_map)
		# val = self.request.get("val")
		# foursquare_scraper.FindLocalBarsWithTips(
		# 		val, ll="40.7,-74", existing_bar_map=existing_bar_map)
		bars = yelp_scraper.FindBarByLocation('dallas cowboys', ll='40.7,-74')
		print "\n\n\nTime: " + str((time.time() - start)) + "\n\n\n"


def fix_path():
	sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
	sys.path.append(os.path.join(os.path.dirname(__file__), 'scrapers'))

FOURSQUARE_CLIENT = foursquare.Foursquare(
		client_id=settings.FOURSQUARE_CLIENT_ID, 
		client_secret=settings.FOURSQUARE_CLIENT_SECRET)
fix_path()
application = webapp2.WSGIApplication([
		('/', MainPage),
  	('/search', SearchHandler),
  	('/insert', Insert),
    ('/reset', Reset),
   	('/pow', Pow),
], debug=True)




