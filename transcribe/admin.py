from django.contrib import admin

from .models import TranscriptionSurvey, MessageToTranscribe, Transcription


@admin.register(TranscriptionSurvey)
class TranscriptionSurveyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(MessageToTranscribe)
class MessageToTranscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'given')
    list_filter = ('survey', )


@admin.register(Transcription)
class TranscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'text')
    list_filter = ('message', )
