# studybuddy
StudyBuddy is a gamified time management web application designed specifically for high school students. It helps students stay productive through task tracking, rewards systems, and AI-powered motivational feedback.

## 🌟 Features

### Core Functionality
- **Task Manager**: Full CRUD operations for tasks with categories, priorities, and deadlines
- **Rewards System**: Earn points and badges for completing tasks
- **Motivational Feed**: AI-powered quotes and study tips
- **Smart Alerts**: Browser notifications and email reminders
- **Dashboard & Analytics**: Track progress with visual charts and statistics
- **User Profiles**: Level up as you complete more tasks

### Gamification Elements
- Points system (Low: 10pts, Medium: 20pts, High: 30pts)
- Level progression (Level = Total Points / 100)
- Streak tracking for consecutive days of activity
- Achievement badges at milestones
- Animated mascot that celebrates your progress

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/studybuddy.git
cd studybuddy
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser (admin):
```bash
python manage.py createsuperuser
```

6. Seed database with initial data:
```bash
python manage.py seed_data
```

7. (Optional) Create demo user with sample tasks:
```bash
python manage.py create_demo_user
```

8. Run development server:
```bash
python manage.py runserver
```

9. Open browser to http://localhost:8000

## 📁 Project Structure

```
studybuddy/
├── studybuddy/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── admin.py         # Admin interface
│   └── management/      # Custom commands
├── templates/           # HTML templates
├── static/              # CSS, JavaScript, images
│   ├── css/
│   └── js/
└── media/              # User uploads
```

## 🗄️ Database Schema

### Models
- **UserProfile**: Extended user data (level, points, streak)
- **Task**: Student tasks with categories and priorities
- **Reward**: Points and badges earned
- **Quote**: Motivational quotes
- **StudyTip**: Study advice and techniques
- **ProgressTracker**: Analytics data

## 🎨 Design Features

### UI/UX
- Bright, engaging color palette with pastels
- Rounded elements and smooth animations
- Animated mascot companion
- Responsive design (mobile & desktop)
- Game-like interface with celebratory animations

### Mascot Interactions
- Floats on screen with animations
- Shows encouraging messages
- Celebrates task completions
- Provides motivational feedback
- Interactive on click

## 🔧 Technology Stack

### Backend
- Django 4.2.7
- Python 3.8+
- SQLite (development) / MySQL/PostgreSQL (production)

### Frontend
- HTML5
- Vanilla CSS3 (with animations)
- Vanilla JavaScript (ES6+)
- Chart.js for analytics visualization

### Infrastructure (Production)
- AWS EC2 (compute)
- AWS RDS (database)
- AWS S3 (static/media files)
- Nginx (reverse proxy)
- Gunicorn (WSGI server)

## 🤖 AI Integration

The `/api/motivation/` endpoint can be integrated with:
- OpenAI API for personalized motivational messages
- HuggingFace models for natural language generation
- Custom ML models for study recommendations

Set your API key in environment variables:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 📊 API Endpoints

```
GET  /dashboard/                    # Main dashboard
GET  /tasks/                        # Task list
POST /api/tasks/create/             # Create task
POST /api/tasks/<id>/complete/      # Complete task
DELETE /api/tasks/<id>/delete/      # Delete task
GET  /api/motivation/               # Get motivation
GET  /profile/                      # User profile
GET  /analytics/                    # Progress analytics
```

## 🎯 Future Enhancements

- Smart Scheduler: AI-suggested study plans
- Leaderboards: Compete with friends
- Social Features: Share achievements
- Mobile App: Native iOS/Android apps
- Calendar Integration: Sync with Google Calendar
- Study Groups: Collaborative task tracking
- Advanced Analytics: ML-powered insights

## 🔒 Security

- CSRF protection enabled
- Password hashing with Django's built-in system
- SQL injection protection via ORM
- XSS protection with template escaping
- Secure session management

## 📝 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=mysql://user:pass@host:port/db
OPENAI_API_KEY=your-openai-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 👥 Authors

- Prince Derek Tettey Martey - Initial work

## 🙏 Acknowledgments

- Inspired by productivity apps like Todoist and Habitica
- Icons and emojis from Unicode Consortium
- Chart.js for beautiful data visualization

## 📧 Support

For support, email support@studybuddy.com or create an issue on GitHub.

---

Made with ❤️ for students who want to achieve their goals!