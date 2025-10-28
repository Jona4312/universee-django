# core/templatetags/form_extras.py
from django import template

register = template.Library()

@register.filter(name="add_class")
def add_class(field, css):
    """
    Agrega clases CSS al widget del campo sin perder las existentes.
    Uso: {{ form.campo|add_class:"form-control is-invalid" }}
    """
    attrs = field.field.widget.attrs.copy()
    existing = attrs.get("class", "")
    attrs["class"] = f"{existing} {css}".strip()
    return field.as_widget(attrs=attrs)
