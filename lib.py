def sanitize(s):
  if s is None: 
    return ''
  else:
    return s.lower().lstrip().rstrip()