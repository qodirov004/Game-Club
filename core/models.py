from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import math

class Game(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='games/', null=True, blank=True)
    table_count = models.IntegerField(verbose_name="Stollar soni")
    standard_price = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class GameSession(models.Model):    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='sessions')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    pause_time = models.DateTimeField(null=True, blank=True)
    total_paused_duration = models.DurationField(default=timezone.timedelta(0))
    is_paid = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.game.name} - {self.get_status_display()}"

    def get_duration(self):
        if self.status == 'completed' and self.end_time:
            # For completed sessions, calculate from start to end minus paused time
            duration = self.end_time - self.start_time - self.total_paused_duration
        elif self.status == 'paused' and self.pause_time:
            # For paused sessions, calculate from start to pause minus paused time
            duration = self.pause_time - self.start_time - self.total_paused_duration
        else:
            # For active sessions, calculate from start to now minus paused time
            duration = timezone.now() - self.start_time - self.total_paused_duration
        
        # Return duration in seconds
        return duration.total_seconds()

    def get_duration_display(self):
        seconds = self.get_duration()
        hours = math.floor(seconds / 3600)
        minutes = math.floor((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"

    def get_cost(self):
        duration_hours = self.get_duration() / 3600
        return duration_hours * float(self.game.standard_price)

    def pause(self):
        if self.status == 'active':
            self.status = 'paused'
            self.pause_time = timezone.now()
            self.save()

    def resume(self):
        if self.status == 'paused' and self.pause_time:
            # Calculate paused duration
            paused_duration = timezone.now() - self.pause_time
            # Add to total paused duration
            self.total_paused_duration += paused_duration
            # Update status
            self.status = 'active'
            self.pause_time = None
            self.save()

    def complete(self):
        if self.status in ['active', 'paused']:
            # If paused, add final paused duration
            if self.status == 'paused' and self.pause_time:
                paused_duration = timezone.now() - self.pause_time
                self.total_paused_duration += paused_duration
            
            self.status = 'completed'
            self.end_time = timezone.now()
            self.save()

class Statistic(models.Model):
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    date = models.DateField()
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    games_count = models.IntegerField(default=0)
    total_hours = models.PositiveBigIntegerField(default=0)
    revenue = models.PositiveBigIntegerField(default=0)
    popular_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    average_session = models.CharField(max_length=20, default="0s 0m")
    
    class Meta:
        unique_together = ('date', 'period')
    
    def __str__(self):
        return f"{self.get_period_display()} - {self.date}"