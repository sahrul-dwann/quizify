from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import LoginForm

app_name = 'quizzes'

urlpatterns = [
    path('', views.home, name='home'),
    path('kuis/', views.quiz_catalog, name='catalog'),
    path('kuis/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('kuis/<int:quiz_id>/mulai/', views.start_quiz, name='start_quiz'),
    path('percobaan/<int:attempt_id>/', views.take_quiz, name='take_quiz'),
    path(
        'percobaan/<int:attempt_id>/jawaban/',
        views.save_attempt_answer,
        name='save_attempt_answer',
    ),
    path(
        'percobaan/<int:attempt_id>/selesai/',
        views.finish_attempt,
        name='finish_attempt',
    ),
    path('hasil/<int:attempt_id>/', views.attempt_result, name='attempt_result'),
    path('riwayat/', views.attempt_history, name='attempt_history'),
    path('daftar/', views.register, name='register'),
    path(
        'akun/masuk/',
        auth_views.LoginView.as_view(
            template_name='quizzes/login.html',
            authentication_form=LoginForm,
        ),
        name='login',
    ),
    path(
        'akun/keluar/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
]
