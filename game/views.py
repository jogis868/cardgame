from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import google.generativeai as genai
import os
import re
import ast
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.core import serializers
from .models import Room, Card, CustomUser, StudentResult
from django.db.models import Max, Count
from django.contrib.auth.models import User
from .forms import RegistrationForm
from .models import CustomUser

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Utility / Login / Profile Views
# ------------------------------------------------------------------------------

@login_required
def index(request):
    joined_room_code = request.session.get("joined_room_code", None)
    return render(request, "index.html", {"joined_room_code": joined_room_code})

def my_custom_login_view(request):
    return render(request, 'login_template.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html')

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = form.cleaned_data['role']  # ✅ Set role directly on CustomUser
            user.save()

            login(request, user)
            return redirect('role_redirect')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def role_redirect_view(request):
    """
    After login, send the teacher to their room list and the student to the index.
    """
    if request.user.role == 'teacher':
        return redirect('teacher_profile')
    else:
        return redirect('index')

@login_required
def student_progress(request):
    if request.user.role != 'student':
        messages.error(request, "Tik mokiniai gali matyti savo progresą")
        return redirect('index')

    # 1. Savo progresas
    my_results = (
        StudentResult.objects.filter(student=request.user)
        .values('room__code', 'room__name')
        .annotate(times_played=Count('id'), best_score=Max('score'))
    )

    # 2. Visi žaidėjai
    leaderboard = (
        StudentResult.objects.values('student__username')
        .annotate(total_score=Max('score'))
        .order_by('-total_score')
    )

    # 3. Pridėti pozicijas
    for idx, player in enumerate(leaderboard, start=1):
        player['position'] = idx

    return render(request, 'student_progress.html', {
        'my_results': my_results,
        'leaderboard': leaderboard,
    })

@csrf_exempt
@login_required
def generate_ai_cards(request, room_id):
    if request.method == 'POST' and request.user.role == 'teacher':
        try:
            room = Room.objects.get(pk=room_id, teacher=request.user)
        except Room.DoesNotExist:
            messages.error(request, "Kambarys nerastas arba nesate jo savininkas")
            return redirect('teacher_profile')

        theme = request.POST.get("theme", "").strip()
        if not theme:
            messages.error(request, "Pateikite temą")
            return redirect('teacher_room_detail', room_id=room_id)

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

        prompt = f"""
        Generate 20 educational flashcards on the topic "{theme}". 
        Strictly return a valid Python list of dictionaries using single quotes, no trailing commas. Example:
        [
        {{'term': 'Term1', 'definition': 'Definition1'}},
        ...
        ]
        Do not return any explanation or formatting — only the list.
        """

        try:
            response = model.generate_content(prompt)
            content = response.text

            # Use regex to extract the first JSON array
            match = re.search(r"\[\s*{.*?}\s*\]", content, re.DOTALL)
            if not match:
                raise ValueError("Could not extract JSON array from Gemini response")

            json_data = match.group(0)
            card_data = ast.literal_eval(json_data)

            created = 0
            for item in card_data:
                if 'term' in item and 'definition' in item:
                    Card.objects.create(
                        room=room,
                        front_text=item['term'],
                        back_text=item['definition']
                    )
                    created += 1
            messages.success(request, f"{created} kortelės sėkmingai sugeneruotos")

        except Exception as e:
            logger.error(f"Gemini klaida: {e}")
            messages.error(request, "Įvyko klaida generuojant korteles su Gemini. Bandykite dar kartą.")

        return redirect('teacher_room_detail', room_id=room_id)

    return JsonResponse({"error": "Neteisingas užklausos metodas arba prieiga uždrausta"}, status=400)


@login_required
def get_user_role(request):
    """
    Display the logged-in user’s role within the game interface.
    """
    role = getattr(request.user, "role", None)
    if not role:
        messages.error(request, "Role not found for user")
        return redirect('profile')
    messages.info(request, f"Jūsų rolė: {role}")
    # Render a simple page that shows the user’s role.
    return render(request, "role.html", {"role": role})

# ------------------------------------------------------------------------------
# Teacher and Student Room Views
# ------------------------------------------------------------------------------

@csrf_exempt
@login_required
def create_room(request):
    """
    Only teachers can create a room. After creation, display the room code in a success message.
    """
    if request.method == 'POST':
        if request.user.role != 'teacher':
            messages.error(request, "Tik mokytojai gali kurti kambarius")
            return redirect('teacher_profile')
        room = Room.objects.create(teacher=request.user)
        messages.success(request, f"Kambarys sukurtas. Kambario kodas: {room.code}")
        return redirect('teacher_room_detail', room_id=room.pk)
    else:
        messages.error(request, "Neteisingas užklausos metodas")
        return redirect('teacher_profile')


@csrf_exempt
@login_required
def join_room(request):
    if request.method == 'POST':
        room_code = request.POST.get("room_code", "").strip()
        if not room_code:
            messages.error(request, "Nepateiktas kambario kodas")
            return redirect('index')
        try:
            room = Room.objects.get(code=room_code)
        except Room.DoesNotExist:
            messages.error(request, "Kambarys nerastas")
            return redirect('index')

        if request.user.role != 'student':
            messages.error(request, "Tik mokiniai gali prisijungti prie kambario")
            return redirect('index')

        cards = list(room.cards.values('front_text', 'back_text'))
        print(f"Cards: {cards}")
        messages.success(request, "Prisijungta prie kambario sėkmingai!")
        return render(request, "index.html", {"room": room, "cards": cards, "joined": True})
    else:
        messages.error(request, "Neteisingas užklausos metodas")
        return redirect('index')


@login_required
def teacher_profile(request):
    """
    Display all rooms created by the logged-in teacher.
    """
    if request.user.role != 'teacher':
        messages.error(request, "Klaida: ne mokytojo profilis")
        return redirect('index')
    rooms = Room.objects.filter(teacher=request.user)
    return render(request, 'teacher_profile.html', {'rooms': rooms})


@login_required
def teacher_room_detail(request, room_id):
    if request.user.role != 'teacher':
        messages.error(request, "Klaida: ne mokytojo profilis")
        return redirect('teacher_profile')
    try:
        room = Room.objects.get(pk=room_id, teacher=request.user)
    except Room.DoesNotExist:
        messages.error(request, "Kambarys nerastas arba nesate jo savininkas")
        return redirect('teacher_profile')
    # Convert the QuerySet to a list of dictionaries
    cards = list(room.cards.values('id', 'front_text', 'back_text'))
    print(f"Cards for room {room_id}: {cards}")
    results = StudentResult.objects.filter(room=room).select_related('student')
    return render(request, 'teacher_room_detail.html', {
        'room': room,
        'cards': cards,
        'results': results
    })


@csrf_exempt
@login_required
def update_room_name(request, room_id):
    """
    Allow a teacher to update the room name.
    """
    if request.method == 'POST':
        if request.user.role != 'teacher':
            messages.error(request, "Tik mokytojai gali keisti kambario pavadinimą")
            return redirect('teacher_room_detail', room_id=room_id)
        try:
            room = Room.objects.get(pk=room_id, teacher=request.user)
        except Room.DoesNotExist:
            messages.error(request, "Kambarys nerastas arba nesate jo savininkas")
            return redirect('teacher_profile')
        # Get new name from a submitted form (or JSON if you support that)
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            new_name = data.get('name', '').strip()
        else:
            new_name = request.POST.get('name', '').strip()
        if not new_name:
            messages.error(request, "Nepateiktas naujas kambario pavadinimas")
            return redirect('teacher_room_detail', room_id=room_id)
        room.name = new_name
        room.save()
        messages.success(request, "Kambario pavadinimas atnaujintas")
        return redirect('teacher_room_detail', room_id=room_id)
    else:
        messages.error(request, "Neteisingas užklausos metodas")
        return redirect('teacher_room_detail', room_id=room_id)


@csrf_exempt
@login_required
def delete_room(request, room_id):
    """
    Allow a teacher to delete a room.
    """
    if request.method == 'POST':
        if request.user.role != 'teacher':
            messages.error(request, "Tik mokytojai gali naikinti kambarius")
            return redirect('teacher_room_detail', room_id=room_id)
        try:
            room = Room.objects.get(pk=room_id, teacher=request.user)
        except Room.DoesNotExist:
            messages.error(request, "Kambarys nerastas arba nesate jo savininkas")
            return redirect('teacher_profile')
        room.delete()
        messages.success(request, "Kambarys ištrintas sėkmingai")
        return redirect('teacher_profile')
    else:
        messages.error(request, "Neteisingas užklausos metodas")
        return redirect('teacher_room_detail', room_id=room_id)

@csrf_exempt
@login_required
def delete_card(request, card_id):
    """
    Handle the deletion of a card by its ID.
    """
    if request.method == 'DELETE':
        try:
            card = Card.objects.get(pk=card_id, room__teacher=request.user)
            card.delete()
            return JsonResponse({"message": "Kortelė ištrinta sėkmingai."}, status=200)
        except Card.DoesNotExist:
            return JsonResponse({"error": "Kortelė nerasta."}, status=404)
    return JsonResponse({"error": "Neteisingas užklausos metodas."}, status=400)


@csrf_exempt
@login_required
def room_cards(request, room_code):
    """
    For teachers or students: view the room’s cards. If POSTed by a teacher, add a new card.
    """
    try:
        room = Room.objects.get(code=room_code)
    except Room.DoesNotExist:
        messages.error(request, "Kambarys nerastas")
        return redirect('index')
    if request.method == 'GET':
        cards = list(room.cards.values('id', 'front_text', 'back_text'))
        return render(request, "room_cards.html", {"room": room, "cards": cards})
    elif request.method == 'POST':
        if request.user.role != 'teacher':
            messages.error(request, "Tik mokytojai gali pridėti korteles")
            return redirect('index', room_code=room_code)
        front_text = request.POST.get("front_text", "").strip()
        back_text = request.POST.get("back_text", "").strip()
        if not front_text or not back_text:
            messages.error(request, "Abu tekstai privalo būti pateikti")
            return redirect('teacher_room_detail', room_id=room.id)
        # Create and save the new card
        Card.objects.create(room=room, front_text=front_text, back_text=back_text)
        messages.success(request, "Kortelė pridėta")
        return redirect('teacher_room_detail', room_id=room.id)
    else:
        messages.error(request, "Neteisingas užklausos metodas")
        return redirect('index')


# ------------------------------------------------------------------------------
# Student Score & Teacher Results Views
# ------------------------------------------------------------------------------

import logging
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def update_score(request):
    if request.method == "POST":
        if request.user.role != "student":
            return JsonResponse({"error": "Only students can update scores"}, status=403)
        try:
            data = json.loads(request.body)
            room_code = data.get("room_code", "").strip()
            new_score = int(data.get("score", 0))

            if not room_code or new_score <= 0:
                return JsonResponse({"error": "Invalid data"}, status=400)

            room = Room.objects.get(code=room_code)
            result, created = StudentResult.objects.get_or_create(
                student=request.user, room=room, defaults={"score": new_score}
            )

            if not created and result.score < new_score:
                result.score = new_score
                result.save()

            return JsonResponse({"message": "Score updated"})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

@login_required
def student_results(request):
    if request.user.role != 'teacher':
        messages.error(request, "Tik mokytojai gali matyti mokinių rezultatus")
        return redirect('index')

    results = (
        StudentResult.objects.filter(room__teacher=request.user)
        .values('student__username', 'room__name', 'room__code')
        .annotate(best_score=Max('score'))
    )

    return render(request, "student_results.html", {"results": results})

@login_required
def get_room_cards(request, room_code):
    try:
        room = Room.objects.get(code=room_code)
        cards = list(room.cards.values('front_text', 'back_text'))
        return JsonResponse({"cards": cards})
    except Room.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)