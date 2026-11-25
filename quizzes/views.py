from datetime import timedelta
from math import ceil

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import RegistrationForm
from .models import AnswerOption, Question, Quiz, QuizAttempt

QUIZ_DURATION = timedelta(minutes=10)


def _attempt_session_key(attempt):
    return f'quiz_attempt_{attempt.pk}'


def _get_attempt_data(request, attempt):
    key = _attempt_session_key(attempt)
    data = request.session.get(key)
    if data is None:
        question_ids = list(
            attempt.quiz.questions.order_by('order', 'pk').values_list('pk', flat=True)
        )
        data = {'question_ids': question_ids, 'answers': {}}
        request.session[key] = data
    return data


def _complete_attempt(request, attempt):
    if attempt.completed_at is not None:
        return

    data = _get_attempt_data(request, attempt)
    answers = data.get('answers', {})
    questions = Question.objects.filter(
        quiz=attempt.quiz,
        pk__in=data.get('question_ids', []),
    ).prefetch_related('options')
    score = 0
    for question in questions:
        selected_id = answers.get(str(question.pk))
        if selected_id is None:
            continue
        if any(
            option.pk == int(selected_id) and option.is_correct
            for option in question.options.all()
        ):
            score += 1

    attempt.score = score
    attempt.completed_at = timezone.now()
    attempt.save(update_fields=('score', 'completed_at'))
    request.session.pop(_attempt_session_key(attempt), None)


def _render_attempt(request, attempt, form_error=None):
    data = _get_attempt_data(request, attempt)
    questions_by_id = {
        question.pk: question
        for question in Question.objects.filter(
            quiz=attempt.quiz,
            pk__in=data['question_ids'],
        ).prefetch_related('options')
    }
    questions = [
        questions_by_id[question_id]
        for question_id in data['question_ids']
        if question_id in questions_by_id
    ]
    deadline = attempt.started_at + QUIZ_DURATION
    remaining_seconds = max(0, ceil((deadline - timezone.now()).total_seconds()))
    remaining_time = (
        f'{remaining_seconds // 60:02d}:{remaining_seconds % 60:02d}'
    )
    selected_option_ids = [
        int(option_id)
        for option_id in data['answers'].values()
    ]
    return render(
        request,
        'quizzes/take_quiz.html',
        {
            'attempt': attempt,
            'quiz': attempt.quiz,
            'questions': questions,
            'form_error': form_error,
            'remaining_seconds': remaining_seconds,
            'remaining_time': remaining_time,
            'selected_option_ids': selected_option_ids,
        },
    )


def home(request):
    return render(request, 'quizzes/home.html')


def quiz_catalog(request):
    quizzes = Quiz.objects.filter(is_published=True).annotate(
        question_count=Count('questions'),
    )
    return render(request, 'quizzes/quiz_catalog.html', {'quizzes': quizzes})


def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_published=True)
    question_count = quiz.questions.count()
    return render(
        request,
        'quizzes/quiz_detail.html',
        {'quiz': quiz, 'question_count': question_count},
    )


@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Akun berhasil dibuat. Selamat datang di Quizify!')
            return redirect('quizzes:catalog')
    else:
        form = RegistrationForm()

    return render(request, 'quizzes/register.html', {'form': form})


@login_required
@require_POST
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id, is_published=True)
    questions = list(quiz.questions.prefetch_related('options'))
    if not questions or any(
        len(question.options.all()) < 2
        or sum(option.is_correct for option in question.options.all()) != 1
        for question in questions
    ):
        messages.info(request, 'Kuis ini belum siap dikerjakan.')
        return redirect('quizzes:quiz_detail', quiz_id=quiz.pk)

    with transaction.atomic():
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=0,
            total_questions=len(questions),
        )
    request.session[_attempt_session_key(attempt)] = {
        'question_ids': [question.pk for question in questions],
        'answers': {},
    }
    return redirect(
        'quizzes:take_quiz',
        attempt_id=attempt.pk,
    )


@login_required
@require_GET
def take_quiz(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz'),
        pk=attempt_id,
        user=request.user,
    )
    if attempt.completed_at is not None:
        return redirect('quizzes:attempt_result', attempt_id=attempt.pk)
    if timezone.now() >= attempt.started_at + QUIZ_DURATION:
        _complete_attempt(request, attempt)
        return redirect('quizzes:attempt_result', attempt_id=attempt.pk)
    return _render_attempt(request, attempt)


@login_required
@require_POST
def save_attempt_answer(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz'),
        pk=attempt_id,
        user=request.user,
    )
    if attempt.completed_at is not None:
        return HttpResponse(status=409)
    if timezone.now() >= attempt.started_at + QUIZ_DURATION:
        _complete_attempt(request, attempt)
        return HttpResponse(status=410)

    data = _get_attempt_data(request, attempt)
    try:
        question_id = int(request.POST.get('question_id', ''))
        option_id = int(request.POST.get('option_id', ''))
    except (TypeError, ValueError):
        return HttpResponseBadRequest('Invalid answer.')

    if question_id not in data['question_ids']:
        return HttpResponseBadRequest('Invalid question.')
    if not AnswerOption.objects.filter(
        pk=option_id,
        question_id=question_id,
        question__quiz=attempt.quiz,
    ).exists():
        return HttpResponseBadRequest('Invalid option.')

    data['answers'][str(question_id)] = option_id
    request.session[_attempt_session_key(attempt)] = data
    return HttpResponse(status=204)


@login_required
@require_POST
def finish_attempt(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz'),
        pk=attempt_id,
        user=request.user,
    )
    if attempt.completed_at is not None:
        return redirect('quizzes:attempt_result', attempt_id=attempt.pk)
    if timezone.now() >= attempt.started_at + QUIZ_DURATION:
        _complete_attempt(request, attempt)
        return redirect('quizzes:attempt_result', attempt_id=attempt.pk)

    data = _get_attempt_data(request, attempt)
    answers = data['answers']
    questions = list(
        Question.objects.filter(
            quiz=attempt.quiz,
            pk__in=data['question_ids'],
        ).prefetch_related('options')
    )
    selected_options = {}
    for question in questions:
        selected_id = request.POST.get(f'question_{question.pk}')
        if not selected_id:
            selected_id = answers.get(str(question.pk))
        try:
            selected_id = int(selected_id)
        except (TypeError, ValueError):
            return _render_attempt(
                request,
                attempt,
                'Pilih satu jawaban untuk setiap pertanyaan.',
            )

        option = next(
            (choice for choice in question.options.all() if choice.pk == selected_id),
            None,
        )
        if option is None:
            return HttpResponseBadRequest('Invalid option.')
        selected_options[question.pk] = option.pk

    data['answers'].update(
        {str(question_id): option_id for question_id, option_id in selected_options.items()}
    )
    request.session[_attempt_session_key(attempt)] = data
    _complete_attempt(request, attempt)
    return redirect('quizzes:attempt_result', attempt_id=attempt.pk)


@login_required
def attempt_result(request, attempt_id):
    attempt = get_object_or_404(
        QuizAttempt.objects.select_related('quiz').filter(completed_at__isnull=False),
        pk=attempt_id,
        user=request.user,
    )
    return render(request, 'quizzes/attempt_result.html', {'attempt': attempt})


@login_required
def attempt_history(request):
    attempts = request.user.quiz_attempts.filter(
        completed_at__isnull=False,
    ).select_related('quiz')
    return render(request, 'quizzes/attempt_history.html', {'attempts': attempts})
