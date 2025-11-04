from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

# User Profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    level = models.IntegerField(default=1)
    total_points = models.IntegerField(default=0)
    streak_count = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def add_points(self, points):
        self.total_points += points
        self.level = (self.total_points // 100) + 1
        self.save()
    
    def update_streak(self):
        today = timezone.now().date()
        if self.last_activity_date:
            days_diff = (today - self.last_activity_date).days
            if days_diff == 1:
                self.streak_count += 1
            elif days_diff > 1:
                self.streak_count = 1
        else:
            self.streak_count = 1
        self.last_activity_date = today
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Task
class Task(models.Model):
    CATEGORY_CHOICES = [
        ('homework', 'Homework'),
        ('reading', 'Reading'),
        ('revision', 'Revision'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def complete_task(self):
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()
            
            points = {'low': 10, 'medium': 20, 'high': 30}[self.priority]
            Reward.objects.create(
                user=self.user,
                task=self,
                points_earned=points,
                badge_name=self.check_badge()
            )
            
            self.user.profile.add_points(points)
            self.user.profile.update_streak()
            self.update_progress_tracker()

    def uncomplete_task(self):
        """Undo task completion - reverse points and rewards"""
        if self.is_completed:
            # Get the reward for this task
            reward = Reward.objects.filter(task=self).first()
            
            if reward:
                # Subtract points from user profile
                points = reward.points_earned
                self.user.profile.total_points = max(0, self.user.profile.total_points - points)
                self.user.profile.level = (self.user.profile.total_points // 100) + 1
                self.user.profile.save()
                
                # Delete the reward
                reward.delete()
            
            # Mark task as incomplete
            self.is_completed = False
            self.completed_at = None
            self.save()
            
            # Update progress tracker
            self.update_progress_tracker()
            
            return True
        return False
    
    def check_badge(self):
        completed_count = Task.objects.filter(user=self.user, is_completed=True).count()
        badges = {
            1: "First Steps",
            5: "Getting Started",
            10: "Task Master",
            25: "Productivity Pro",
            50: "Study Champion",
            100: "Academic Legend"
        }
        return badges.get(completed_count)
    
    def update_progress_tracker(self):
        tracker, created = ProgressTracker.objects.get_or_create(user=self.user)
        tracker.total_tasks_completed = Task.objects.filter(user=self.user, is_completed=True).count()
        tracker.weekly_streak = self.user.profile.streak_count
        tracker.updated_at = timezone.now()
        tracker.save()

# Rewards
class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    badge_name = models.CharField(max_length=100, null=True, blank=True)
    date_awarded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_awarded']
    
    def __str__(self):
        return f"{self.user.username} - {self.points_earned} points"
    
#Quote
class Quote(models.Model):
    CATEGORY_CHOICES = [
        ('motivation', 'Motivation'),
        ('focus', 'Focus'),
        ('time-management', 'Time Management'),
    ]
    
    content = models.TextField()
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='motivation')
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.author}: {self.content[:50]}..."
    
#StudyTips
class StudyTip(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('moderate', 'Moderate'),
        ('hard', 'Hard'),
    ]
    
    content = models.TextField()
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='moderate')
    context_tag = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.context_tag}: {self.content[:50]}..."
    
#Progress Track
class ProgressTracker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    total_tasks_completed = models.IntegerField(default=0)
    weekly_streak = models.IntegerField(default=0)
    average_completion_time = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Progress"
    
#Chat bot
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    is_bot = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        sender = "Bot" if self.is_bot else self.user.username
        return f"{sender}: {self.message[:50]}..."
    
