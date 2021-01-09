from django import template
from ..models import Order
from django.db.models import Sum

register = template.Library()

@register.filter
def cart_item_count(user):

    if user.is_authenticated:
        qs = Order.objects.filter(placed = False, user=user)
        if qs.exists():
            order = qs[0]
            count = order.orderproduct_set.all().aggregate(sum = Sum('quantity_ordered'))

            return count.get('sum') if count.get('sum') else 0
        else:
            return 0
