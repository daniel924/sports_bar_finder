import lib

from google.appengine.ext import ndb

class Bar(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty()
	teams = ndb.StringProperty(repeated=True)
	address = ndb.StringProperty()
	city = ndb.StringProperty()
	lat = ndb.FloatProperty()
	lon = ndb.FloatProperty()
	display_name = ndb.StringProperty()


def insert(name, team_list, address, city, lat, lon):
	# First sanitize input.
	name = lib.sanitize(name)
	address = lib.sanitize(address)
	city = lib.sanitize(city)
	teams = [lib.sanitize(t) for t in team_list]

	# Create new bar or append new teams to old bar.
	bar = search(name, city=city)
	if not bar:
		bar = Bar(name=name.replace('\'', ''), teams=teams, 
							address=address, city=city, lat=lat, lon=lon, 
							display_name=name)
	else:
		bar = bar[0]
		bar.teams = list(set(teams) | set(bar.teams))
	bar.put()

def search(val, city=None, ll=None):
	# This should be used first, but right now I don't have a way
	# to query for a range of latitude / longitude 
	# if ll:
	# 	bars = Bar.query(
	# 			ndb.AND(
	# 				ndb.OR(Bar.name == val, Bar.teams == val),
	# 				Bar.ll == ll)
	# 		).fetch()
	# Strip ' from name for searching.
	val = val.replace('\'', '')
	if city:
		bars = Bar.query(
			ndb.AND(
				ndb.OR(Bar.name == val, Bar.teams == val),
				Bar.city == city)
		).fetch()
	else:
		bars = Bar.query(
				ndb.OR(Bar.name == val, Bar.teams == val)
		).fetch()
	return bars

def searchByLocation(city=None, ll=None):
	if city:
		return Bar.query(Bar.city == city).fetch()


