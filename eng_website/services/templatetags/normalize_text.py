from django import template
from django.template.exceptions import TemplateSyntaxError

register = template.Library()
MINUTE_FORMS = ['минут', 'минуты', 'минута']
LESSON_FORMS = ['уроков', 'урока', 'урок']


@register.filter
def normalize_text_for_numbers(minutes, type):
    if type == 'minutes':
        forms = MINUTE_FORMS
    elif type == 'lessons':
        forms = LESSON_FORMS
    else:
        raise TemplateSyntaxError('Wrong type for filter normalize_text_for_numbers')

    tens = minutes % 100
    ones = tens % 10
    if tens > 4 and tens < 20:
        return f'{minutes} {forms[0]}'
    elif ones > 1 and ones < 5:
        return f'{minutes} {forms[1]}'
    else:
        return f'{minutes} {forms[2]}'
