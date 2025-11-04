from django.core.management.base import BaseCommand
from core.models import Quote, StudyTip

class Command(BaseCommand):
    help = 'Seeds the database with initial quotes and study tips'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        
        # Quotes
        quotes_data = [
            {
                'content': 'The future belongs to those who believe in the beauty of their dreams.',
                'author': 'Eleanor Roosevelt',
                'category': 'motivation'
            },
            {
                'content': 'Success is not final, failure is not fatal: it is the courage to continue that counts.',
                'author': 'Winston Churchill',
                'category': 'motivation'
            },
            {
                'content': 'The only way to do great work is to love what you do.',
                'author': 'Steve Jobs',
                'category': 'motivation'
            },
            {
                'content': 'Concentrate all your thoughts upon the work in hand. The sun\'s rays do not burn until brought to a focus.',
                'author': 'Alexander Graham Bell',
                'category': 'focus'
            },
            {
                'content': 'You don\'t have to be great to start, but you have to start to be great.',
                'author': 'Zig Ziglar',
                'category': 'motivation'
            },
            {
                'content': 'Time is what we want most, but what we use worst.',
                'author': 'William Penn',
                'category': 'time-management'
            },
            {
                'content': 'The key is not to prioritize what\'s on your schedule, but to schedule your priorities.',
                'author': 'Stephen Covey',
                'category': 'time-management'
            },
            {
                'content': 'Don\'t watch the clock; do what it does. Keep going.',
                'author': 'Sam Levenson',
                'category': 'time-management'
            },
            {
                'content': 'Focus on being productive instead of busy.',
                'author': 'Tim Ferriss',
                'category': 'focus'
            },
            {
                'content': 'The secret of getting ahead is getting started.',
                'author': 'Mark Twain',
                'category': 'motivation'
            },
        ]

        for quote_data in quotes_data:
            Quote.objects.get_or_create(**quote_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(quotes_data)} quotes'))

        # Study Tips
        tips_data = [
            {
                'content': 'Use the Pomodoro Technique: Study for 25 minutes, then take a 5-minute break. After 4 sessions, take a longer 15-30 minute break.',
                'difficulty_level': 'easy',
                'context_tag': 'concentration'
            },
            {
                'content': 'Create a dedicated study space free from distractions. Your brain will associate this space with focus and productivity.',
                'difficulty_level': 'easy',
                'context_tag': 'planning'
            },
            {
                'content': 'Practice active recall: Instead of rereading notes, test yourself on the material. This strengthens memory retention.',
                'difficulty_level': 'moderate',
                'context_tag': 'exam-prep'
            },
            {
                'content': 'Break large tasks into smaller, manageable chunks. This makes them less overwhelming and easier to complete.',
                'difficulty_level': 'easy',
                'context_tag': 'planning'
            },
            {
                'content': 'Use the Feynman Technique: Explain concepts in simple terms as if teaching someone else. This reveals gaps in understanding.',
                'difficulty_level': 'moderate',
                'context_tag': 'exam-prep'
            },
            {
                'content': 'Study the most challenging material when your energy is highest, typically in the morning or after breaks.',
                'difficulty_level': 'easy',
                'context_tag': 'concentration'
            },
            {
                'content': 'Create mind maps to visualize connections between concepts. This helps with both understanding and memory.',
                'difficulty_level': 'moderate',
                'context_tag': 'exam-prep'
            },
            {
                'content': 'Set specific, measurable goals for each study session. Instead of "study math", aim for "complete 10 algebra problems".',
                'difficulty_level': 'easy',
                'context_tag': 'planning'
            },
            {
                'content': 'Use spaced repetition: Review material at increasing intervals (1 day, 3 days, 1 week) to strengthen long-term memory.',
                'difficulty_level': 'hard',
                'context_tag': 'exam-prep'
            },
            {
                'content': 'Eliminate digital distractions: Use apps to block social media during study time or leave your phone in another room.',
                'difficulty_level': 'easy',
                'context_tag': 'concentration'
            },
            {
                'content': 'Get enough sleep! Your brain consolidates learning during sleep. Aim for 7-9 hours nightly.',
                'difficulty_level': 'easy',
                'context_tag': 'concentration'
            },
            {
                'content': 'Use color-coding in your notes to categorize information. Different colors help create visual associations and improve recall.',
                'difficulty_level': 'easy',
                'context_tag': 'exam-prep'
            },
            {
                'content': 'Practice interleaving: Mix different subjects or topics in one study session rather than focusing on one thing. This improves problem-solving skills.',
                'difficulty_level': 'hard',
                'context_tag': 'exam-prep'
            },
            {
                'content': 'Take regular breaks to move your body. Physical activity increases blood flow to the brain and improves concentration.',
                'difficulty_level': 'easy',
                'context_tag': 'concentration'
            },
            {
                'content': 'Review your notes within 24 hours of learning new material. This significantly improves retention.',
                'difficulty_level': 'easy',
                'context_tag': 'planning'
            },
        ]

        for tip_data in tips_data:
            StudyTip.objects.get_or_create(**tip_data)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(tips_data)} study tips'))
        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
