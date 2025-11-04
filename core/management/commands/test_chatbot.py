from django.core.management.base import BaseCommand
from core.views import ChatbotService

class Command(BaseCommand):
    help = 'Test chatbot API providers'

    def handle(self, *args, **kwargs):
        self.stdout.write('\n🤖 Testing StudyBuddy Chatbot Providers...\n')
        
        test_messages = [
            {
                "role": "system",
                "content": "You are StudyBuddy, a helpful study assistant."
            },
            {
                "role": "user",
                "content": "How can I improve my focus while studying?"
            }
        ]
        
        # Test OpenAI
        self.stdout.write('\n1️⃣  Testing OpenAI...')
        result = ChatbotService.call_openai(test_messages)
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'   ✓ OpenAI working!'))
            self.stdout.write(f'   Response: {result["message"][:100]}...')
        else:
            self.stdout.write(self.style.WARNING(f'   ✗ OpenAI failed: {result.get("error")}'))
        
        # Test HuggingFace Primary
        self.stdout.write('\n2️⃣  Testing HuggingFace (Primary)...')
        result = ChatbotService.call_huggingface(test_messages, model='primary')
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'   ✓ HuggingFace primary working!'))
            self.stdout.write(f'   Response: {result["message"][:100]}...')
        else:
            self.stdout.write(self.style.WARNING(f'   ✗ HuggingFace primary failed: {result.get("error")}'))
        
        # Test HuggingFace Backup
        self.stdout.write('\n3️⃣  Testing HuggingFace (Backup)...')
        result = ChatbotService.call_huggingface(test_messages, model='backup')
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f'   ✓ HuggingFace backup working!'))
            self.stdout.write(f'   Response: {result["message"][:100]}...')
        else:
            self.stdout.write(self.style.WARNING(f'   ✗ HuggingFace backup failed: {result.get("error")}'))
        
        # Test Local Fallback
        self.stdout.write('\n4️⃣  Testing Local Fallback...')
        response = ChatbotService.get_fallback_response("I need help with studying")
        self.stdout.write(self.style.SUCCESS(f'   ✓ Local fallback always works!'))
        self.stdout.write(f'   Response: {response[:100]}...')
        
        self.stdout.write('\n✅ Testing complete!\n')