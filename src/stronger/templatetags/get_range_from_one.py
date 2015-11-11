from django.template import Library

register = Library()

@register.filter
def get_range_from_one(value):
  """
  Returns a list containing a numeric range made from one to a given value.
  """
  return range(1, value)
