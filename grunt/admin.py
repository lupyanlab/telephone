from django.contrib import admin

from .models import Game, Chain, Message

@admin.register(Game, Chain)
class GameAdmin(admin.ModelAdmin):
    pass

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chain', 'generation', 'parent', 'audio')
