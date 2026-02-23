from django import forms


class CartUpdateForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=10)
