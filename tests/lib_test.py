import unittest
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

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
    tmap = lib.testBuildTeamsList(lib.TEAMS_FILE)
    self.assertEqual('new york yankees', tmap['yankees'])
    self.assertEqual('new york yankees', tmap['yankees'])
    self.assertEqual('boston red sox', tmap['red sox'])
    self.assertEqual('phoenix coyotes', tmap['coyotes'])
    self.assertNone(tmap['boston'])

def testSanitize(self):
    s1 = lib.sanitize(None)
    self.assertEqual('', s1)
    s2 = lib.sanitize('   sAsBerYla       ')
    self.assertEqual('sasberyla')

def testBarToJson(self):
    pass
  
def tearDown(self):
  self.testbed.deactivate()

if __name__ == '__main__':
    unittest.main()