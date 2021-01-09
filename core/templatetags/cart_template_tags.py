from django import template
from ..models import Order

register = template.Library()

@register.filter
def cart_item_count(user):

    if user.is_authenticated:
        qs = Order.objects.filter(placed = False, user=user)
        if qs.exists():
            order = qs[0]
            count = order.orderproduct_set.all().count()
            return count
        else:
            return 0
