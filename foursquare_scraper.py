import collections
import foursquare
import threading

import bar_model
import lib


Bar = collections.namedtuple('Bar', 'id name address city')

client_id = "2OMJJJOIFVW3HOEKXZIQE3KKG0YUB3WRLIJ5JWUL2ARUIVPM"
client_secret = "UYYGDFZQCRCELF1WCCQ5AHZZ4VBYOIXY3LJGL0T3ZHJXH5B3"
sports_bar_cat_id = "4bf58dd8d48988d11d941735"

def BuildTeamsList():
	teams = {}
	f = open('teams.txt')
	for line in f:
		split = line.split(',')
		city = split[0].lstrip().rstrip().lower()
		team = split[1].lstrip().rstrip().lower()
		full_team_name = city + ' ' + team
		teams[full_team_name] = full_team_name
		teams[team] = full_team_name
	return teams

TEAMS_MAP = BuildTeamsList()

def InsertBar(b, existing_bar_map, client):
	try:
		name = lib.sanitize(str(b['name']))	
	except TypeError as e:
		print e
		return
	print name
	address = lib.sanitize(b['location'].get('address'))
	city = lib.sanitize(b['location'].get('city'))
	# Skip if they are already in the DB.
	if (existing_bar_map and 
		name in existing_bar_map and 
		existing_bar_map[name].city == city and 
		existing_bar_map[name].address == address):
			return None
	# Thoughts to improve speed:
	# 0. problem is multiple get calls and this doesnt work async
	# 1. Bulk query venues - THREADING
	# 3. make TEAMS_MAP keys into a set and intersect for diff
	# 4. query tips in the first place, this might help to get 
	#    query specific team data as opposed to random area
	# 5. migrate to simplejson library
	teams = set()
	for tag in client.venues(b['id'])['venue']['tags']:
		if tag in TEAMS_MAP: 
			teams.add(TEAMS_MAP[tag])
	bar_model.insert(name, teams, address, city)

def FindLocalBars(city=None, ll=None, existing_bar_map=None):
	# Get local bars from foursquare
	client = foursquare.Foursquare(
		client_id=client_id, client_secret=client_secret)
	query_params = {'categoryId': sports_bar_cat_id, 'limit': 10}
	if city: query_params['near'] = city
	if ll: query_params['ll'] = ll
	bars = client.venues.search(params=query_params)
	print [b['name'] for b in bars['venues']]

	for b in bars['venues']:
		InsertBar(b, existing_bar_map, client)


def FindLocalBarsWithTips(city=None, ll=None):
	pass
