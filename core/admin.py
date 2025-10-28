# core/admin.py (Versión Completa y Corregida)

from django.contrib import admin
from .models import (
    Area, Carrera, Ramo,
    Recurso,
    ForumThread, ForumReply,
    TutorProfile, TutoringRequest,
    Review  # <-- ¡AÑADIDO!
)

# =========================
# ÁREA
# =========================
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug")
    prepopulated_fields = {"slug": ("nombre",)}

# =========================
# CARRERA
# =========================
@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ("nombre", "area", "slug")
    list_filter = ("area",)
    search_fields = ("nombre",)
    prepopulated_fields = {"slug": ("nombre",)}

# =========================
# RAMO
# =========================
@admin.register(Ramo)
class RamoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "carrera", "codigo", "slug")
    list_filter = ("carrera",)
    search_fields = ("nombre", "codigo")
    prepopulated_fields = {"slug": ("nombre",)}

# =========================
# RECURSO
# =========================
@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "ramo", "creado_en")
    list_filter = ("ramo", "ramo__carrera")
    search_fields = ("titulo", "descripcion")

# =========================
# FORO – THREAD
# =========================
@admin.register(ForumThread)
class ForumThreadAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'creado_en')
    list_filter = ('creado_en',)
    search_fields = ('titulo', 'contenido', 'autor__username')
    prepopulated_fields = {'slug': ('titulo',)}

# =========================
# FORO – REPLY
# =========================
@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'autor', 'creado_en')
    list_filter = ('creado_en',)
    search_fields = ('contenido', 'autor__username', 'thread__titulo')

# =========================
# TUTOR PROFILE (ACTUALIZADO)
# =========================
@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    # --- CAMBIO: Añadido 'coffee_link' para verlo en la lista ---
    list_display = ('user', 'activo', 'verificado', 'coffee_link', 'actualizado_en')
    list_filter = ('activo', 'verificado')
    search_fields = ('user__username', 'user__email', 'bio', 'materias')
    
    # --- CAMBIO: Usamos 'fieldsets' para organizar mejor y añadir el nuevo campo ---
    fieldsets = (
        (None, {
            'fields': ('user', 'bio', 'materias')
        }),
        ('Estado y Monetización', {
            'fields': ('activo', 'verificado', 'coffee_link')
        }),
    )
    readonly_fields = ('user',) # Para no cambiar el usuario accidentalmente

# =========================
# TUTORING REQUEST
# =========================
@admin.register(TutoringRequest)
class TutoringRequestAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'created_at')
    list_filter = ('status', 'subject')
    search_fields = ('student__username', 'tutor__username', 'subject__nombre')
    readonly_fields = ('student', 'tutor', 'subject', 'message', 'created_at', 'updated_at')

# =========================
# REVIEWS (NUEVO)
# =========================
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """ Configuración del admin para las Reseñas. """
    list_display = ('tutor', 'student', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('tutor__user__username', 'student__username', 'comment')
    # Las reseñas no deberían ser editables por un admin
    readonly_fields = ('tutor', 'student', 'rating', 'comment', 'created_at')