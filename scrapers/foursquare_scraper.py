import collections
import foursquare
import threading
import logging

import bar_model
import lib


Bar = collections.namedtuple('Bar', 'id name address city')

client_id = "2OMJJJOIFVW3HOEKXZIQE3KKG0YUB3WRLIJ5JWUL2ARUIVPM"
client_secret = "UYYGDFZQCRCELF1WCCQ5AHZZ4VBYOIXY3LJGL0T3ZHJXH5B3"
sports_bar_cat_id = "4bf58dd8d48988d11d941735"

LOCK = threading.Lock()
TEAMS_MAP = lib.BuildTeamsList(lib.TEAMS_FILE)

def _GetTeamsForBar(bar, client):
	teams = set()
	for tag in client.venues(bar['id'])['venue']['tags']:
		if tag in TEAMS_MAP: 
			teams.add(TEAMS_MAP[tag])
	return teams

def InsertBar(b, existing_bar_map, client):
	try:
		name = lib.sanitize(str(b['name']))	
	except TypeError as e:
		logging.warn('%s\n%s', name, e)
		return
	address = lib.sanitize(b['location'].get('address'))
	city = lib.sanitize(b['location'].get('city'))
	# Skip if they are already in the DB.
	if (existing_bar_map and 
		name in existing_bar_map and 
		existing_bar_map[name].city == city and 
		existing_bar_map[name].address == address):
			return 
	print name
	teams = _GetTeamsForBar(b, client)
	with LOCK:		
		bar_model.insert(name, teams, address, city)

# @lib.memoized
def FindLocalBars(city=None, ll=None, existing_bar_map=None, client=None):
	# Get local bars from foursquare
	client = client or foursquare.Foursquare(
		client_id=client_id, client_secret=client_secret)
	query_params = {'categoryId': sports_bar_cat_id, 'limit': 50}
	if city: query_params['near'] = city
	if ll: query_params['ll'] = ll
	bars = client.venues.search(params=query_params)
	logging.info('Inserting bars: %s\n', [b['name'] for b in bars['venues']])
	for b in bars['venues']:
		t = threading.Thread(
			target=InsertBar, args=(b, existing_bar_map, client))
		t.setDaemon(True)
		t.start()

def GetTeamsForBar(bar_name, ll=None, city=None, existing_bar_map=None, client=None):
	client = client or foursquare.Foursquare(
		client_id=client_id, client_secret=client_secret)
	query_params = {
			'query': bar_name, 'categoryId': sports_bar_cat_id, 'limit': 3}
	if city: query_params['near'] = city
	if ll: query_params['ll'] = ll
	logging.info('Querying foursquare for bar %s', bar_name)
	bars = client.venues.search(params=query_params)
	logging.info('Found bars in fsquare: %s\n', [b['name'] for b in bars['venues']])
	for b in bars['venues']:
		if b['name'].lower() != bar_name.lower(): continue
		teams = _GetTeamsForBar(b, client)
		return teams
	return []


# Doesn't really work.
def FindLocalBarsWithTips(val, city=None, ll=None, existing_bar_map=None):
	client = foursquare.Foursquare(
			client_id=client_id, client_secret=client_secret)
	query_params = {'categoryId': sports_bar_cat_id, 'limit': 500, 'radius': 1000}
	if city: query_params['near'] = city
	if ll: query_params['ll'] = ll
	query_params['query'] = val
	tips = client.tips.search(params=query_params)

	print "Count: " + str(len(tips['tips']))
	for tip in tips['tips']:
		venue = tip['venue']
		print venue['name']
		for category in venue['categories']:
			if category['id'] == sports_bar_cat_id:
					import pdb; pdb.set_trace()
					x = 5
	x = 5





