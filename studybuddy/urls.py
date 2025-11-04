"""
URL configuration for studybuddy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.land_view, name='land'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('profile/', views.profile_view, name='profile'),
    path('analytics/', views.analytics_view, name='analytics'),
    
    # API endpoints
    path('api/tasks/create/', views.create_task, name='create_task'),
    path('api/tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('api/tasks/<int:task_id>/uncomplete/', views.uncomplete_task, name='uncomplete_task'),
    path('api/tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('api/motivation/', views.api_motivation, name='api_motivation'),
    # Chatbot endpoints
    path('api/chat/', views.chat_with_mascot, name='chat_with_mascot'),
    path('api/chat/history/', views.get_chat_history, name='get_chat_history'),
    path('api/chat/clear/', views.clear_chat_history, name='clear_chat_history'),
    path('api/study-help/', views.get_study_help, name='get_study_help'),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])