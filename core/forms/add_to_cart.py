from django import forms
from core.models import OrderProduct

class OrderProductForm(forms.ModelForm):

    class Meta:
        model = OrderProduct
        fields = ('product','quantity_ordered')
