from django.contrib import admin

from .models import Survey, Question, Response


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'given', 'answer')
    list_filter = ('survey', )


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'selection')
    list_filter = ('question', 'selection')
