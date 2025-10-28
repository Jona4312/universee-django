from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages # Asegúrate que messages esté importado
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import logging
import os
import json
from django.utils import timezone

from django import forms
from django.template.loader import render_to_string
from weasyprint import HTML
import markdown
from django.core.mail import send_mail
from openai import OpenAI

from .forms import (
    RecursoForm, TutorProfileForm, ForumThreadForm, TutoringRequestForm, StudyRoomForm
)
from .models import (
    Area, Carrera, Ramo, Recurso,
    ForumThread, ForumReply,
    TutorProfile, User, TutoringRequest, Review,
    StudyRoom, ChatMessage
)


# ==============================
# LOG
# ==============================
log = logging.getLogger(__name__)

# ==============================
# PÁGINAS BÁSICAS Y PERFIL
# ==============================
# ... (Tu código home, dashboard, user_profile - Omitido por brevedad) ...
def home(request):
    return render(request, "home.html")

@login_required
def dashboard(request):
    q = (request.GET.get("q") or "").strip()
    results = []
    if q:
        qs = (
            Recurso.objects
            .select_related("ramo", "ramo__carrera", "ramo__carrera__area")
            .filter(
                Q(titulo__icontains=q) |
                Q(descripcion__icontains=q) |
                Q(tags__name__icontains=q) |
                Q(ramo__nombre__icontains=q) |
                Q(ramo__carrera__nombre__icontains=q) |
                Q(ramo__carrera__area__nombre__icontains=q)
            )
            .distinct()[:20]
        )
        results = list(qs)
    return render(request, "dashboard.html", {"q": q, "results": results})

@login_required
def user_profile(request):
    user = request.user
    recursos_subidos = Recurso.objects.filter(autor=user)
    threads_creados = ForumThread.objects.filter(autor=user)
    tutorias_realizadas = TutoringRequest.objects.filter(tutor=user, status='completed').count()

    contribuciones = list(recursos_subidos) + list(threads_creados)
    contribuciones_ordenadas = sorted(contribuciones, key=lambda x: x.creado_en, reverse=True)

    context = {
        'user': user,
        'contribuciones_recientes': contribuciones_ordenadas,
        'total_recursos': recursos_subidos.count(),
        'total_threads': threads_creados.count(),
        'total_tutorias': tutorias_realizadas
    }
    return render(request, 'account/profile.html', context)


# ==============================
# RECURSOS
# ==============================
# ... (Tu código de RECURSOS - Omitido por brevedad) ...
# --- Catálogo Académico Centralizado ---
CATALOGO_ACADEMICO = {
    "Facultad de Ciencias Sociales": ["Antropología", "Psicología", "Sociología", "Trabajo Social"],
    "Facultad de Comunicaciones": ["Periodismo", "Dirección Audiovisual", "Publicidad", "Cine"],
    "Facultad de Derecho": ["Derecho"],
    "Facultad de Educación": ["Pedagogía en Educación Parvularia", "Pedagogía en Educación Básica", "Pedagogía en Educación Media"],
    "Facultad de Humanidades y Arte": ["Traducción/Interpretación en Idiomas Extranjeros", "Pedagogía en Artes Visuales", "Pedagogía en Educación Musical", "Pedagogía en Filosofía", "Pedagogía en Historia y Geografía"],
    "Escuela de Gobierno": ["Administración Pública y Ciencia Política"],
    "Facultad de Economía y Negocios": ["Ingenería Comercial", "Auditoría / Contador Auditor", "Ingeniería en Información y Control de Gestión", "Ingeniería en Gestión Turística", "Administración de Empresas"],
    "Facultad de Ingeniería": ["Ingeniería Civil (Plan Común)", "Ingeniería Civil Industrial", "Ingeniería Civil en Computación / Informática", "Ingeniería Civil Mecánica", "Ingeniería Civil Química", "Ingeniería Civil Eléctrica", "Ingeniería Civil de Minas", "Ingeniería Civil en Obras Civiles", "Ingeniería Civil Aeroespacial", "Ingeniería Civil Biomédica", "Ingeniería Civil en Biotecnología", "Ingeniería Civil en Ciencia de Datos", "Ingeniería en Diseño", "Ingeniería en Aviación Comercial", "Ciencias de la Computación"],
    "Facultad de Medicina": ["Medicina", "Enfermería", "Kinesiología", "Nutrición y Dietética", "Tecnología Médica", "Fonoaudiología", "Terapia Ocupacional", "Obstetricia y Puericultura"],
    "Facultad de Odontología": ["Odontología"],
    "Facultad de Química y de Farmacia": ["Química y Farmacia", "Bioquímica"],
    "Facultad de Ciencias Biológicas": ["Biología", "Bioquímica", "Biología Marina", "Bioingeniería"],
    "Facultad de Ciencias Físicas y Matemáticas": ["Física", "Astronomía", "Matemática", "Estadística", "Geología"],
    "Facultad de Ciencias Químicas": ["Química", "Química Ambiental"],
    "Facultad de Agronomía e Ingeniería Forestal": ["Agronomía", "Ingeniería Forestal", "Ingeniería en Recursos Naturales Renovables"],
    "Facultad de Arquitectura, Diseño y Estudios Urbanos": ["Arquitectura", "Diseño", "Planificación Urbana", "Geografía"],
    "Áreas Técnicas (USM)": ["Técnico Universitario en Mantenimiento Aeronáutico", "Técnico Universitario en Construcción", "Técnico Universitario en Electricidad", "Técnico Universitario en Mecánica Automotriz"]
}

@login_required
def recursos_list(request):
    q = (request.GET.get("q") or "").strip()
    tipo = (request.GET.get("tipo") or "").strip()
    formato = (request.GET.get("formato") or "").strip()
    anio = (request.GET.get("anio") or "").strip()
    qs = Recurso.objects.select_related("ramo", "ramo__carrera", "ramo__carrera__area").all()
    if q:
        qs = qs.filter(Q(titulo__icontains=q) | Q(descripcion__icontains=q) | Q(tags__name__icontains=q)).distinct()
    if tipo:
        qs = qs.filter(tipo=tipo)
    if formato:
        qs = qs.filter(formato=formato)
    if anio:
        try:
            qs = qs.filter(anio=int(anio))
        except ValueError:
            pass
    page_obj = Paginator(qs, 12).get_page(request.GET.get("page", 1))
    ctx = {"q": q, "tipo": tipo, "formato": formato, "anio": anio, "page_obj": page_obj, "formatos": ["pdf", "ppt", "doc", "zip", "img", "otro"], "area": None, "carrera": None, "ramo": None}
    return render(request, "recursos/lista.html", ctx)

@login_required
def recurso_detalle(request, area_slug, carrera_slug, ramo_slug, recurso_slug):
    recurso = get_object_or_404(Recurso.objects.select_related("ramo", "ramo__carrera", "ramo__carrera__area"), slug=recurso_slug, ramo__slug=ramo_slug, ramo__carrera__slug=carrera_slug, ramo__carrera__area__slug=area_slug)
    return render(request, "recursos/detalle.html", {"recurso": recurso})

@login_required
def recurso_descargar(request, pk):
    recurso = get_object_or_404(Recurso, pk=pk)
    return redirect(recurso.archivo.url)

@login_required
def recursos_subir(request):
    if request.method == "POST":
        form = RecursoForm(request.POST, request.FILES)
        facultad = (request.POST.get("facultad") or "").strip()
        carrera_name = (request.POST.get("carrera") or "").strip()
        ramo_name = (request.POST.get("ramo") or "").strip()
        faltan = []
        if not facultad: faltan.append("Facultad")
        if not carrera_name: faltan.append("Carrera")
        if not ramo_name: faltan.append("Ramo")
        if faltan:
            messages.error(request, f"Faltan campos obligatorios: {', '.join(faltan)}.")
        elif form.is_valid():
            area, _ = Area.objects.get_or_create(nombre=facultad)
            carrera, _ = Carrera.objects.get_or_create(area=area, nombre=carrera_name)
            ramo, _ = Ramo.objects.get_or_create(carrera=carrera, nombre=ramo_name)
            recurso = form.save(commit=False)
            recurso.ramo = ramo
            if request.user.is_authenticated:
                recurso.autor = request.user
            recurso.save()
            form.save_m2m()
            messages.success(request, "¡Recurso subido con éxito!")
            return redirect("dashboard")
        else:
            messages.error(request, "Revisa los errores del formulario.")
    else:
        form = RecursoForm()

    context = {
        "form": form,
        "facultades_list": list(CATALOGO_ACADEMICO.keys())
    }
    return render(request, "recursos/subir.html", context)

def get_carreras_ajax(request):
    facultad = request.GET.get('facultad', '')
    carreras = CATALOGO_ACADEMICO.get(facultad, [])
    return JsonResponse({'carreras': carreras})


# ==============================
# FORO
# ==============================
# ... (Tu código de FORO - Omitido por brevedad) ...
@login_required
def forum_index(request):
    all_threads = ForumThread.objects.select_related('autor').annotate(num_replies=Count('replies')).order_by('-actualizado_en')
    return render(request, 'forum/index.html', {'threads': all_threads})

@login_required
def create_forum_thread(request):
    if request.method == 'POST':
        form = ForumThreadForm(request.POST)
        if form.is_valid():
            thread = form.save(commit=False)
            thread.autor = request.user
            thread.save()
            form.save_m2m()
            messages.success(request, '¡Tu duda ha sido publicada!')
            return redirect(thread.get_absolute_url())
    else:
        form = ForumThreadForm()
    return render(request, 'forum/create_thread.html', {'form': form})

@login_required
def forum_thread_detail(request, slug):
    thread = get_object_or_404(ForumThread, slug=slug)
    replies = thread.replies.select_related('autor').order_by('creado_en')
    if request.method == 'POST':
        reply_content = request.POST.get('contenido', '').strip()
        if reply_content:
            ForumReply.objects.create(thread=thread, autor=request.user, contenido=reply_content)
            messages.success(request, '¡Tu respuesta ha sido publicada!')
            thread.save()
            return redirect(thread.get_absolute_url())
    return render(request, 'forum/thread_detail.html', {'thread': thread, 'replies': replies})


# ==============================
# TUTORES
# ==============================
# ... (Tu código de TUTORES - Omitido por brevedad) ...
@login_required
def tutor_list(request):
    search_query = request.GET.get('q', '')
    tutors = TutorProfile.objects.filter(activo=True).select_related('user').annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews'),
        completed_tutorias=Count(
            'user__received_tutoring_requests',
            filter=Q(user__received_tutoring_requests__status='completed')
        )
    )
    if search_query:
        tutors = tutors.filter(
            Q(user__username__icontains=search_query) |
            Q(materias__icontains=search_query)
        ).distinct()
    tutors = tutors.order_by('-verificado', 'user__username')
    context = {
        'tutors': tutors,
        'search_query': search_query
    }
    return render(request, 'tutors/list.html', context)

@login_required
def tutor_detail(request, username):
    tutor_profile = get_object_or_404(TutorProfile, user__username=username, activo=True)
    reviews = tutor_profile.reviews.all()
    review_count = reviews.count()
    average_rating = 0
    if review_count > 0:
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if request.method == 'POST':
        if request.user.is_authenticated and request.user != tutor_profile.user:
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            if rating:
                Review.objects.update_or_create(
                    tutor=tutor_profile,
                    student=request.user,
                    defaults={'rating': int(rating), 'comment': comment}
                )
                messages.success(request, '¡Tu reseña ha sido publicada!')
                return redirect('tutor_detail', username=username)
            else:
                messages.error(request, 'Debes seleccionar una calificación.')
    materias_list = []
    if tutor_profile.materias:
        materias_list = [m.strip() for m in tutor_profile.materias.split(',') if m.strip()]
    context = {
        'tutor_profile': tutor_profile,
        'reviews': reviews,
        'review_count': review_count,
        'average_rating': average_rating,
        'materias_list': materias_list
    }
    return render(request, 'tutors/detail.html', context)

@login_required
def become_tutor(request):
    tutor_profile, created = TutorProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = TutorProfileForm(request.POST, instance=tutor_profile)
        if form.is_valid():
            profile = form.save()
            if not profile.activo:
                profile.activo = True
                profile.save(update_fields=['activo'])
            messages.success(request, '¡Tu perfil de tutor ha sido actualizado y activado!')
            return redirect('tutor_detail', username=request.user.username)
    else:
        form = TutorProfileForm(instance=tutor_profile)
    return render(request, 'tutors/become_tutor.html', {'form': form})


# ==============================
# SOLICITUDES DE TUTORÍA (ACTUALIZADO CON MENSAJE)
# ==============================
@login_required
def request_tutoring(request, username):
    # ... (Tu código de request_tutoring - Omitido por brevedad) ...
    tutor_user = get_object_or_404(User, username=username)
    tutor_profile = get_object_or_404(TutorProfile, user=tutor_user, activo=True)

    if request.method == 'POST':
        form = TutoringRequestForm(request.POST)
        if form.is_valid():
            tutoring_request = form.save(commit=False)
            tutoring_request.student = request.user
            tutoring_request.tutor = tutor_user
            tutoring_request.save()

            subject_email = f'Nueva solicitud de tutoría de {request.user.username} en UniversoE'
            message_email = (
                f'¡Hola {tutor_user.username}!\n\n'
                f'Has recibido una nueva solicitud de tutoría de parte de {request.user.username}.\n\n'
                f'Mensaje del estudiante:\n"{tutoring_request.message}"\n\n'
                f'Correo del estudiante: {request.user.email}\n'
            )
            try:
                send_mail(subject_email, message_email, settings.DEFAULT_FROM_EMAIL, [tutor_user.email])
                messages.success(request, '¡Tu solicitud fue enviada al tutor!')
            except Exception as e:
                log.error(f"Error enviando email: {e}")
                messages.warning(request, 'Solicitud enviada, pero falló el correo de notificación.')

            return redirect('tutor_detail', username=tutor_user.username)
    else:
        form = TutoringRequestForm()

    return render(request, 'tutors/request_tutoring.html', {'form': form, 'tutor_profile': tutor_profile})


@login_required
def manage_tutoring_requests(request):
    # Lógica POST para actualizar estado (se mantiene igual)
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        new_status = request.POST.get('new_status')
        if new_status not in ['accepted', 'rejected', 'completed']:
            messages.error(request, 'Acción no válida.')
            return redirect('manage_tutoring_requests')
        try:
            tutoring_request = TutoringRequest.objects.get(id=request_id, tutor=request.user)
            tutoring_request.status = new_status
            tutoring_request.save()
            messages.success(request, '¡Solicitud actualizada!')
        except TutoringRequest.DoesNotExist:
            messages.error(request, 'No se encontró la solicitud o no tienes permiso.')
        return redirect('manage_tutoring_requests')

    # Lógica GET para mostrar la página
    
    # --- ¡CAMBIO AQUÍ! Añadido el mensaje informativo ---
    messages.info(request, '💡 ¡Recuerda! Solo las tutorías marcadas como "Completadas" ✅ suman a tu contador en el perfil. ¡Gestiona tus solicitudes para mostrar tu impacto!')
    # --- FIN DEL CAMBIO ---

    pending_requests = TutoringRequest.objects.filter(
        tutor=request.user,
        status='pending'
    ).select_related('student').order_by('created_at')
    other_requests = TutoringRequest.objects.filter(
        tutor=request.user
    ).exclude(
        status='pending'
    ).select_related('student').order_by('-updated_at')
    
    context = {
        'pending_requests': pending_requests,
        'other_requests': other_requests
    }
    return render(request, 'tutors/manage_requests.html', context)

# ==============================
# IA y PDF
# ==============================
# ... (Tu código de IA y PDF - Omitido por brevedad) ...
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/v1")

def _ai_make_guide(topic: str, level: str, n_ex: int) -> str:
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise RuntimeError("DEEPSEEK_API_KEY no está configurada.")
    messages_chat = [{"role": "system", "content": "Eres un profesor que genera guías claras en español. Devuelve Markdown con: 1) Objetivos, 2) Teoría con ejemplos, 3) Ejercicios, 4) Pautas."}, {"role": "user", "content": f"Tema: {topic}\nNivel: {level}\nEjercicios: {n_ex}"}]
    resp = client.chat.completions.create(model="deepseek-chat", messages=messages_chat, temperature=0.3, max_tokens=2048)
    return resp.choices[0].message.content.strip()

@login_required
def guia_inteligente(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == "POST":
        topic = (request.POST.get("topic") or "").strip()
        level = (request.POST.get("level") or "Universitario").strip()
        try:
            n_ex = int(request.POST.get("ejercicios") or 5)
        except ValueError:
            n_ex = 5
        if not topic:
            return HttpResponse("Debes ingresar un tema.", status=400)
        try:
            result = _ai_make_guide(topic, level, n_ex)
            if is_ajax:
                html_result = render_to_string('ai/resultado.html', {'result': result})
                return HttpResponse(html_result)
            else:
                return render(request, "ai/guia.html", {"result": result})
        except Exception as e:
            log.error(f"Error IA: {e}")
            if is_ajax:
                return HttpResponse(f"Hubo un error al generar la guía: {e}", status=500)
            messages.error(request, f"Error al generar laG guía: {e}")
    return render(request, "ai/guia.html", {"result": None})

@login_required
def guia_descargar_pdf(request):
    if request.method == 'GET':
        markdown_content = request.GET.get('guide_content', '')
        if not markdown_content:
            messages.error(request, "No se proporcionó contenido para el PDF.")
            return redirect('guia_inteligente')
        html_content = markdown.markdown(markdown_content, extensions=['fenced_code'])
        rendered_html = render_to_string('ai/guia_pdf.html', {'content': html_content})
        pdf_file = HTML(string=rendered_html, base_url=request.build_absolute_uri()).write_pdf()
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="guia_de_estudio.pdf"'
        return response
    return redirect('guia_inteligente')


# ==============================
# Salas de Estudio
# ==============================
# ... (Tu código de Salas de Estudio - Omitido por brevedad) ...
@login_required
def study_room_list(request):
    """
    Muestra la lista de salas de estudio activas y permite crear nuevas.
    """
    if request.method == 'POST':
        form = StudyRoomForm(request.POST)
        if form.is_valid():
            study_room = form.save(commit=False)
            study_room.creador = request.user
            study_room.save()
            messages.success(request, f'¡Sala "{study_room.nombre}" creada con éxito!')
            return redirect(study_room.get_absolute_url())
        else:
            messages.error(request, 'Hubo un error al crear la sala. Revisa el formulario.')
    else:
        form = StudyRoomForm()

    now = timezone.now()
    active_rooms = StudyRoom.objects.filter(
        Q(es_temporal=False) | Q(es_temporal=True, creado_en__gte=now - timezone.timedelta(hours=6))
    ).select_related('creador', 'ramo').order_by('-creado_en')

    context = {
        'study_rooms': active_rooms,
        'form': form
    }
    return render(request, 'study_rooms/list.html', context)


@login_required
def study_room_detail(request, pk):
    """
    Muestra el detalle de una sala de estudio específica y maneja el chat.
    """
    study_room = get_object_or_404(StudyRoom.objects.select_related('creador', 'ramo'), pk=pk)

    if request.method == 'POST':
        content = request.POST.get('message_content', '').strip()
        if content:
            ChatMessage.objects.create(
                room=study_room,
                author=request.user,
                content=content
            )
            return redirect('study_room_detail', pk=pk)
        else:
            messages.warning(request, 'No puedes enviar un mensaje vacío.')

    chat_messages = study_room.messages.select_related('author').order_by('timestamp')

    context = {
        'room': study_room,
        'chat_messages': chat_messages
    }
    return render(request, 'study_rooms/detail.html', context)