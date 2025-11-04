from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Task, UserProfile
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates a demo user with sample tasks'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating demo user...')
        
        # Create demo user
        username = 'demo'
        email = 'demo@studybuddy.com'
        password = 'demo123'
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Demo user created: {username}'))
        else:
            self.stdout.write(self.style.WARNING(f'Demo user already exists: {username}'))
        
        # Update profile
        profile = user.profile
        profile.total_points = 150
        profile.level = 2
        profile.streak_count = 5
        profile.save()
        
        # Create sample tasks
        now = timezone.now()
        
        sample_tasks = [
            {
                'title': 'Complete Math Homework',
                'description': 'Finish chapters 3-4 exercises',
                'category': 'homework',
                'priority': 'high',
                'due_date': now + timedelta(days=1),
                'is_completed': False
            },
            {
                'title': 'Read Biology Chapter 5',
                'description': 'Read and take notes on cellular respiration',
                'category': 'reading',
                'priority': 'medium',
                'due_date': now + timedelta(days=2),
                'is_completed': False
            },
            {
                'title': 'Revise History Notes',
                'description': 'Review WWI timeline and key events',
                'category': 'revision',
                'priority': 'medium',
                'due_date': now + timedelta(days=3),
                'is_completed': False
            },
            {
                'title': 'Prepare English Presentation',
                'description': 'Create slides for Shakespeare presentation',
                'category': 'homework',
                'priority': 'high',
                'due_date': now + timedelta(days=4),
                'is_completed': False
            },
            {
                'title': 'Chemistry Lab Report',
                'description': 'Write up results from last week\'s experiment',
                'category': 'homework',
                'priority': 'medium',
                'due_date': now + timedelta(days=5),
                'is_completed': False
            },
            {
                'title': 'Practice Spanish Vocabulary',
                'description': 'Learn 20 new words for upcoming test',
                'category': 'revision',
                'priority': 'low',
                'due_date': now + timedelta(days=7),
                'is_completed': False
            },
            {
                'title': 'Finished Physics Problem Set',
                'description': 'Completed all kinematics problems',
                'category': 'homework',
                'priority': 'high',
                'due_date': now - timedelta(days=1),
                'is_completed': True
            },
            {
                'title': 'Read Geography Chapter 2',
                'description': 'Learned about plate tectonics',
                'category': 'reading',
                'priority': 'medium',
                'due_date': now - timedelta(days=2),
                'is_completed': True
            },
        ]
        
        for task_data in sample_tasks:
            Task.objects.get_or_create(
                user=user,
                title=task_data['title'],
                defaults=task_data
            )
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(sample_tasks)} sample tasks'))
        self.stdout.write(self.style.SUCCESS(f'\nDemo credentials:\nUsername: {username}\nPassword: {password}'))