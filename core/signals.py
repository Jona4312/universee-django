# core/signals.py
from django.dispatch import receiver
from django.contrib import messages
from allauth.account.signals import user_signed_up, user_logged_in
from django.core.exceptions import ValidationError

@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    messages.success(request, f"🎉 Cuenta creada: {user.username}. ¡Bienvenido/a a UniversoE!")

@receiver(user_logged_in)
def on_user_logged_in(request, user, **kwargs):
    messages.success(request, f"¡Hola, {user.username}! Sesión iniciada correctamente.")
