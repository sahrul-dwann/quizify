from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AnswerOption, Question, Quiz, QuizAttempt


class HomePageTests(TestCase):
    def test_homepage_renders(self):
        response = self.client.get(reverse('quizzes:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quizzes/home.html')
        self.assertContains(response, 'Bikin belajar')


class QuizCatalogTests(TestCase):
    def test_catalog_only_shows_published_quizzes(self):
        published_quiz = Quiz.objects.create(
            title='Kuis publik',
            description='Deskripsi untuk kuis publik',
            is_published=True,
        )
        Quiz.objects.create(title='Kuis draft')

        response = self.client.get(reverse('quizzes:catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quizzes/quiz_catalog.html')
        self.assertContains(response, published_quiz.title)
        self.assertNotContains(response, 'Kuis draft')

    def test_catalog_shows_empty_state_when_no_quizzes_are_published(self):
        Quiz.objects.filter(
            title='Pemrograman Dasar hingga Menengah',
        ).update(is_published=False)
        response = self.client.get(reverse('quizzes:catalog'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Belum ada kuis')


class SeededQuizTests(TestCase):
    def test_programming_quiz_has_ten_questions_with_one_correct_option_each(self):
        quiz = Quiz.objects.get(title='Pemrograman Dasar hingga Menengah')
        questions = list(quiz.questions.prefetch_related('options'))

        self.assertTrue(quiz.is_published)
        self.assertEqual(len(questions), 10)
        for question in questions:
            options = list(question.options.all())
            self.assertEqual(len(options), 4)
            self.assertEqual(sum(option.is_correct for option in options), 1)


class QuizTakingTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='learner',
            password='test-password-123',
        )
        self.quiz = Quiz.objects.create(title='Kuis sains', is_published=True)
        self.question_one = Question.objects.create(
            quiz=self.quiz,
            text='Ibu kota Indonesia?',
            order=1,
        )
        self.correct_option_one = AnswerOption.objects.create(
            question=self.question_one,
            text='Jakarta',
            is_correct=True,
        )
        AnswerOption.objects.create(
            question=self.question_one,
            text='Bandung',
        )
        self.question_two = Question.objects.create(
            quiz=self.quiz,
            text='Berapakah 2 + 2?',
            order=2,
        )
        self.correct_option_two = AnswerOption.objects.create(
            question=self.question_two,
            text='4',
            is_correct=True,
        )
        AnswerOption.objects.create(question=self.question_two, text='5')

    def start_attempt(self):
        response = self.client.post(
            reverse('quizzes:start_quiz', args=[self.quiz.pk])
        )
        self.assertEqual(response.status_code, 302)
        return QuizAttempt.objects.get(
            user=self.user,
            quiz=self.quiz,
            completed_at__isnull=True,
        )

    def test_registration_creates_account_and_logs_user_in(self):
        response = self.client.post(
            reverse('quizzes:register'),
            {
                'username': 'new_learner',
                'password1': 'NoSimilar-Unique-293!Pass',
                'password2': 'NoSimilar-Unique-293!Pass',
            },
        )

        self.assertRedirects(response, reverse('quizzes:catalog'))
        self.assertTrue(
            get_user_model().objects.filter(username='new_learner').exists()
        )
        self.assertIn('_auth_user_id', self.client.session)

    def test_starting_quiz_requires_login(self):
        response = self.client.post(
            reverse('quizzes:start_quiz', args=[self.quiz.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('quizzes:login')))

    def test_quiz_page_renders_navigation_for_each_question(self):
        self.client.force_login(self.user)
        attempt = self.start_attempt()
        response = self.client.get(
            reverse('quizzes:take_quiz', args=[attempt.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-remaining-seconds="600"')
        self.assertContains(
            response,
            f'data-question-target="question_{self.question_one.pk}"',
        )
        self.assertContains(
            response,
            f'data-question-target="question_{self.question_two.pk}"',
        )

    def test_reloading_quiz_page_does_not_reset_timer(self):
        self.client.force_login(self.user)
        attempt = self.start_attempt()
        attempt.started_at = timezone.now() - timedelta(minutes=7)
        attempt.save(update_fields=('started_at',))

        response = self.client.get(
            reverse('quizzes:take_quiz', args=[attempt.pk])
        )

        self.assertContains(response, 'data-remaining-seconds="180"')
        self.assertContains(response, '03:00')

    def test_submission_saves_score_and_result_does_not_show_answers(self):
        self.client.force_login(self.user)
        attempt = self.start_attempt()
        self.client.post(
            reverse('quizzes:save_attempt_answer', args=[attempt.pk]),
            {
                'question_id': self.question_one.pk,
                'option_id': self.correct_option_one.pk,
            },
        )
        self.client.post(
            reverse('quizzes:save_attempt_answer', args=[attempt.pk]),
            {
                'question_id': self.question_two.pk,
                'option_id': self.correct_option_two.pk,
            },
        )
        response = self.client.post(
            reverse('quizzes:finish_attempt', args=[attempt.pk]),
            {
                f'question_{self.question_one.pk}': self.correct_option_one.pk,
                f'question_{self.question_two.pk}': self.correct_option_two.pk,
            },
        )

        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 2)
        self.assertEqual(attempt.total_questions, 2)
        self.assertRedirects(
            response,
            reverse('quizzes:attempt_result', args=[attempt.pk]),
        )

        result_response = self.client.get(response.url)
        self.assertContains(result_response, 'Kuis selesai')
        self.assertNotContains(result_response, 'Jakarta')
        self.assertNotContains(result_response, 'Bandung')

    def test_option_from_another_question_is_rejected(self):
        self.client.force_login(self.user)
        attempt = self.start_attempt()
        response = self.client.post(
            reverse('quizzes:save_attempt_answer', args=[attempt.pk]),
            {
                'question_id': self.question_one.pk,
                'option_id': self.correct_option_two.pk,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(attempt.score, 0)
        self.assertIsNone(attempt.completed_at)

    def test_expired_attempt_is_completed_from_saved_answers(self):
        self.client.force_login(self.user)
        attempt = self.start_attempt()
        response = self.client.post(
            reverse('quizzes:save_attempt_answer', args=[attempt.pk]),
            {
                'question_id': self.question_one.pk,
                'option_id': self.correct_option_one.pk,
            },
        )
        self.assertEqual(response.status_code, 204)

        attempt.started_at = timezone.now() - timedelta(minutes=11)
        attempt.save(update_fields=('started_at',))
        response = self.client.post(
            reverse('quizzes:save_attempt_answer', args=[attempt.pk]),
            {
                'question_id': self.question_two.pk,
                'option_id': self.correct_option_two.pk,
            },
        )

        self.assertEqual(response.status_code, 410)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 1)
        self.assertIsNotNone(attempt.completed_at)

    def test_attempt_history_is_private_to_the_logged_in_user(self):
        other_user = get_user_model().objects.create_user(
            username='another_learner',
            password='test-password-123',
        )
        other_quiz = Quiz.objects.create(
            title='Kuis privat orang lain',
            is_published=True,
        )
        QuizAttempt.objects.create(
            user=other_user,
            quiz=other_quiz,
            score=1,
            total_questions=1,
            completed_at=timezone.now(),
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse('quizzes:attempt_history'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, other_quiz.title)
