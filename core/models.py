# core/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from taggit.managers import TaggableManager
from django.urls import reverse # Asegúrate de tener este import
import os

User = get_user_model()

# =========================
# Modelos Existentes
# =========================

class Area(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    slug   = models.SlugField(max_length=90, unique=True, blank=True)
    class Meta: verbose_name = "Área"; verbose_name_plural = "Áreas"; ordering = ["nombre"]
    def __str__(self): return self.nombre
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

class Carrera(models.Model):
    area   = models.ForeignKey(Area, on_delete=models.CASCADE, related_name="carreras")
    nombre = models.CharField(max_length=100)
    slug   = models.SlugField(max_length=110, blank=True)
    class Meta: unique_together = ("area", "slug"); ordering = ["nombre"]
    def __str__(self): return f"{self.nombre} · {self.area.nombre}"
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

class Ramo(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name="ramos")
    nombre  = models.CharField(max_length=120)
    codigo  = models.CharField(max_length=20, blank=True)
    slug    = models.SlugField(max_length=130, blank=True)
    class Meta: unique_together = ("carrera", "slug"); ordering = ["nombre"]
    def __str__(self): return f"{self.nombre} · {self.carrera.nombre}"
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

def resource_upload_to(instance, filename):
    base, ext = os.path.splitext(filename)
    fname = f"{slugify(base)[:60]}{ext.lower()}"
    a = instance.ramo.carrera.area.slug
    c = instance.ramo.carrera.slug
    r = instance.ramo.slug
    y = str(instance.anio or "s-anio")
    return f"recursos/{a}/{c}/{r}/{y}/{fname}"

class Recurso(models.Model):
    TIPO_CHOICES = [("apunte", "Apunte/Resumen"), ("guia", "Guía/Ejercicios"), ("prueba", "Prueba/Examen"), ("otros", "Otros")]
    FORMATO_CHOICES = [("pdf","PDF"),("ppt","PPT/PPTX"),("doc","DOC/DOCX"), ("zip","ZIP"),("img","Imagen"),("otro","Otro")]
    SEMESTRE_CHOICES = [(1,"1"),(2,"2")]
    titulo = models.CharField(max_length=160); slug = models.SlugField(max_length=180, blank=True)
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ramo = models.ForeignKey(Ramo, on_delete=models.CASCADE, related_name="recursos")
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to=resource_upload_to, max_length=300)
    tipo = models.CharField(max_length=12, choices=TIPO_CHOICES, default="apunte")
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default="pdf")
    anio = models.PositiveIntegerField(blank=True, null=True)
    semestre = models.IntegerField(choices=SEMESTRE_CHOICES, blank=True, null=True)
    tags = TaggableManager(blank=True); creado_en = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-creado_en"]
    def __str__(self): return self.titulo
    def save(self, *args, **kwargs):
        if not self.slug: base = slugify(self.titulo)[:170] or "recurso"; self.slug = base
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse('recurso_detalle', args=[self.ramo.carrera.area.slug, self.ramo.carrera.slug, self.ramo.slug, self.slug])

class ForumThread(models.Model):
    titulo = models.CharField(max_length=200); slug = models.SlugField(max_length=220, unique=True, blank=True)
    contenido = models.TextField(); autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="threads")
    tags = TaggableManager(blank=True); creado_en = models.DateTimeField(auto_now_add=True); actualizado_en = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-creado_en']
    def __str__(self): return self.titulo
    def save(self, *args, **kwargs):
        if not self.slug: self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)
    def get_absolute_url(self): return reverse('forum_thread_detail', args=[self.slug])

class ForumReply(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name="replies")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    contenido = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['creado_en']
    def __str__(self): return f"Respuesta de {self.autor.username} en '{self.thread.titulo}'"

class TutorProfile(models.Model):
    TIPO_VOLUNTARIO = 'voluntario'
    TIPO_DONACION = 'donacion'
    TIPO_PRIVADO = 'privado'
    TIPO_TUTOR_CHOICES = [
        (TIPO_VOLUNTARIO, 'Ayuda Voluntaria (Gratis)'),
        (TIPO_DONACION, 'A base de Donaciones (Invítame un café ☕)'),
        (TIPO_PRIVADO, 'Tarifa Privada (Arreglo por interno)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tutor_profile')
    bio = models.TextField(blank=True, help_text="Una breve descripción sobre ti, tu experiencia y cómo puedes ayudar.")
    materias = models.CharField(
        max_length=255,
        blank=True,
        help_text="Escribe tus habilidades o materias separadas por comas."
    )
    coffee_link = models.URLField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Enlace a MercadoPago, Ko-fi, etc. para 'Invítale un café'"
    )
    tipo_tutor = models.CharField(
        max_length=20,
        choices=TIPO_TUTOR_CHOICES,
        default=TIPO_VOLUNTARIO,
        help_text="Define cómo ofreces tus tutorías."
    )
    verificado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['user__username']
    def __str__(self): return f"Perfil de tutor para {self.user.username}"

class TutoringRequest(models.Model):
    STATUS_CHOICES = [('pending', 'Pendiente'), ('accepted', 'Aceptada'), ('rejected', 'Rechazada'), ('completed', 'Completada')]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_tutoring_requests')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_tutoring_requests')
    subject = models.ForeignKey(
        Ramo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        subject_name = self.subject.nombre if self.subject else "Tema en mensaje"
        return f"Solicitud de {self.student.username} a {self.tutor.username} sobre {subject_name}"

class Review(models.Model):
    tutor = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="given_reviews")
    rating = models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-created_at']
        unique_together = ('tutor', 'student')
    def __str__(self):
        return f"Reseña de {self.student.username} para {self.tutor.user.username} ({self.rating} estrellas)"

class StudyRoom(models.Model):
    nombre = models.CharField(max_length=100, help_text="Nombre corto y descriptivo para la sala (ej. 'Certamen 2 Cálculo')")
    descripcion = models.TextField(blank=True, help_text="Descripción más detallada (opcional)")
    ramo = models.ForeignKey(Ramo, on_delete=models.SET_NULL, null=True, blank=True, related_name="study_rooms")
    creador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_study_rooms")
    es_temporal = models.BooleanField(default=False, help_text="Marcar si es una sesión rápida o temporal")
    fecha_expiracion = models.DateTimeField(null=True, blank=True, help_text="Si es temporal, ¿cuándo debería desaparecer?")
    enlace_videollamada = models.URLField(max_length=255, blank=True, help_text="Enlace a Google Meet, Jitsi, Discord, etc.")
    enlace_pizarra = models.URLField(max_length=255, blank=True, help_text="Enlace a Excalidraw, Miro, etc.")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-creado_en']
    def __str__(self):
        return self.nombre
    def get_absolute_url(self):
        return reverse('study_room_detail', args=[self.pk])

# =========================
# ¡NUEVO MODELO! Mensaje de Chat
# =========================
class ChatMessage(models.Model):
    # A qué sala pertenece el mensaje
    room = models.ForeignKey(StudyRoom, on_delete=models.CASCADE, related_name="messages")
    # Quién escribió el mensaje
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="chat_messages")
    # El contenido del mensaje
    content = models.TextField()
    # Cuándo se envió
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp'] # Mensajes más antiguos primero

    def __str__(self):
        author_name = self.author.username if self.author else "Usuario"
        return f"Msg by {author_name} in {self.room.nombre} at {self.timestamp.strftime('%H:%M')}"

# --- Fin del nuevo modelo ---