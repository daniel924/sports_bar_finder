import collections
import logging
import json
import urllib
import urllib2

import oauth2

import bar_model
import lib
import settings

API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 3
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'


TEAMS_MAP = lib.BuildTeamsList(settings.TEAMS_FILE)

def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(settings.YELP_CONSUMER_KEY, settings.YELP_CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_settings.YELP_TOKEN': settings.YELP_TOKEN,
            'oauth_settings.YELP_CONSUMER_KEY': settings.YELP_CONSUMER_KEY
        }
    )
    token = oauth2.Token(settings.YELP_TOKEN, settings.YELP_TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print u'Querying {0} ...'.format(url)

    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, ll):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    
    url_params = {
        'term': term.replace(' ', '+'),
        'll': ll.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'category_filer': 'sportsbar'
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def FindBarByLocation(val, ll=None, city=None):
  logging.info('Querying yelp')
  bizes = search(val, ll)['businesses']
  bars = []
  for b in bizes:
    address = b['location']['address'][0]
    city = b['location']['city']
    bars.append(bar_model.Bar(
        name=lib.sanitize(b['name']), address=address, city=city, 
        lat=b['location']['coordinate']['latitude'],
        lon=b['location']['coordinate']['longitude'])) 
  bar_names = [bar.name for bar in bars]
  logging.info('Bars found from yelp: %s', bar_names)
  return bars



