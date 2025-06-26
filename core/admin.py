from django.contrib import admin
from .models import Game, GameSession, Statistic

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard_price', 'image', 'created_at')
    search_fields = ('name',)

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('game', 'status', 'start_time', 'end_time', 'is_paid', 'created_by')
    list_filter = ('status', 'is_paid')
    search_fields = ('game__name', 'created_by__username')
    date_hierarchy = 'start_time'

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('date', 'period', 'games_count', 'total_hours', 'revenue', 'popular_game')
    list_filter = ('period',)
    date_hierarchy = 'date'