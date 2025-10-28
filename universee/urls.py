# universee/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication URLs
    path("accounts/", include("allauth.urls")),

    # Main app URLs
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.user_profile, name="profile"),

    # Forum URLs
    path("forum/", views.forum_index, name="forum_index"),
    path("forum/new/", views.create_forum_thread, name="create_forum_thread"),
    path("forum/thread/<slug:slug>/", views.forum_thread_detail, name="forum_thread_detail"),
    
    # Tutoring System URLs
    path("tutors/", views.tutor_list, name="tutor_list"),
    path("tutors/<str:username>/", views.tutor_detail, name="tutor_detail"),
    path("profile/become-tutor/", views.become_tutor, name="become_tutor"),
    path("tutors/<str:username>/request/", views.request_tutoring, name="request_tutoring"),
    path("dashboard/tutorias/", views.manage_tutoring_requests, name="manage_tutoring_requests"),
    
    # Resource URLs
    path("recursos/", views.recursos_list, name="recursos_list"),
    path("recursos/subir/", views.recursos_subir, name="recursos_subir"),
    path("recursos/descargar/<int:pk>/", views.recurso_descargar, name="recurso_descargar"),
    path("recursos/<slug:area_slug>/<slug:carrera_slug>/<slug:ramo_slug>/<slug:recurso_slug>/", views.recurso_detalle, name="recurso_detalle"),

    # AJAX URL
    path("ajax/get-carreras/", views.get_carreras_ajax, name="get_carreras_ajax"),

    # AI Guide URLs
    path("guia/", views.guia_inteligente, name="guia_inteligente"),
    path("guia/descargar/", views.guia_descargar_pdf, name="guia_descargar_pdf"),

    # --- NEW: Study Room URLs ---
    path("study-rooms/", views.study_room_list, name="study_room_list"), # List and Create rooms
    path("study-rooms/<int:pk>/", views.study_room_detail, name="study_room_detail"), # View a specific room
    # --- END NEW ---
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)