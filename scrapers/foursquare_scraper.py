import collections
import foursquare
import threading
import logging

import bar_model
import lib
import settings

SPORTS_BAR_CAT_ID = "4bf58dd8d48988d11d941735"
NIGHTLIFE_SPOT_CAT = "4d4b7105d754a06376d81259"

Bar = collections.namedtuple('Bar', 'id name address city')

LOCK = threading.Lock()
TEAMS_MAP = lib.BuildTeamsList(settings.TEAMS_FILE)


def GetAddress(venue):
	return lib.sanitize(venue['location'].get('address'))

def GetCity(venue):
	return lib.sanitize(venue['location'].get('city'))	

def GetLat(venue):
	return venue['location'].get('lat')

def GetLon(venue):
	return venue['location'].get('lng')


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


def GetBar(client, bar_name, ll=None, city=None):
	# We just use nightlife spot here as foursquare bar categorizations are not
	# always that accurate and we are just verifying this is a bar anyway.
	query_params = {
			'query': bar_name, 'categoryId': NIGHTLIFE_SPOT_CAT, 'limit': 3}
	if city: query_params['near'] = city
	if ll: query_params['ll'] = ll
	logging.info('Querying foursquare for bar %s', bar_name)
	bars = client.venues.search(params=query_params)
	# We only queried for one bar that's all we should find, code is like this
	# in case we
	logging.info('Found bars in fsquare: %s\n', [b['name'] for b in bars['venues']])
	for b in bars['venues']:
		if lib.normalize(b['name']) != lib.normalize(bar_name): continue
		teams = _GetTeamsForBar(b, client)
		bar = bar_model.Bar(
			name=b['name'], teams=teams, address=GetAddress(b), city=GetCity(b), 
			lat=GetLat(b), lon=GetLon(b))
		return bar, True
	return None, False


def GetTeamsForBar(client, bar_name, ll=None, city=None):
	"""Query foursquare to verify that the bar returned from yelp is a sports bar."""
	bar, is_bar = GetBar(client, bar_name, ll, city)
	if bar:
		return bar.teams, is_bar
	else:
		return [], is_bar


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





