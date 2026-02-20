from __future__ import annotations

from django import forms

from .models import Product


BRAND_CHOICES = [
    ('Nike', 'Nike'),
    ('Adidas', 'Adidas'),
    ('New Balance', 'New Balance'),
    ('Vans', 'Vans'),
]


class ProductAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        brand_field = self.fields.get('brand')
        if brand_field:
            # Forsiraj deterministički dropdown (Select) za brand.
            # (Neki browseri/templateovi ga inače mogu prikazati kao običan text input.)
            choices = list(BRAND_CHOICES)

            current_value = None
            if self.instance and getattr(self.instance, 'brand', None):
                current_value = self.instance.brand
            elif self.data:
                current_value = self.data.get(self.add_prefix('brand'))

            if current_value and current_value not in [value for value, _ in choices]:
                choices.append((current_value, current_value))

            brand_field.choices = choices
            brand_field.widget = forms.Select(choices=choices)

        # Tailwind design-system klase:
        # - .input je definiran u frontend/src/tailwind.css i kompajliran u static/css/tailwind.css
        input_class = 'input'
        file_class = 'block w-full text-sm text-slate-700 file:mr-4 file:rounded-full file:border-0 file:bg-slate-100 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-ink-900 hover:file:bg-slate-200'

        for name, field in self.fields.items():
            widget = field.widget
            # Preskoči RadioSelect itd. (trenutno ih nema u ovoj formi), ali ostavi robusno za ubuduće.
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                continue
            if isinstance(widget, forms.ClearableFileInput):
                widget.attrs['class'] = file_class
                continue
            # Text/number/url/textarea
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = (existing + ' ' + input_class).strip()

    class Meta:
        model = Product
        fields = [
            'title',
            'brand',
            'description',
            'price',
            'image',
            'image_url',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }
