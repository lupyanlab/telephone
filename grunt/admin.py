from django.contrib import admin

from .models import Game, Chain, Message


def kill_message(modeladmin, request, queryset):
    """ Set the selected messages num_children to zero. """
    queryset.update(num_children=0)
kill_message.short_description = "Prevent selected messages from replicating"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game')
    list_filter = ('game', )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chain', 'generation', 'parent', 'audio', 'num_children')
    actions = [kill_message, ]
    list_filter = ('chain', )
