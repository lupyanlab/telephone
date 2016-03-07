from django.contrib import admin

from .models import Game, Chain, Message


def reject_message(modeladmin, request, queryset):
    """Batch reject messages."""
    queryset.update(rejected=True)
reject_message.short_description = "Prevent selected messages from replicating"

def verify_message(modeladmin, request, queryset):
    """Batch verify messages."""
    queryset.update(verified=True)
verify_message.short_description = "Mark selected messages as verified"

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Chain)
class ChainAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'game')
    list_filter = ('game', )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chain', 'generation', 'parent', 'audio', 'num_children', 'rejected', 'verified')
    list_filter = ('chain', 'rejected', 'verified')
    actions = [reject_message, verify_message]
