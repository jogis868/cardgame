from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    index, role_redirect_view, profile_view, create_room, join_room, student_results, get_user_role, 
    teacher_profile, teacher_room_detail, update_score, update_room_name, delete_room, room_cards, get_room_cards,
    delete_card, generate_ai_cards, register_view, student_progress
)

urlpatterns = [
    # Authentication and General
    path('', index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('role-redirect/', role_redirect_view, name='role_redirect'),
    path('accounts/profile/', profile_view, name='profile'),
    path('get-room-cards/<str:room_code>/', get_room_cards, name='get_room_cards'),
    path('register/', register_view, name='register'),

    # Student-Specific URLs
    path('student/join-room/', join_room, name='join_room'),
    path('student/results/', student_results, name='student_results'),
    path('student/update-score/', update_score, name='update_score'),
    path('student/get-user-role/', get_user_role, name='get_user_role'),
    path('student/progress/', student_progress, name='student_progress'),

    # Teacher-Specific URLs
    path('teacher/rooms/', teacher_profile, name='teacher_profile'),
    path('teacher/create-room/', create_room, name='create_room'),
    path('teacher/rooms/<int:room_id>/', teacher_room_detail, name='teacher_room_detail'),
    path('teacher/rooms/<int:room_id>/update-name/', update_room_name, name='update_room_name'),
    path('teacher/rooms/<int:room_id>/delete/', delete_room, name='delete_room'),
    path('teacher/rooms/<str:room_code>/cards/', room_cards, name='room_cards'),
    path('teacher/rooms/delete-card/<int:card_id>/', delete_card, name='delete_card'),
    path('teacher/rooms/<int:room_id>/generate-ai-cards/', generate_ai_cards, name='generate_ai_cards'),

]