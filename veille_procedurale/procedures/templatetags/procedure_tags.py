from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def get_unread_notifications_count(user):
    return user.procedure_notifications.filter(is_read=False).count()