from django import forms


COLOR_CHOICES = [
    ('black', 'Crna'),
    ('white', 'Bijela'),
]


class AddToCartForm(forms.Form):
    # Forma za dodavanje u session košaricu (odvojeno od checkout/payment validacije).

    size = forms.ChoiceField(choices=[(str(size), str(size)) for size in range(35, 48)])
    color = forms.ChoiceField(choices=COLOR_CHOICES, required=True)
    quantity = forms.IntegerField(min_value=1, max_value=10, initial=1)

    # UX opcija: ako je checkout=True, nakon dodavanja vodi na checkout (ili login pa checkout).
    checkout = forms.BooleanField(required=False)
