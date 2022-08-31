def is_null_or_empty(string):
  is_not_null = (string != None) and isinstance(string, str)
  if not is_not_null:
    is_not_null = len(string) != 0
  return not is_not_null
