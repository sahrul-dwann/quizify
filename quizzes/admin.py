from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import AnswerOption, Question, Quiz, QuizAttempt


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')


class AnswerOptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        options = [
            form.cleaned_data
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get('DELETE', False)
            and form.cleaned_data.get('text')
        ]
        if len(options) < 2:
            raise ValidationError('Setidaknya harus ada dua pilihan jawaban.')
        if sum(option.get('is_correct', False) for option in options) != 1:
            raise ValidationError('Tandai tepat satu pilihan sebagai jawaban benar.')


class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    formset = AnswerOptionInlineFormSet
    extra = 2
    min_num = 2
    validate_min = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text', 'quiz__title')
    inlines = (AnswerOptionInline,)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'quiz',
        'score',
        'total_questions',
        'started_at',
        'completed_at',
    )
    list_filter = ('quiz', 'started_at', 'completed_at')
    search_fields = ('user__username', 'quiz__title')
    readonly_fields = (
        'user',
        'quiz',
        'score',
        'total_questions',
        'started_at',
        'completed_at',
    )

    def has_add_permission(self, request):
        return False
