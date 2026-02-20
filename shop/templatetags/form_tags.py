from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, css_class):
    # Template filter: dodaje CSS class na widget polja forme.
    existing_classes = field.field.widget.attrs.get('class', '')
    new_classes = f"{existing_classes} {css_class}".strip()
    return field.as_widget(attrs={'class': new_classes})
