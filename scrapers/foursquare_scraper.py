import collections
import foursquare
import threading
import logging

import bar_model
import lib
import settings

SPORTS_BAR_CAT_ID = "4bf58dd8d48988d11d941735"

Bar = collections.namedtuple('Bar', 'id name address city')

LOCK = threading.Lock()
TEAMS_MAP = lib.BuildTeamsList(settings.TEAMS_FILE)

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

# used for sourcing surrounding bars
# @lib.memoized
def FindLocalBars(client, city=None, ll=None, existing_bar_map=None):
	# Get local bars from foursquare
	query_params = {'categoryId': SPORTS_BAR_CAT_ID, 'limit': 50}
	if city: query_params['near'] = city
	if ll: query_params['ll'] = ll
	bars = client.venues.search(params=query_params)
	logging.info('Inserting bars: %s\n', [b['name'] for b in bars['venues']])
	for b in bars['venues']:
		t = threading.Thread(
			target=InsertBar, args=(b, existing_bar_map, client))
		t.setDaemon(True)
		t.start()

def GetTeamsForBar(client, bar_name, ll=None, city=None):
	"""Query foursquare to verify that the bar returned from yelp is a sports bar."""
	query_params = {
			'query': bar_name, 'categoryId': SPORTS_BAR_CAT_ID, 'limit': 1}
	if city: query_params['near'] = city
	if ll: query_params['ll'] = ll
	logging.info('Querying foursquare for bar %s', bar_name)
	bars = client.venues.search(params=query_params)
	# We only queried for one bar that's all we should find, code is like this
	# in case we
	logging.info('Found bars in fsquare: %s\n', [b['name'] for b in bars['venues']])
	for b in bars['venues']:
		if lib.sanitize(b['name']) != bar_name: continue
		teams = _GetTeamsForBar(b, client)
		return teams, True
	return [], False


# Doesn't really work.
def FindLocalBarsWithTips(val, city=None, ll=None, existing_bar_map=None):
	client = foursquare.Foursquare(
			client_id=client_id, client_secret=client_secret)
	query_params = {'categoryId': SPORTS_BAR_CAT_ID, 'limit': 500, 'radius': 1000}
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





