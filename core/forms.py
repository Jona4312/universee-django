# core/forms.py

from django import forms
# --- ¡CAMBIO AQUÍ! Añadido StudyRoom ---
from .models import Recurso, TutorProfile, ForumThread, TutoringRequest, Ramo, StudyRoom 
# --- FIN DEL CAMBIO ---

# ==========
# Recurso
# ==========
class RecursoForm(forms.ModelForm):
    class Meta:
        model = Recurso
        fields = ("titulo", "descripcion", "archivo", "tipo", "formato", "anio", "semestre")
        widgets = {
            "titulo":       forms.TextInput(attrs={"class": "form-control", "placeholder": "Título del apunte"}),
            "descripcion": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Descripción (opcional)"}),
            "archivo":      forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tipo":         forms.Select(attrs={"class": "form-control"}),
            "formato":      forms.Select(attrs={"class": "form-control"}),
            "anio":         forms.NumberInput(attrs={"class": "form-control", "min": 2000, "max": 2100}),
            "semestre":     forms.Select(attrs={"class": "form-control"}),
        }

# ==========
# Foro
# ==========
class ForumThreadForm(forms.ModelForm):
    class Meta:
        model = ForumThread
        fields = ['titulo', 'contenido', 'tags']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Un título claro y conciso...'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Describe tu duda con el mayor detalle posible. Puedes usar Markdown.'}),
            'tags': forms.TextInput(attrs={'class': "form-control", 'placeholder': 'Ej: cálculo, certamen-1, python'}),
        }
        labels = {'titulo': 'Título', 'contenido': 'Descripción', 'tags': 'Etiquetas'}


# ==========
# TutorProfile
# ==========
class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ['bio', 'materias', 'tipo_tutor', 'coffee_link']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Cuéntale a otros sobre ti, tu experiencia y en qué materias te sientes más fuerte...'
            }),
            'materias': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cálculo I, Álgebra Lineal, Programación en Python...'
            }),
            'tipo_tutor': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'coffee_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.buymeacoffee.com/tu_usuario'
            })
        }
        labels = {
            'bio': 'Sobre mí',
            'materias': 'Materias que dominas',
            'tipo_tutor': 'Modalidad de Tutoría',
            'coffee_link': 'Enlace de "Invítale un café" (Opcional)'
        }
        help_texts = {
            'materias': 'Escribe tus habilidades o materias separadas por comas.',
            'coffee_link': 'Pega tu enlace de donación (ej. Ko-fi, MercadoPago). Este enlace solo se mostrará si eliges la modalidad "A base de Donaciones".'
        }

# ==========
# Solicitud de Tutoría
# ==========
class TutoringRequestForm(forms.ModelForm):
    class Meta:
        model = TutoringRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe brevemente qué materia necesitas, qué quieres repasar o en qué tienes dudas...'}),
        }
        labels = { 
            'message': 'Tu mensaje para el tutor'
        }

# =========================
# ¡NUEVO! Formulario para Sala de Estudio
# =========================
class StudyRoomForm(forms.ModelForm):
    class Meta:
        model = StudyRoom
        # --- ¡CAMBIO AQUÍ! Eliminado 'ramo' ---
        fields = [
            'nombre',
            'descripcion',
            # 'ramo', <-- Eliminado
            'es_temporal',
            'enlace_videollamada',
            'enlace_pizarra'
        ]
        # --- FIN DEL CAMBIO ---

        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Ej: Repaso Final Álgebra'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Opcional: ¿Qué temas específicos se verán? ¿Hay algún requisito?'
            }),
            # --- ¡CAMBIO AQUÍ! Eliminado widget de 'ramo' ---
            # 'ramo': forms.Select(attrs={'class': 'form-select'}),
            # --- FIN DEL CAMBIO ---
            'es_temporal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'enlace_videollamada': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://meet.google.com/...'
            }),
            'enlace_pizarra': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://excalidraw.com/...'
            }),
        }

        labels = {
            'nombre': 'Nombre de la Sala',
            'descripcion': 'Descripción (Opcional)',
            # --- ¡CAMBIO AQUÍ! Eliminada label de 'ramo' ---
            # 'ramo': '¿Asociada a un Ramo Específico? (Opcional)',
            # --- FIN DEL CAMBIO ---
            'es_temporal': '¿Es una sesión temporal / rápida?',
            'enlace_videollamada': 'Enlace a Videollamada (Opcional)',
            'enlace_pizarra': 'Enlace a Pizarra Virtual (Opcional)'
        }

        help_texts = {
            'es_temporal': 'Marca esto si es una sesión corta o espontánea. Las salas temporales podrían desaparecer después de un tiempo.',
            'enlace_videollamada': 'Pega aquí el enlace a Google Meet, Jitsi, Discord, etc.',
            'enlace_pizarra': 'Pega aquí el enlace a Excalidraw, Miro, etc.'
        }