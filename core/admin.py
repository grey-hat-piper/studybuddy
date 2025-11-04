from django.contrib import admin
from .models import UserProfile, Task, Reward, Quote, StudyTip, ProgressTracker, ChatMessage

# Register your models here.
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'level', 'total_points', 'streak_count']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'priority', 'due_date', 'is_completed']
    list_filter = ['category', 'priority', 'is_completed']

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'points_earned', 'badge_name', 'date_awarded']

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ['author', 'category', 'date_added']

@admin.register(StudyTip)
class StudyTipAdmin(admin.ModelAdmin):
    list_display = ['context_tag', 'difficulty_level', 'date_added']

@admin.register(ProgressTracker)
class ProgressTrackerAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_tasks_completed', 'weekly_streak', 'updated_at']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_preview', 'is_bot', 'created_at']
    list_filter = ['is_bot', 'created_at']
    search_fields = ['user__username', 'message']
    
    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message