from django.conf import settings
from django.db import models
from django.utils import timezone


class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at', '-pk']
        verbose_name_plural = 'quizzes'

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'pk']

    def __str__(self):
        return f'{self.quiz.title}: {self.text[:50]}'


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='options',
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['pk']

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.PROTECT,
        related_name='attempts',
    )
    score = models.PositiveIntegerField()
    total_questions = models.PositiveIntegerField()
    started_at = models.DateTimeField(default=timezone.now, editable=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-started_at', '-pk']

    def __str__(self):
        return f'{self.user} - {self.quiz} ({self.score}/{self.total_questions})'
