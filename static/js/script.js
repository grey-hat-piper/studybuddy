// static/js/script.js

// ===== CSRF TOKEN HELPER =====
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// ===== MASCOT FUNCTIONS =====
function showMascotMessage(message, duration = 4000) {
    const mascotMessage = document.getElementById('mascot-message');
    const mascot = document.querySelector('.mascot-face');
    
    if (mascotMessage) {
        mascotMessage.textContent = message;
        mascotMessage.classList.add('show');
        
        // Celebrate animation
        mascot.classList.add('celebrate');
        setTimeout(() => mascot.classList.remove('celebrate'), 600);
        
        setTimeout(() => {
            mascotMessage.classList.remove('show');
        }, duration);
    }
}

function celebrateTaskCompletion(points, badge, streak) {
    const messages = [
        `🎉 Awesome! You earned ${points} points!`,
        `🔥 ${streak} day streak! You're on fire!`,
        `💪 Keep crushing it! ${points} points earned!`,
        `⭐ Amazing work! +${points} points!`,
        `🚀 You're unstoppable! ${points} points!`
    ];
    
    let message = messages[Math.floor(Math.random() * messages.length)];
    
    if (badge) {
        message += ` 🎖️ New badge: ${badge}!`;
    }
    
    showMascotMessage(message, 6000);
}

// ===== MODAL FUNCTIONS =====
function showTaskModal() {
    const modal = document.getElementById('taskModal');
    if (modal) {
        modal.style.display = 'block';
        
        // Set default due date to tomorrow
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(23, 59, 0, 0);
        
        const dueDateInput = document.getElementById('taskDueDate');
        if (dueDateInput) {
            dueDateInput.value = tomorrow.toISOString().slice(0, 16);
        }
    }
}

function closeTaskModal() {
    const modal = document.getElementById('taskModal');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('taskForm').reset();
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('taskModal');
    const chatwindow = document.getElementById('chatWindow')
    if (event.target === modal || event.target === chatwindow ) {
        closeTaskModal();
    }
}

// ===== TASK MANAGEMENT =====
async function createTask(event) {
    event.preventDefault();
    
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    const category = document.getElementById('taskCategory').value;
    const priority = document.getElementById('taskPriority').value;
    const dueDate = document.getElementById('taskDueDate').value;
    
    if (!title || !dueDate) {
        showMascotMessage('⚠️ Please fill in all required fields!', 3000);
        return;
    }
    
    try {
        const response = await fetch('/api/tasks/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                title,
                description,
                category,
                priority,
                due_date: dueDate
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMascotMessage('✅ Task created successfully! Let\'s do this!', 3000);
            closeTaskModal();
            
            // Reload page after a short delay
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showMascotMessage('❌ Oops! Something went wrong. Try again!', 3000);
        }
    } catch (error) {
        console.error('Error creating task:', error);
        showMascotMessage('❌ Network error. Please check your connection!', 3000);
    }
}

async function completeTask(taskId) {
    // if (!confirm('Mark this task as complete?')) {
    //     return;
    // }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}/complete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            celebrateTaskCompletion(data.points, data.badge, data.streak);
            
            // Update UI
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showMascotMessage('❌ ' + (data.error || 'Could not complete task'), 3000);
        }
    } catch (error) {
        console.error('Error completing task:', error);
        showMascotMessage('❌ Network error. Please try again!', 3000);
    }
}

async function uncompleteTask(taskId) {
    if (!confirm('Mark this task as incomplete? This will reverse your points and progress.')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}/uncomplete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMascotMessage(
                `↶ Task reopened! ${data.points_lost} points removed. Keep working on it! 💪`, 
                4000
            );
            
            // Update UI
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            showMascotMessage('❌ ' + (data.error || 'Could not undo task completion'), 3000);
        }
    } catch (error) {
        console.error('Error uncompleting task:', error);
        showMascotMessage('❌ Network error. Please try again!', 3000);
    }
}

async function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${taskId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMascotMessage('🗑️ Task deleted successfully!', 2000);
            
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showMascotMessage('❌ Could not delete task. Try again!', 3000);
        }
    } catch (error) {
        console.error('Error deleting task:', error);
        showMascotMessage('❌ Network error. Please try again!', 3000);
    }
}

// ===== MOTIVATION API =====
async function getNewMotivation() {
    const button = event.target;
    button.disabled = true;
    button.textContent = 'Loading...';
    
    try {
        const response = await fetch('/api/motivation/');
        const data = await response.json();
        
        showMascotMessage(data.message, 5000);
        
        // Update quote if on dashboard
        const quoteElement = document.querySelector('.quote');
        if (quoteElement && data.quote) {
            quoteElement.innerHTML = `
                "${data.quote.content}"
                <footer>— ${data.quote.author}</footer>
            `;
        }
        
        button.textContent = 'Get Inspired!';
        button.disabled = false;
    } catch (error) {
        console.error('Error fetching motivation:', error);
        showMascotMessage('❌ Could not fetch motivation. Try again!', 3000);
        button.textContent = 'Get Inspired!';
        button.disabled = false;
    }
}

// ===== NOTIFICATIONS =====
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                showMascotMessage('🔔 Notifications enabled! I\'ll remind you about tasks!', 3000);
            }
        });
    }
}

function showNotification(title, options) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, options);
    }
}

function checkUpcomingTasks() {
    // This would be called periodically to check for tasks due soon
    // For production, implement proper backend scheduling
    const now = new Date();
    const oneHour = 60 * 60 * 1000;
    
    // Mock implementation - in production, fetch from API
    console.log('Checking for upcoming tasks...');
}

// ===== FORM VALIDATION =====
function validateTaskForm() {
    const title = document.getElementById('taskTitle').value.trim();
    const dueDate = document.getElementById('taskDueDate').value;
    
    if (!title) {
        showMascotMessage('⚠️ Task title is required!', 2000);
        return false;
    }
    
    if (!dueDate) {
        showMascotMessage('⚠️ Due date is required!', 2000);
        return false;
    }
    
    const selectedDate = new Date(dueDate);
    const now = new Date();
    
    if (selectedDate < now) {
        showMascotMessage('⚠️ Due date must be in the future!', 2000);
        return false;
    }
    
    return true;
}

// ===== EVENT LISTENERS =====
document.addEventListener('DOMContentLoaded', function() {
    // Task form submission
    const taskForm = document.getElementById('taskForm');
    if (taskForm) {
        taskForm.addEventListener('submit', createTask);
    }
    
    // Mascot click interaction
    const mascot = document.querySelector('.mascot-face');
    if (mascot) {
        mascot.addEventListener('click', function() {
            const encouragements = [
                "You're doing great! Keep it up! 🌟",
                "Believe in yourself! You've got this! 💪",
                "Every task completed is a victory! 🎉",
                "Stay focused and amazing things will happen! ✨",
                "You're making incredible progress! 🚀",
                "Keep pushing forward! Success is near! 🎯"
            ];
            const message = encouragements[Math.floor(Math.random() * encouragements.length)];
            showMascotMessage(message);
        });
    }
    
    // Request notification permission after a short delay
    setTimeout(() => {
        if ('Notification' in window && Notification.permission === 'default') {
            requestNotificationPermission();
        }
    }, 5000);
    
    // Set up periodic task checking (every 15 minutes)
    setInterval(checkUpcomingTasks, 15 * 60 * 1000);
    
    // Initialize tooltips and other UI enhancements
    initializeUI();
});

// ===== UI ENHANCEMENTS =====
function initializeUI() {
    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.classList.contains('no-loading')) {
                this.classList.add('loading');
                setTimeout(() => {
                    this.classList.remove('loading');
                }, 1000);
            }
        });
    });
    
    // Auto-hide messages after delay
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
}

// ===== PROGRESS TRACKING =====
function updateProgressBar(percentage) {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        bar.style.width = percentage + '%';
    });
}

// ===== KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + N: New task
    if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        showTaskModal();
    }
    
    // Escape: Close modal
    if (event.key === 'Escape') {
        closeTaskModal();
    }
});

// ===== LOCAL STORAGE HELPERS =====
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('Error saving to localStorage:', error);
    }
}

function getFromLocalStorage(key) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    } catch (error) {
        console.error('Error reading from localStorage:', error);
        return null;
    }
}

// ===== THEME TOGGLE (Future Enhancement) =====
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-theme', newTheme);
    saveToLocalStorage('theme', newTheme);
}

// ===== ANALYTICS HELPERS =====
function trackEvent(eventName, eventData) {
    // Placeholder for analytics tracking
    console.log('Event tracked:', eventName, eventData);
    
    // In production, send to analytics service
    // Example: gtag('event', eventName, eventData);
}

// ===== UTILITY FUNCTIONS =====
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===== EXPORT FUNCTIONS FOR GLOBAL USE =====
window.showTaskModal = showTaskModal;
window.closeTaskModal = closeTaskModal;
window.createTask = createTask;
window.completeTask = completeTask;
window.uncompleteTask = uncompleteTask;
window.deleteTask = deleteTask;
window.getNewMotivation = getNewMotivation;
window.showMascotMessage = showMascotMessage;

// ===== WELCOME MESSAGE =====
console.log('%c👋 Welcome to StudyBuddy!', 'font-size: 24px; color: #6366f1; font-weight: bold;');
console.log('%c🚀 Let\'s make today productive!', 'font-size: 16px; color: #8b5cf6;');

// ===== CHAT WINDOW MANAGEMENT =====
let chatOpen = false;
let chatHistory = [];

function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    const mascot = document.getElementById('mascot');
    const chatBadge = document.getElementById('chatBadge');
    
    chatOpen = !chatOpen;
    
    if (chatOpen) {
        chatWindow.classList.add('open');
        mascot.style.display = 'none';
        
        // Load chat history on first open
        if (chatHistory.length === 0) {
            loadChatHistory();
        }
    } else {
        chatWindow.classList.remove('open');
        mascot.style.display = 'block';
    }
    
    // Hide badge when opening chat
    if (chatBadge && chatOpen) {
        chatBadge.style.display = 'none';
    }
}

// ===== LOAD CHAT HISTORY =====
async function loadChatHistory() {
    try {
        const response = await fetch('/api/chat/history/');
        const data = await response.json();
        
        if (data.success && data.messages.length > 0) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = ''; // Clear welcome message
            
            data.messages.forEach(msg => {
                appendMessage(msg.message, msg.is_bot, false);
            });
            
            chatHistory = data.messages;
            scrollToBottom();
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

// ===== SEND MESSAGE =====
async function sendMessage(message) {
    if (!message.trim()) return;
    
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.querySelector('.send-btn');
    
    // Append user message immediately
    appendMessage(message, false);
    
    // Clear input and disable
    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (data.success) {
            // Append bot response
            appendMessage(data.message, true);
            
            // Show celebration if message is encouraging
            if (isEncouragingMessage(data.message)) {
                celebrateChatMessage();
            }
        } else {
            appendMessage('Sorry, I encountered an error. Please try again! 😅', true);
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        appendMessage('Oops! Network error. Please check your connection! 🔌', true);
    } finally {
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

// ===== APPEND MESSAGE TO CHAT =====
function appendMessage(text, isBot = false, shouldScroll = true) {
    const chatMessages = document.getElementById('chatMessages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = isBot ? 'bot-message' : 'user-message';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = isBot ? '🎓' : (window.userInitial || '👤');
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(bubble);
    chatMessages.appendChild(messageDiv);
    
    if (shouldScroll) {
        scrollToBottom();
    }
}

// ===== TYPING INDICATOR =====
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator bot-message';
    typingDiv.id = 'typingIndicator';
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = '🎓';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        dot.className = 'typing-dot';
        bubble.appendChild(dot);
    }
    
    typingDiv.appendChild(avatar);
    typingDiv.appendChild(bubble);
    chatMessages.appendChild(typingDiv);
    
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

// ===== QUICK QUESTIONS =====
function quickQuestion(question) {
    const chatInput = document.getElementById('chatInput');
    chatInput.value = question;
    sendMessage(question);
}

// ===== CLEAR CHAT =====
async function clearChat() {
    if (!confirm('Clear all chat messages? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/chat/clear/', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="bot-message">
                    <div class="message-avatar">🎓</div>
                    <div class="message-bubble">
                        Chat cleared! Fresh start! How can I help you today? 🌟
                    </div>
                </div>
            `;
            chatHistory = [];
            showMascotMessage('Chat history cleared! 🗑️', 2000);
        }
    } catch (error) {
        console.error('Error clearing chat:', error);
        showMascotMessage('Could not clear chat. Try again! ❌', 2000);
    }
}

// ===== SCROLL TO BOTTOM =====
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ===== HELPER FUNCTIONS =====
function isEncouragingMessage(message) {
    const encouragingWords = ['great', 'awesome', 'amazing', 'fantastic', 'excellent', 
                              'wonderful', 'perfect', 'brilliant', 'outstanding'];
    return encouragingWords.some(word => message.toLowerCase().includes(word));
}

function celebrateChatMessage() {
    const mascot = document.querySelector('.chat-icon');
    if (mascot) {
        mascot.classList.add('celebrate');
        setTimeout(() => mascot.classList.remove('celebrate'), 600);
    }
}

// ===== STUDY HELP SHORTCUT =====
async function getQuickStudyHelp(subject, topic) {
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/study-help/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({ subject, topic })
        });
        
        const data = await response.json();
        
        removeTypingIndicator();
        
        if (data.success) {
            appendMessage(data.advice, true);
        }
    } catch (error) {
        console.error('Error getting study help:', error);
        removeTypingIndicator();
    }
}

// ===== CHAT FORM HANDLER =====
document.addEventListener('DOMContentLoaded', function() {
    // Chat form submission
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = document.getElementById('chatInput').value;
            sendMessage(message);
        });
    }
    
    // Enter key to send (Shift+Enter for new line)
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(this.value);
            }
        });
    }
    
    // Auto-focus chat input when opening
    const originalToggle = toggleChat;
    toggleChat = function() {
        originalToggle();
        if (chatOpen) {
            setTimeout(() => {
                document.getElementById('chatInput')?.focus();
            }, 100);
        }
    };
    
    // Store user initial for avatar
    const username = document.querySelector('.nav-user')?.textContent;
    if (username) {
        window.userInitial = username.trim()[0].toUpperCase();
    }
    
    // Notification badge pulse
    const badge = document.getElementById('chatBadge');
    if (badge) {
        // Show badge after 10 seconds if chat hasn't been opened
        setTimeout(() => {
            if (!chatOpen) {
                badge.style.display = 'flex';
            }
        }, 10000);
    }
});

// ===== CHAT KEYBOARD SHORTCUTS =====
document.addEventListener('keydown', function(e) {
    // Alt + C: Toggle chat
    if (e.altKey && e.key === 'c') {
        e.preventDefault();
        toggleChat();
    }
    
    // Escape: Close chat if open
    if (e.key === 'Escape' && chatOpen) {
        toggleChat();
    }
});

// ===== SMART SUGGESTIONS =====
function updateQuickActions(context) {
    const quickActions = document.querySelector('.chat-quick-actions');
    if (!quickActions) return;
    
    let suggestions = [];
    
    // Context-aware suggestions based on page
    if (window.location.pathname.includes('tasks')) {
        suggestions = [
            '🎯 How to prioritize tasks?',
            '⏰ Time management tips',
            '📝 Breaking down big projects'
        ];
    } else if (window.location.pathname.includes('analytics')) {
        suggestions = [
            '📊 How to improve my stats?',
            '🎯 Setting better goals',
            '💪 Staying motivated'
        ];
    } else {
        suggestions = [
            '🎯 Focus tips',
            '📅 Schedule help',
            '😰 Feeling overwhelmed'
        ];
    }
    
    quickActions.innerHTML = suggestions.map(s => 
        `<button onclick="quickQuestion('${s.substring(2)}')" class="quick-btn">${s}</button>`
    ).join('');
}

// ===== PROACTIVE CHAT SUGGESTIONS =====
function checkForHelpOpportunities() {
    // If user has many overdue tasks, offer help
    const overdueTasks = document.querySelectorAll('.task-card.overdue');
    if (overdueTasks.length >= 3 && !chatOpen) {
        setTimeout(() => {
            showMascotMessage('Hey! I noticed you have some overdue tasks. Want to chat about managing your workload? 💪', 8000);
        }, 5000);
    }
    
    // If user completed many tasks, celebrate
    const completedToday = document.querySelector('[data-completed-today]');
    if (completedToday && parseInt(completedToday.dataset.completedToday) >= 5) {
        showMascotMessage('Wow! 5+ tasks done today! You\'re crushing it! Want to chat about your success? 🎉', 6000);
    }
}

// Run opportunity checks after page load
window.addEventListener('load', () => {
    setTimeout(checkForHelpOpportunities, 3000);
    updateQuickActions();
});

// ===== EXPORT CHAT FUNCTIONS =====
window.toggleChat = toggleChat;
window.sendMessage = sendMessage;
window.quickQuestion = quickQuestion;
window.clearChat = clearChat;
window.getQuickStudyHelp = getQuickStudyHelp;

// ===== VOICE INPUT (OPTIONAL FEATURE) =====
let recognition = null;

function initVoiceInput() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
            sendMessage(transcript);
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            showMascotMessage('Could not understand. Please try typing! 🎤', 3000);
        };
    }
}

function startVoiceInput() {
    if (recognition) {
        recognition.start();
        showMascotMessage('Listening... 🎤', 2000);
    }
}

// ===== CHAT ANALYTICS =====
function trackChatInteraction(action, details = {}) {
    // Track chat usage for analytics
    const analyticsData = {
        action: action,
        timestamp: new Date().toISOString(),
        ...details
    };
    
    // Store locally for analytics dashboard
    const chatAnalytics = JSON.parse(localStorage.getItem('chatAnalytics') || '[]');
    chatAnalytics.push(analyticsData);
    
    // Keep only last 100 interactions
    if (chatAnalytics.length > 100) {
        chatAnalytics.shift();
    }
    
    localStorage.setItem('chatAnalytics', JSON.stringify(chatAnalytics));
    
    console.log('Chat interaction tracked:', action);
}

// Track when chat is opened
const originalToggleChatTracked = toggleChat;
toggleChat = function() {
    originalToggleChatTracked();
    if (chatOpen) {
        trackChatInteraction('chat_opened');
    } else {
        trackChatInteraction('chat_closed');
    }
};

// ===== SMART CONTEXT DETECTION =====
function detectUserContext() {
    const context = {
        page: window.location.pathname,
        time: new Date().getHours(),
        hasOverdueTasks: document.querySelectorAll('.task-card.overdue').length > 0,
        completedToday: parseInt(document.querySelector('[data-completed-today]')?.textContent || '0'),
        currentStreak: parseInt(document.querySelector('.streak-count')?.textContent || '0')
    };
    
    return context;
}

function getContextualGreeting() {
    const hour = new Date().getHours();
    const context = detectUserContext();
    
    let greeting = '';
    
    // Time-based greeting
    if (hour < 12) {
        greeting = 'Good morning! ☀️';
    } else if (hour < 18) {
        greeting = 'Good afternoon! 👋';
    } else {
        greeting = 'Good evening! 🌙';
    }
    
    // Add context
    if (context.completedToday >= 3) {
        greeting += ' You\'re doing amazing today!';
    } else if (context.hasOverdueTasks) {
        greeting += ' Ready to tackle those tasks?';
    } else if (context.currentStreak >= 5) {
        greeting += ` ${context.currentStreak} day streak - incredible!`;
    }
    
    return greeting;
}

// ===== CHAT EXPORT FEATURE =====
function exportChatHistory() {
    const messages = Array.from(document.querySelectorAll('.user-message, .bot-message'));
    let chatText = '=== StudyBuddy Chat History ===\n';
    chatText += `Exported: ${new Date().toLocaleString()}\n\n`;
    
    messages.forEach(msg => {
        const isBot = msg.classList.contains('bot-message');
        const text = msg.querySelector('.message-bubble').textContent;
        chatText += `${isBot ? '🎓 StudyBuddy' : '👤 You'}: ${text}\n\n`;
    });
    
    // Create download
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `studybuddy-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    
    showMascotMessage('Chat history exported! 📥', 2000);
}

// ===== CHAT REMINDERS =====
function setChatReminder(message, delayMinutes) {
    setTimeout(() => {
        if (!chatOpen) {
            showMascotMessage(message, 6000);
            // Make badge pulse more noticeably
            const badge = document.getElementById('chatBadge');
            if (badge) {
                badge.style.display = 'flex';
                badge.style.animation = 'pulse 1s infinite';
            }
        }
    }, delayMinutes * 60 * 1000);
}

// Set helpful reminders
document.addEventListener('DOMContentLoaded', function() {
    // Remind user about chat after 15 minutes if not used
    setChatReminder('💡 Need any study tips or motivation? I\'m here to help!', 15);
    
    // Check-in after 30 minutes
    setChatReminder('👋 How\'s your study session going? Want to chat?', 30);
});

// ===== EMOJI REACTIONS =====
function addEmojiReaction(messageElement, emoji) {
    const reaction = document.createElement('span');
    reaction.className = 'message-reaction';
    reaction.textContent = emoji;
    reaction.style.cssText = `
        position: absolute;
        bottom: -8px;
        right: 8px;
        background: white;
        border-radius: 50%;
        padding: 2px 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 0.875rem;
    `;
    
    messageElement.style.position = 'relative';
    messageElement.appendChild(reaction);
}

// ===== SUGGESTED RESPONSES =====
function showSuggestedResponses(responses) {
    const chatMessages = document.getElementById('chatMessages');
    
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'suggested-responses';
    suggestionsDiv.style.cssText = `
        display: flex;
        gap: 0.5rem;
        padding: 0.5rem;
        flex-wrap: wrap;
    `;
    
    responses.forEach(response => {
        const btn = document.createElement('button');
        btn.className = 'suggestion-btn';
        btn.textContent = response;
        btn.style.cssText = `
            padding: 0.5rem 1rem;
            background: white;
            border: 2px solid var(--primary);
            border-radius: 20px;
            color: var(--primary);
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.3s;
        `;
        
        btn.onclick = () => {
            sendMessage(response);
            suggestionsDiv.remove();
        };
        
        btn.onmouseover = () => {
            btn.style.background = 'var(--primary)';
            btn.style.color = 'white';
        };
        
        btn.onmouseout = () => {
            btn.style.background = 'white';
            btn.style.color = 'var(--primary)';
        };
        
        suggestionsDiv.appendChild(btn);
    });
    
    chatMessages.appendChild(suggestionsDiv);
    scrollToBottom();
}

// Example: Show suggestions after certain bot responses
function handleBotResponse(message) {
    appendMessage(message, true);
    
    // Show suggestions if bot asks a question
    if (message.includes('?')) {
        const suggestions = [
            '✅ Yes, that helps!',
            '❓ Tell me more',
            '🤔 I need different advice'
        ];
        setTimeout(() => showSuggestedResponses(suggestions), 500);
    }
}

// ===== CHAT THEMES (OPTIONAL) =====
function setChatTheme(theme) {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.setAttribute('data-theme', theme);
    localStorage.setItem('chatTheme', theme);
}

function loadChatTheme() {
    const savedTheme = localStorage.getItem('chatTheme') || 'default';
    setChatTheme(savedTheme);
}

// ===== TYPING SPEED SIMULATION =====
function typeMessage(text, isBot = true, speed = 30) {
    return new Promise((resolve) => {
        const chatMessages = document.getElementById('chatMessages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = isBot ? 'bot-message' : 'user-message';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = isBot ? '🎓' : '👤';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
        chatMessages.appendChild(messageDiv);
        
        let index = 0;
        const interval = setInterval(() => {
            bubble.textContent += text[index];
            index++;
            scrollToBottom();
            
            if (index === text.length) {
                clearInterval(interval);
                resolve();
            }
        }, speed);
    });
}

// ===== CHAT STATISTICS =====
function getChatStatistics() {
    const analytics = JSON.parse(localStorage.getItem('chatAnalytics') || '[]');
    
    return {
        totalMessages: analytics.filter(a => a.action === 'message_sent').length,
        chatSessions: analytics.filter(a => a.action === 'chat_opened').length,
        averageMessagesPerSession: 0, // Calculate based on data
        lastChatDate: analytics.length > 0 ? analytics[analytics.length - 1].timestamp : null
    };
}

// ===== INITIALIZE CHAT FEATURES =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize voice input if available
    initVoiceInput();
    
    // Load chat theme
    loadChatTheme();
    
    // Show contextual greeting when chat opens
    const originalLoad = loadChatHistory;
    loadChatHistory = async function() {
        await originalLoad();
        
        // If no history, show contextual greeting
        if (chatHistory.length === 0) {
            const greeting = getContextualGreeting();
            setTimeout(() => {
                const welcomeMsg = document.querySelector('.bot-message .message-bubble');
                if (welcomeMsg) {
                    welcomeMsg.textContent = `${greeting} ${welcomeMsg.textContent}`;
                }
            }, 500);
        }
    };
});

// ===== ACCESSIBILITY FEATURES =====
function setupChatAccessibility() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    
    // Screen reader announcements
    chatInput?.setAttribute('aria-label', 'Type your message to StudyBuddy');
    chatMessages?.setAttribute('aria-live', 'polite');
    chatMessages?.setAttribute('aria-atomic', 'false');
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (chatOpen) {
            // Arrow up/down to navigate messages
            if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                // Implement message navigation
            }
        }
    });
}

setupChatAccessibility();

console.log('💬 StudyBuddy Chatbot initialized! Press Alt+C to open chat.');
console.log('🎤 Voice input available:', recognition !== null);