from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
import json
import random
from datetime import datetime, timedelta
from .models import Task, Reward, Quote, StudyTip, ProgressTracker, ChatMessage
from openai import OpenAI
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from .models import ChatMessage
import openai
import requests
import logging
# Create your views here.

# Landing page
def land_view(request):
    return render(request, 'index.html')

# Sign Up
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to StudyBuddy, {user.username}!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

#Log in
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Log out
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out. See you soon!')
    return redirect('land')

# Dashboard
@login_required
def dashboard_view(request):
    tasks = Task.objects.filter(user=request.user, is_completed=False).order_by('due_date')[:5]
    recent_rewards = Reward.objects.filter(user=request.user)[:3]
    
    completed_today = Task.objects.filter(
        user=request.user,
        is_completed=True,
        completed_at__date=timezone.now().date()
    ).count()
    
    quote = Quote.objects.order_by('?').first()
    tip = StudyTip.objects.order_by('?').first()
    
    context = {
        'tasks': tasks,
        'recent_rewards': recent_rewards,
        'completed_today': completed_today,
        'quote': quote,
        'tip': tip,
        'profile': request.user.profile,
    }
    return render(request, 'dashboard.html', context)

#View Tasks
@login_required
def tasks_view(request):
    filter_type = request.GET.get('filter', 'all')
    
    tasks = Task.objects.filter(user=request.user)
    
    if filter_type == 'pending':
        tasks = tasks.filter(is_completed=False)
    elif filter_type == 'completed':
        tasks = tasks.filter(is_completed=True)
    elif filter_type != 'all':
        tasks = tasks.filter(category=filter_type)
    
    context = {'tasks': tasks, 'filter': filter_type}
    return render(request, 'tasks.html', context)

#Create tasks
@login_required
@require_http_methods(["POST"])
def create_task(request):
    try:
        data = json.loads(request.body)
        task = Task.objects.create(
            user=request.user,
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category', 'other'),
            priority=data.get('priority', 'medium'),
            due_date = datetime.fromisoformat(data['due_date'])
            # due_date=data['due_date']
        )
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'category': task.category,
                'priority': task.priority,
                'due_date': task.due_date.isoformat()
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
#Complete tasks
@login_required
@require_http_methods(["POST"])
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if not task.is_completed:
        task.complete_task()
        
        return JsonResponse({
            'success': True,
            'points': {'low': 10, 'medium': 20, 'high': 30}[task.priority],
            'badge': task.check_badge(),
            'streak': request.user.profile.streak_count,
            'level': request.user.profile.level
        })
    
    return JsonResponse({'success': False, 'error': 'Task already completed'})

#Uncomplete task
@login_required
@require_http_methods(["POST"])
def uncomplete_task(request, task_id):
    """Undo task completion"""
    task = get_object_or_404(Task, id=task_id, user=request.user)
    
    if task.is_completed:
        # Get points before undoing
        reward = Reward.objects.filter(task=task).first()
        points_lost = reward.points_earned if reward else 0
        
        success = task.uncomplete_task()
        
        if success:
            return JsonResponse({
                'success': True,
                'points_lost': points_lost,
                'new_total': request.user.profile.total_points,
                'new_level': request.user.profile.level,
                'message': f'Task marked as incomplete. {points_lost} points removed.'
            })
    
    return JsonResponse({'success': False, 'error': 'Task is not completed'})

#Delete tasks
@login_required
@require_http_methods(["DELETE"])
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return JsonResponse({'success': True})

#View Profile
@login_required
def profile_view(request):
    profile = request.user.profile
    badges = Reward.objects.filter(user=request.user, badge_name__isnull=False).values_list('badge_name', flat=True).distinct()
    recent_tasks = Task.objects.filter(user=request.user, is_completed=True).order_by('-completed_at')[:10]
    
    context = {
        'profile': profile,
        'badges': list(badges),
        'recent_tasks': recent_tasks,
    }
    return render(request, 'profile.html', context)

#Analytics
@login_required
def analytics_view(request):
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)
    
    tasks_by_day = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        count = Task.objects.filter(
            user=request.user,
            is_completed=True,
            completed_at__date=date.date()
        ).count()
        tasks_by_day.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    
    category_stats = Task.objects.filter(
        user=request.user,
        is_completed=True
    ).values('category').annotate(count=Count('id'))
    
    context = {
        'tasks_by_day': json.dumps(tasks_by_day),
        'category_stats': json.dumps(list(category_stats)),
        'total_completed': Task.objects.filter(user=request.user, is_completed=True).count(),
        'total_points': request.user.profile.total_points,
    }
    return render(request, 'analytics.html', context)

#motivational messages
@login_required
def api_motivation(request):
    """AI-powered motivation endpoint"""
    profile = request.user.profile
    
    motivational_messages = [
        f"🌟 Amazing work, {request.user.username}! You're at level {profile.level} and crushing it!",
        f"🔥 {profile.streak_count} day streak! You're unstoppable!",
        "💪 Every task completed is a step toward greatness!",
        "🎯 Focus on progress, not perfection. You're doing great!",
        "✨ Believe in yourself. You've got this!",
        "🚀 You're building incredible momentum. Keep going!",
        "🌈 Your future self will thank you for the work you're doing today!",
    ]
    
    message = random.choice(motivational_messages)
    quote = Quote.objects.order_by('?').first()
    
    return JsonResponse({
        'message': message,
        'quote': {
            'content': quote.content if quote else "You are capable of amazing things!",
            'author': quote.author if quote else "StudyBuddy"
        },
        'level': profile.level,
        'streak': profile.streak_count
    })

logger = logging.getLogger(__name__) 

# Configure APIs
# openai.api_key = settings.OPENAI_API_KEY
client = OpenAI(base_url="https://router.huggingface.co/v1",api_key=settings.OPENAI_API_KEY)
# Configure Huggingface APIs
HUGGINGFACE_API_KEY = settings.HUGGINGFACE_API_KEY

class ChatbotService:
    """
    Multi-provider chatbot service with automatic fallback
    Priority: OpenAI → HuggingFace → Local Fallback
    """
    
    # HuggingFace models (free tier)
    MODELS = {
        'primary': 'mistralai/Mistral-7B-Instruct-v0.2',  # Best free model
        'backup': 'HuggingFaceH4/zephyr-7b-beta',          # Alternative
        'fast': 'microsoft/DialoGPT-large',                 # Faster, simpler
    }
    
    @staticmethod
    def call_openai(messages, max_tokens=300, temperature=0.7):
        """
        Call OpenAI API
        """
        try:
            response = client.chat.completions.create(
                # model="gpt-3.5-turbo",
                model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=10  # 10 second timeout
            )
            return {
                'success': True,
                'message': response.choices[0].message.content.strip(),
                'provider': 'openai'
            }
        except openai.RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return {'success': False, 'error': 'rate_limit'}
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {'success': False, 'error': 'api_error'}
        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed")
            return {'success': False, 'error': 'auth_error'}
        except Exception as e:
            logger.error(f"OpenAI unexpected error: {e}")
            return {'success': False, 'error': 'unknown'}
    
    # @staticmethod
    # def call_huggingface(messages, model='primary', max_tokens=300, temperature=0.7):
    #     """
    #     Call HuggingFace Inference API (FREE)
    #     """
    #     try:
    #         # Convert messages to prompt format
    #         prompt = ChatbotService._messages_to_prompt(messages)
            
    #         model_id = ChatbotService.MODELS[model]
    #         api_url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
            
    #         headers = {
    #             "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    #             "Content-Type": "application/json",
    #             "x-use-cache": "true" # Enable caching for faster responses(just added)
    #         }
            
    #         payload = {
    #             "inputs": prompt,
    #             "parameters": {
    #                 "max_new_tokens": max_tokens,
    #                 "temperature": temperature,
    #                 "top_p": 0.95,
    #                 "do_sample": True,
    #                 "return_full_text": False
    #             },
    #             "options": {
    #                 "use_cache": True,
    #                 "wait_for_model": True
    #             }
    #         }
            
    #         response = requests.post(
    #             api_url,
    #             headers=headers,
    #             json=payload,
    #             timeout=30
    #         )
            
    #         if response.status_code == 200:
    #             result = response.json()
                
    #             # Handle different response formats
    #             if isinstance(result, list) and len(result) > 0:
    #                 generated_text = result[0].get('generated_text', '')
    #             elif isinstance(result, dict):
    #                 generated_text = result.get('generated_text', '')
    #             else:
    #                 generated_text = str(result)
                
    #             # Clean up the response
    #             generated_text = ChatbotService._clean_response(generated_text)
                
    #             return {
    #                 'success': True,
    #                 'message': generated_text,
    #                 'provider': f'huggingface_{model}'
    #             }
            
    #         elif response.status_code == 503:
    #             # Model is loading, try backup model
    #             logger.warning(f"HuggingFace model loading, trying backup")
    #             if model != 'backup':
    #                 return ChatbotService.call_huggingface(messages, model='backup')
    #             return {'success': False, 'error': 'model_loading'}
            
    #         else:
    #             logger.error(f"HuggingFace error: {response.status_code} - {response.text}")
    #             return {'success': False, 'error': 'api_error'}
                
    #     except requests.exceptions.Timeout:
    #         logger.warning("HuggingFace request timeout")
    #         return {'success': False, 'error': 'timeout'}
    #     except Exception as e:
    #         logger.error(f"HuggingFace unexpected error: {e}")
    #         return {'success': False, 'error': 'unknown'} 
    
    @staticmethod
    def call_huggingface(messages, model='primary', max_tokens=300, temperature=0.7):
        """
        Call OpenAI API (converted from HuggingFace)
        """
        try:
            # Map model keys to OpenAI models
            openai_models = {
                'primary': 'openai/gpt-oss-safeguard-20b:groq',
                'backup': 'MiniMaxAI/MiniMax-M2:novita',
                'fast': 'gpt-3.5-turbo'
            }

            model_name = openai_models.get(model, 'openai/gpt-oss-120b:groq')

            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=30  # 30 second timeout
            )

            generated_text = response.choices[0].message.content.strip()

            # Clean up the response
            generated_text = ChatbotService._clean_response(generated_text)

            return {
                'success': True,
                'message': generated_text,
                'provider': f'openai_{model}'
            }

        except openai.RateLimitError:
            logger.warning("OpenAI rate limit exceeded")
            return {'success': False, 'error': 'rate_limit'}
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return {'success': False, 'error': 'api_error'}
        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed")
            return {'success': False, 'error': 'auth_error'}
        except openai.Timeout:
            logger.warning("OpenAI request timeout")
            return {'success': False, 'error': 'timeout'}
        except Exception as e:
            logger.error(f"OpenAI unexpected error: {e}")
            return {'success': False, 'error': 'unknown'}

    @staticmethod
    def _messages_to_prompt(messages):
        """
        Convert OpenAI-style messages to a single prompt
        """
        prompt_parts = []
        
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System Instructions: {content}\n")
            elif role == 'user':
                prompt_parts.append(f"Student: {content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"StudyBuddy: {content}\n")
        
        prompt_parts.append("StudyBuddy:")
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _clean_response(text):
        """
        Clean up generated text
        """
        # Remove common artifacts
        text = text.strip()

        # Remove # messages
        lines = text.splitlines()
        lines = [line for line in lines if not line.startswith("#")]
        text = "\n".join(lines)

        # Remove repetitive "StudyBuddy:" prefixes
        if text.startswith("StudyBuddy:"):
            text = text.replace("StudyBuddy:", "", 1).strip()
        
        # Remove trailing incomplete sentences
        if text and text[-1] not in '.!?':
            # Find last complete sentence
            last_punct = max(
                text.rfind('.'),
                text.rfind('!'),
                text.rfind('?')
            )
            if last_punct > 0:
                text = text[:last_punct + 1]
        
        # Limit length
        if len(text) > 500:
            text = text[:497] + "..."
        
        return text or "I'm here to help! Could you rephrase that? 🤔"
    
    @staticmethod
    def get_fallback_response(user_message):
        """
        Local fallback responses when all APIs fail
        """
        message_lower = user_message.lower()
        
        # Pattern matching for common queries
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hey there! 👋 I'm StudyBuddy! How can I help you with your studies today?"
        
        elif any(word in message_lower for word in ['help', 'stuck', 'confused']):
            return "I'm here to help! 💪 Can you tell me more about what you're working on? Break it down into smaller steps and we'll tackle it together!"
        
        elif any(word in message_lower for word in ['motivate', 'motivation', 'tired']):
            return "You've got this! 🌟 Remember, every small step forward is progress. Take a short break, drink some water, and come back refreshed. You're doing amazing!"
        
        elif any(word in message_lower for word in ['focus', 'distracted', 'concentrate']):
            return "Try the Pomodoro Technique! 🍅 Study for 25 minutes, then take a 5-minute break. Remove distractions, put your phone away, and focus on one task at a time. You can do it!"
        
        elif any(word in message_lower for word in ['study', 'learn', 'exam', 'test']):
            return "Great question about studying! 📚 Try active recall - test yourself instead of just rereading. Create flashcards, explain concepts out loud, and practice with problems. Spaced repetition is key!"
        
        elif any(word in message_lower for word in ['time', 'schedule', 'plan']):
            return "Time management is crucial! ⏰ Try planning your day the night before. Use a priority matrix: urgent-important tasks first. Break big projects into smaller tasks. You've got this!"
        
        elif any(word in message_lower for word in ['thank', 'thanks']):
            return "You're welcome! 😊 Keep up the great work! I'm always here if you need help or motivation!"
        
        else:
            return "I'm having some technical difficulties right now, but I'm still here for you! 🤗 In the meantime, check out your study tips or try breaking down your task into smaller steps. You can do this!"
    
    @staticmethod
    def get_response(messages, user_message):
        """
        Main method: Try providers in order with automatic fallback
        """
        # Try OpenAI first (if API key exists)
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != '':
            logger.info("Trying OpenAI...")
            result = ChatbotService.call_openai(messages)
            if result['success']:
                logger.info("✓ OpenAI responded")
                return result
            logger.warning(f"✗ OpenAI failed: {result.get('error')}")
        
        # Try HuggingFace (primary model)
        if settings.HUGGINGFACE_API_KEY and settings.HUGGINGFACE_API_KEY != '':
            logger.info("Trying HuggingFace primary model...")
            result = ChatbotService.call_huggingface(messages, model='primary')
            if result['success']:
                logger.info("✓ HuggingFace responded")
                return result
            logger.warning(f"✗ HuggingFace primary failed: {result.get('error')}")
            
            # Try backup model
            logger.info("Trying HuggingFace backup model...")
            result = ChatbotService.call_huggingface(messages, model='backup')
            if result['success']:
                logger.info("✓ HuggingFace backup responded")
                return result
            logger.warning(f"✗ HuggingFace backup failed: {result.get('error')}")
        
        # Local fallback
        logger.info("Using local fallback responses")
        return {
            'success': True,
            'message': ChatbotService.get_fallback_response(user_message),
            'provider': 'local_fallback'
        }



@login_required
@require_http_methods(["POST"])
def chat_with_mascot(request):
    """
    AI Chatbot endpoint - handles conversations with the mascot
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
        
        # Validate message length
        if len(user_message) > 500:
            return JsonResponse({
                'error': 'Message too long. Please keep it under 500 characters.'
            }, status=400)

        # Save user message
        ChatMessage.objects.create(
            user=request.user,
            message=user_message,
            is_bot=False
        )
        
        # Get conversation history (last 10 messages for context)
        history = ChatMessage.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10][::-1]
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": """You are StudyBuddy, a friendly and encouraging AI study companion for high school students. 
                Your personality:
                - Enthusiastic and supportive (use emojis occasionally)
                - Clear and concise in explanations
                - Focused on education, productivity, and student wellbeing
                - Never do homework for them, but guide them to learn
                - Encourage healthy study habits and work-life balance
                
                You help with:
                - Study techniques and time management
                - Understanding homework concepts (guide, don't solve)
                - Motivation and encouragement
                - Breaking down complex topics
                - Exam preparation strategies
                - Managing stress and staying focused
                
                Important guidelines:
                -Always prioritize the student's learning and growth
                -Avoid all # messages
                -Keep responses very brief unless explaining something complex.
                -Ask follow up questions to understand their needs.
                -Always be positive and celebrate their efforts!"""
            }
        ]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": "assistant" if msg.is_bot else "user",
                "content": msg.message
            })
        
        # Add current message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        
        # Get AI response with automatic fallback
        result = ChatbotService.get_response(messages, user_message)
        
        if result['success']:
            bot_message = result['message']
            provider = result['provider']

        # Get AI response
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=messages,
        #     max_tokens=300,
        #     temperature=0.7,
        # )

        # bot_message = response.choices[0].message.content.strip()

        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",  # or "gpt-4" for better responses
        #     messages=messages,
        #     max_tokens=300,
        #     temperature=0.7,
        # )
        
        # bot_message = response.choices[0].message.content.strip()
        
        # Save bot response
            ChatMessage.objects.create(
                user=request.user,
                message=bot_message,
                is_bot=True
            )
            logger.info(f"Chat response from {provider} for user {request.user.username}")
            #last_msg = ChatMessage.objects.filter(user=request.user).order_by('-created_at').first()
        
            return JsonResponse({
                'success': True,
                'message': bot_message,
                'provider': provider,
                #'timestamp': last_msg.created_at.isoformat()
                'timestamp': ChatMessage.objects.latest('created_at').created_at.isoformat()
            })
        else:
            # This shouldn't happen due to local fallback
            return JsonResponse({
                'success': False,
                'error': 'All chat services are temporarily unavailable'
            }, status=503)
    
    except Exception as e:
        logger.error(f"Chat error: {e}",exc_info=True)
        import traceback
        print("🔥 OpenAI Chat Error:", e)
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

    # except Exception as e:
    #     logger.error(f"Chat error: {e}",exc_info=True)
    #     return JsonResponse({
    #         'success': False,
    #         'error': str(e)
    #     }, status=500)
    
#Chat History    
@login_required
def get_chat_history(request):
    """
    Retrieve chat history for the current user
    """
    messages = ChatMessage.objects.filter(
        user=request.user
    ).order_by('created_at')[:50]  # Last 50 messages
    
    chat_data = [{
        'message': msg.message,
        'is_bot': msg.is_bot,
        'timestamp': msg.created_at.isoformat()
    } for msg in messages]
    
    return JsonResponse({
        'success': True,
        'messages': chat_data
    })

#clear chat
@login_required
@require_http_methods(["DELETE"])
def clear_chat_history(request):
    """
    Clear all chat messages for the current user
    """
    ChatMessage.objects.filter(user=request.user).delete()
    return JsonResponse({'success': True})

#Prompting for study help
@login_required
@require_http_methods(["POST"])
def get_study_help(request):
    """
    Quick study help - specialized responses for common questions
    """
    try:
        data = json.loads(request.body)
        topic = data.get('topic', '')
        subject = data.get('subject', '')
        
        prompt = f"""As StudyBuddy, provide a brief, encouraging study tip for a high school student 
        who needs help with {subject}: {topic}. 
        Give them 2-3 actionable steps to understand this better. Be supportive and use an emoji or two."""
        
        # response = openai.ChatCompletion.create(
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are StudyBuddy, a helpful study companion."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.8,
        )
        
        advice = response.choices[0].message.content.strip()
        
        return JsonResponse({
            'success': True,
            'advice': advice
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
