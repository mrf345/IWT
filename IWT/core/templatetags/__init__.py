from django.template.defaultfilters import register
from django.contrib.auth.models import User

@register.filter(name='get_len')
def get_len(data):
    return len(data)

@register.filter(name='get_range')
def get_range(num):
    return range(1, num + 1)

@register.filter(name='dot_it')
def dot_it(text):
    return text if '.' in text else text + '.'

@register.filter(name='com_it')
def com_it(text):
    return text if ',' in text else text + ','

@register.filter(name='number_it')
def number_it(list):
    return [(index + 1, item) for index, item in enumerate(list)]
    