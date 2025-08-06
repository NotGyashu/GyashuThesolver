# models.py
from app import db
from datetime import datetime, time
import pytz
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    date_subscribed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False,index=True)
    last_email_sent = db.Column(db.DateTime)
    
    # New fields for customization
    preferred_time = db.Column(db.Time, default=time(10, 0))  # Default 10:00 AM
    timezone = db.Column(db.String(50), default='Asia/Kolkata',index=True)  # User's timezone
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    max_articles = db.Column(db.Integer, default=5)  # Max articles per email
    
    # Relationships
    preferences = db.relationship('UserPreference', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"User('{self.email}', active={self.is_active})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'date_subscribed': self.date_subscribed.isoformat() if self.date_subscribed else None,
            'is_active': self.is_active,
            'last_email_sent': self.last_email_sent.isoformat() if self.last_email_sent else None,
            'preferred_time': self.preferred_time.strftime('%H:%M') if self.preferred_time else '10:00',
            'timezone': self.timezone,
            'frequency': self.frequency,
            'max_articles': self.max_articles,
            'preferences': [pref.to_dict() for pref in self.preferences]
        }
    
    def get_preferred_topics(self):
        """Get list of user's preferred topic names"""
        return [pref.topic.name for pref in self.preferences if pref.is_active]
    
    def should_receive_email_today(self):
        """Check if user should receive email today based on frequency"""
        return True
        if not self.is_active:
            return False
            
        # If user has never received an email, they should receive one
        if not self.last_email_sent:
            return True
        
        # Calculate days since last email
        days_since_last = (datetime.utcnow().date() - self.last_email_sent.date()).days
        
        if self.frequency == 'daily':
            # Send daily if it's been at least 1 day since last email
            return days_since_last >= 1
        elif self.frequency == 'weekly':
            return days_since_last >= 7
        elif self.frequency == 'monthly':
            return days_since_last >= 30
        
        return False

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    keywords = db.Column(db.Text)  # Comma-separated keywords
    icon = db.Column(db.String(50))  # Emoji or icon class
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    preferences = db.relationship('UserPreference', backref='topic', lazy=True)
    articles = db.relationship('NewsArticle', backref='topic', lazy=True)
    
    def __repr__(self):
        return f"Topic('{self.name}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'icon': self.icon,
            'is_active': self.is_active,
            'subscriber_count': len([p for p in self.preferences if p.is_active])
        }

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.Integer, default=1)  # 1=high, 2=medium, 3=low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'topic_id', name='unique_user_topic'),)
    
    def __repr__(self):
        return f"UserPreference(user={self.user_id}, topic={self.topic_id})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic_id': self.topic_id,
            'topic_name': self.topic.name if self.topic else None,
            'topic_icon': self.topic.icon if self.topic else None,
            'is_active': self.is_active,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class NewsArticle(db.Model):
    __tablename__ = 'news_articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100))
    published_at = db.Column(db.DateTime)
    date_fetched = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50), default='AI')
    
    # Enhanced fields
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    relevance_score = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f"NewsArticle('{self.title[:50]}...')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'description': self.description,
            'source': self.source,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'date_fetched': self.date_fetched.isoformat() if self.date_fetched else None,
            'topic_name': self.topic.name if self.topic else self.category,
            'topic_id': self.topic_id,
            'category': self.category,
            'relevance_score': self.relevance_score
        }

class EmailLog(db.Model):
    __tablename__ = 'email_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    email_sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    articles_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='sent')  # sent, failed, pending
    error_message = db.Column(db.Text)
    
    # Enhanced fields
    topics_included = db.Column(db.Text)  # JSON string of topics
    delivery_time_scheduled = db.Column(db.DateTime)
    user_timezone = db.Column(db.String(50))
    
    # Relationship
    user = db.relationship('User', backref=db.backref('email_logs', lazy=True))
    
    def __repr__(self):
        return f"EmailLog(user_id={self.user_id}, status='{self.status}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user.email if self.user else None,
            'email_sent_at': self.email_sent_at.isoformat(),
            'delivery_time_scheduled': self.delivery_time_scheduled.isoformat() if self.delivery_time_scheduled else None,
            'articles_count': self.articles_count,
            'status': self.status,
            'error_message': self.error_message,
            'topics_included': self.topics_included,
            'user_timezone': self.user_timezone
        }

# Initialize default topics
def initialize_default_topics():
    """Initialize default topics in the database"""
    default_topics = [
        {
            'name': 'Machine Learning',
            'description': 'ML algorithms, neural networks, and model developments',
            'keywords': 'machine learning,ML,neural networks,deep learning,algorithms',
            'icon': '🧠'
        },
        {
            'name': 'Natural Language Processing',
            'description': 'Language models, chatbots, and text analysis',
            'keywords': 'NLP,natural language processing,GPT,BERT,language models,chatbots',
            'icon': '💬'
        },
        {
            'name': 'Computer Vision',
            'description': 'Image recognition, object detection, and visual AI',
            'keywords': 'computer vision,image recognition,object detection,CNN,visual AI',
            'icon': '👁️'
        },
        {
            'name': 'AI Ethics & Safety',
            'description': 'Responsible AI, bias prevention, and safety measures',
            'keywords': 'AI ethics,AI safety,bias,responsible AI,fairness,explainable AI',
            'icon': '⚖️'
        },
        {
            'name': 'AI Tools & Frameworks',
            'description': 'New AI tools, platforms, and development frameworks',
            'keywords': 'AI tools,TensorFlow,PyTorch,Hugging Face,OpenAI,frameworks',
            'icon': '🛠️'
        },
        {
            'name': 'AI Startups & Business',
            'description': 'AI startup news, funding, and business applications',
            'keywords': 'AI startups,funding,business,investment,market,unicorns',
            'icon': '🚀'
        },
        {
            'name': 'Robotics & Automation',
            'description': 'Robotics advances and automation technologies',
            'keywords': 'robotics,automation,robots,autonomous systems,manufacturing',
            'icon': '🤖'
        },
        {
            'name': 'AI Research & Papers',
            'description': 'Latest research publications and scientific breakthroughs',
            'keywords': 'AI research,papers,publications,science,breakthrough,academic',
            'icon': '📚'
        }
    ]
    
    for topic_data in default_topics:
        existing_topic = Topic.query.filter_by(name=topic_data['name']).first()
        if not existing_topic:
            topic = Topic(**topic_data)
            db.session.add(topic)
    
    try:
        db.session.commit()
        print("✅ Default topics initialized")
    except Exception as e:
        print(f"❌ Error initializing topics: {e}")
        db.session.rollback()



# models.py - Add this new model
class NotificationChannel(db.Model):
    __tablename__ = 'notification_channels'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    channel_type = db.Column(db.String(20), nullable=False)  # slack, teams, whatsapp
    channel_name = db.Column(db.String(100))  # e.g., "#ai-news", "General", etc.
    webhook_url = db.Column(db.String(500))  # Slack/Teams webhook URL
    phone_number = db.Column(db.String(20))  # For WhatsApp
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sent_at = db.Column(db.DateTime)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('notification_channels', lazy=True))
    
    def __repr__(self):
        return f"NotificationChannel('{self.channel_type}', user={self.user_id})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'channel_type': self.channel_type,
            'channel_name': self.channel_name,
            'webhook_url': self.webhook_url[:50] + '...' if self.webhook_url else None,
            'phone_number': self.phone_number,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None
        }
