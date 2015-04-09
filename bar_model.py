import lib

from google.appengine.ext import ndb


class Bar(ndb.Model):
	id = ndb.StringProperty()
	name = ndb.StringProperty()
	teams = ndb.StringProperty(repeated=True)
	address = ndb.StringProperty()
	city = ndb.StringProperty()


def insert(name, team_list, address, city):
	# First sanitize input.
	name = lib.sanitize(name)
	address = lib.sanitize(address)
	city = lib.sanitize(city)
	teams = [lib.sanitize(t) for t in team_list]

	# Create new bar or append new teams to old bar.
	# this should be synchronous.
	bar = Bar.query(ndb.AND(Bar.name == name, Bar.city == city)).fetch()
	if not bar:
		bar = Bar(name=name, teams=teams, address=address, city=city)
	else:
		bar = bar[0]
		bar.teams = list(set(teams) | set(bar.teams))
	bar.put()

def search(val, city):
	if city:
			bars = Bar.query(
				ndb.AND(
					ndb.OR(Bar.name == vsl, Bar.teams == val),
					Bar.city == city)
			).fetch()
	else:
		bars = Bar.query(
			ndb.OR(Bar.name == val, Bar.teams == val)
		).fetch()
	return bars