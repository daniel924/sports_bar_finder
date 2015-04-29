import collections
import functools

TEAMS_FILE = 'teams.txt'

class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)

def sanitize(s):
  if s is None: 
    return ''
  else:
    return s.lower().lstrip().rstrip()

@memoized
def BuildTeamsList(teams_file):
  teams = {}
  f = open(teams_file)
  for line in f:
    split = line.split(',')
    city = split[0].lstrip().rstrip().lower()
    team = split[1].lstrip().rstrip().lower()
    full_team_name = city + ' ' + team
    teams[full_team_name] = full_team_name
    teams[team] = full_team_name
  return teams

def BarToJson(bar):
  """Takes in a bar_model.Bar and returns json."""
  return {
      'name': bar.name.title(),
      'teams': [t.title() for t in bar.teams],
      'city': bar.city.title(),
      'address': bar.address.title()}