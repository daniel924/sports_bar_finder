import unittest
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed

import bar_model

class BarModelTests(unittest.TestCase):

  def setUp(self):
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    # Next, declare which service stubs you want to use.
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()

  def testInsertNewBar(self):
    bar_model.insert('newbies lair', ['newbs'], None, 'bahstan')
    bars = bar_model.Bar.query(bar_model.Bar.name == 'newbies lair').fetch()
    self.assertEqual(1, len(bars))
    self.assertEqual('newbies lair', bars[0].name)

  def testInsertBarSameNameDifferentCity(self):
    bar_model.insert('newbies lair', ['newbs'], None, 'bahstan')
    bar_model.insert('newbies lair', ['newbs'], None, 'new yowk')
    bars = bar_model.Bar.query(bar_model.Bar.name == 'newbies lair').fetch()
    self.assertEqual(2, len(bars))

  def testInsertBarTwiceMergesTeams(self):
    bar_model.insert('Pop Bar', ['pops'], 'address', 'nyc')
    bar_model.insert('Pop Bar', ['peps'], 'address', 'nyc')
    bars = bar_model.Bar.query(bar_model.Bar.name == 'pop bar').fetch()
    self.assertEqual(1, len(bars))
    self.assertItemsEqual(['pops', 'peps'], bars[0].teams)

  def testInsertBarTrimsWhiteSpaceAndLowersCase(self):
    bar_model.insert(' jOe\'s', [' poPs '], ' aDdy', 'cIty ')
    bars = bar_model.Bar.query(bar_model.Bar.name == 'joe\'s').fetch()
    self.assertEqual(1, len(bars))
    self.assertItemsEqual(['pops'], bars[0].teams)
    self.assertEqual('addy', bars[0].address)
    self.assertEqual('city', bars[0].city)

  def testSearchByBarName(self):
    bar_model.Bar(name='peeps', teams=['plows', 'pampers'], address='addy', city='new york, ny').put()
    bars = bar_model.search('peeps')
    self.assertEqual(1, len(bars))
    self.assertEqual('peeps', bars[0].name)
    self.assertItemsEqual(['plows', 'pampers'], bars[0].teams)

  def testSearchByTeam(self):
    bar_model.Bar(name='peeps', teams=['plows', 'pampers'], address='addy', city='new york, ny').put()
    bars = bar_model.search('plows')
    self.assertEqual(1, len(bars))
    self.assertEqual('peeps', bars[0].name)
    self.assertItemsEqual(['plows', 'pampers'], bars[0].teams)

  def testSearchWithCity(self):
    bar_model.Bar(name='peeps', teams=['plows', 'pampers'], address='addy', city='new york, ny').put()
    bar_model.Bar(name='peeps', teams=['plows', 'pouches'], address='addy', city='boston, ma').put()
    bars = bar_model.search('peeps', city='new york, ny')
    self.assertEqual(1, len(bars))
    self.assertEqual('peeps', bars[0].name)
    self.assertEqual(['plows', 'pampers'], bars[0].teams)

def tearDown(self):
  self.testbed.deactivate()

if __name__ == '__main__':
    unittest.main()