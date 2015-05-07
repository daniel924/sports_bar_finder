import unittest
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

import bar_model
import lib

class LibTests(unittest.TestCase):

  def setUp(self):
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    # Next, declare which service stubs you want to use.
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def testBuildTeamsList(self):
    tmap = lib.BuildTeamsList(lib.TEAMS_FILE)
    self.assertEqual('new york yankees', tmap['new york yankees'])
    self.assertEqual('new york yankees', tmap['yankees'])
    self.assertEqual('boston red sox', tmap['red sox'])
    self.assertEqual('arizona coyotes', tmap['coyotes'])
    self.assertIsNone(tmap.get('boston'))

  def testBuildBackwardsTeamsList(self):
    tmap = lib.BuildBackwardsTeamsList(lib.TEAMS_FILE)
    self.assertEqual('yankees', tmap['new york yankees'])
    self.assertEqual('red sox', tmap['boston red sox'])
    self.assertEqual('coyotes', tmap['arizona coyotes'])
    self.assertIsNone(tmap.get('boston'))

  def testSanitize(self):
    s1 = lib.sanitize(None)
    self.assertEqual('', s1)
    s2 = lib.sanitize('   sAsBerYla       ')
    self.assertEqual('sasberyla', s2)

  def testBarToJson(self):
    bar = bar_model.Bar(
      name='b', teams=['pa', 'po'], city='philly', 
      address='42 wallaby way', display_name='bonkers')
    bar_json = lib.BarToJson(bar)
    self.assertEqual('Bonkers', bar_json['name'])
    self.assertEqual(['Pa', 'Po'], bar_json['teams'])
    self.assertEqual('Philly', bar_json['city'])
    self.assertEqual('42 Wallaby Way', bar_json['address'])

  def tearDown(self):
    self.testbed.deactivate()

if __name__ == '__main__':
  unittest.main()
