from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re


SIZE_CHOICES = [(str(size), str(size)) for size in range(35, 48)]

COLOR_CHOICES = [
    ('black', 'Crna'),
    ('white', 'Bijela'),
]

DELIVERY_CHOICES = [
    ('standard', 'Standard (3-5 dana)'),
    ('express', 'Express (1-2 dana)'),
]

PAYMENT_CHOICES = [
    ('cod', 'Pouzeće'),
    ('card', 'Kartica (Visa/Mastercard)'),
    ('paypal', 'PayPal'),
]


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=False)
    referral_code = forms.CharField(required=False, max_length=50)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dodaj Bootstrap form-control klasu na sva polja
        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            classes = (existing + ' form-control').strip()
            field.widget.attrs.update({'class': classes})



class ProductOrderForm(forms.Form):
    size = forms.ChoiceField(choices=SIZE_CHOICES, widget=forms.RadioSelect, label='Veličina', initial='42')
    color = forms.ChoiceField(choices=COLOR_CHOICES, label='Boja', initial='black')
    quantity = forms.IntegerField(min_value=1, max_value=10, initial=1, label='Količina')
    full_name = forms.CharField(max_length=120, label='Ime i prezime')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=30, label='Telefon')
    address = forms.CharField(max_length=200, label='Adresa')
    city = forms.CharField(max_length=100, label='Grad')
    postal_code = forms.CharField(max_length=10, label='Poštanski broj')
    delivery_method = forms.ChoiceField(choices=DELIVERY_CHOICES, label='Dostava', initial='standard')
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, label='Plaćanje', initial='cod')

    # Uvjetni podaci o plaćanju (prikazani/obavezni ovisno o payment_method)
    paypal_email = forms.EmailField(required=False, label='PayPal email')
    cardholder_name = forms.CharField(required=False, max_length=120, label='Ime i prezime na kartici')
    card_number = forms.CharField(required=False, max_length=19, label='Broj kartice', help_text='Upiši samo brojeve (16 znamenki)')
    card_expiry = forms.CharField(required=False, max_length=5, label='Rok valjanosti (MM/YY)')
    card_cvv = forms.CharField(required=False, max_length=3, label='CVV')

    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}), label='Napomena (opcionalno)')
    agree_terms = forms.BooleanField(label='Prihvaćam uvjete kupovine')

    def __init__(self, *args, **kwargs):
        # mode='product' -> validira samo opcije proizvoda za dodavanje u košaricu
        # mode='checkout' -> validira cijelu checkout formu
        mode = kwargs.pop('mode', 'checkout')
        super().__init__(*args, **kwargs)

        if mode == 'product':
            # Stranica proizvoda validira samo veličinu/boju/količinu.
            # Ukloni checkout polja da ne padnu na validaciji.
            for name in [
                'full_name',
                'email',
                'phone',
                'address',
                'city',
                'postal_code',
                'delivery_method',
                'payment_method',
                'paypal_email',
                'cardholder_name',
                'card_number',
                'card_expiry',
                'card_cvv',
                'notes',
                'agree_terms',
            ]:
                self.fields.pop(name, None)

        if mode == 'checkout':
            # Stavke košarice već sadrže veličinu/boju/količinu po stavci.
            # Checkout forma prikuplja samo podatke o dostavi/plaćanju.
            for name in ['size', 'color', 'quantity']:
                self.fields.pop(name, None)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.RadioSelect):
                widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(widget, forms.CheckboxInput):
                existing = widget.attrs.get('class', '')
                widget.attrs.update({'class': (existing + ' form-check-input').strip()})
            elif isinstance(widget, forms.Select):
                existing = widget.attrs.get('class', '')
                widget.attrs.update({'class': (existing + ' form-select').strip()})
            elif isinstance(widget, forms.Textarea):
                existing = widget.attrs.get('class', '')
                widget.attrs.update({'class': (existing + ' form-control').strip()})
            else:
                existing = widget.attrs.get('class', '')
                widget.attrs.update({'class': (existing + ' form-control').strip()})
        if 'quantity' in self.fields:
            self.fields['quantity'].widget.attrs.update({'min': 1, 'max': 10})

        # Postavi osnovne atribute za uvjetna polja
        if 'card_number' in self.fields:
            self.fields['card_number'].widget.attrs.update({'inputmode': 'numeric', 'autocomplete': 'cc-number'})
        if 'card_expiry' in self.fields:
            self.fields['card_expiry'].widget.attrs.update({'autocomplete': 'cc-exp'})
            self.fields['card_expiry'].widget.attrs.update({'placeholder': 'MM/YY', 'inputmode': 'numeric', 'maxlength': 5})
        if 'card_cvv' in self.fields:
            self.fields['card_cvv'].widget.attrs.update({'inputmode': 'numeric', 'autocomplete': 'cc-csc'})
            self.fields['card_cvv'].widget.attrs.update({'maxlength': 3})
        if 'cardholder_name' in self.fields:
            self.fields['cardholder_name'].widget.attrs.update({'autocomplete': 'cc-name'})

    def clean(self):
        cleaned = super().clean()
        # Stranica proizvoda ima samo veličinu/boju/količinu.
        if 'payment_method' not in self.fields:
            return cleaned
        payment_method = cleaned.get('payment_method')

        # Pouzeće: nema dodatnih polja
        if payment_method == 'cod':
            return cleaned

        if payment_method == 'paypal':
            if not cleaned.get('paypal_email'):
                self.add_error('paypal_email', 'Unesi PayPal email.')
            return cleaned

        if payment_method == 'card':
            cardholder_name = (cleaned.get('cardholder_name') or '').strip()
            card_number_raw = (cleaned.get('card_number') or '').strip()
            card_expiry = (cleaned.get('card_expiry') or '').strip()
            card_cvv = (cleaned.get('card_cvv') or '').strip()

            if not cardholder_name:
                self.add_error('cardholder_name', 'Unesi ime na kartici.')

			# Normaliziraj broj kartice na samo znamenke
            card_number_digits = re.sub(r'\D', '', card_number_raw)
            if not card_number_digits:
                self.add_error('card_number', 'Unesi broj kartice.')
            elif len(card_number_digits) != 16:
                self.add_error('card_number', 'Broj kartice mora imati točno 16 znamenki.')
            else:
                cleaned['card_number'] = card_number_digits

            if not card_expiry:
                self.add_error('card_expiry', 'Unesi rok valjanosti.')
            elif not re.fullmatch(r'(0[1-9]|1[0-2])\/(\d{2})', card_expiry):
                self.add_error('card_expiry', 'Format mora biti MM/YY gdje je MM 01-12, a YY su zadnje dvije znamenke godine (npr. 08/27).')

            if not card_cvv:
                self.add_error('card_cvv', 'Unesi CVV.')
            elif not re.fullmatch(r'\d{3}', card_cvv):
                self.add_error('card_cvv', 'CVV mora imati točno 3 znamenke.')

            return cleaned

        self.add_error('payment_method', 'Nepoznata metoda plaćanja.')
        return cleaned
