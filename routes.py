# routes.py - Updated imports
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from models import User, NewsArticle, EmailLog, Topic, UserPreference, NotificationChannel, initialize_default_topics
from app import db
from news_service import NewsService
from datetime import datetime, timedelta, time
import re
import pytz

# Create Blueprint
main = Blueprint('main', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Home Routes
@main.route('/')
def home():
    """Home page"""
    total_subscribers = User.query.filter_by(is_active=True).count()
    total_topics = Topic.query.filter_by(is_active=True).count()
    recent_articles = NewsArticle.query.order_by(NewsArticle.date_fetched.desc()).limit(3).all()

    return render_template('Index.tsx',
                         total_subscribers=total_subscribers,
                         total_topics=total_topics,
                         recent_articles=recent_articles)

# Subscription Routes
@main.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    """Handle user subscription"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter an email address.', 'danger')
            return redirect(url_for('main.subscribe'))
        
        if not validate_email(email):
            flash('Please enter a valid email address.', 'danger')
            return redirect(url_for('main.subscribe'))
        
        try:
            existing_user = User.query.filter_by(email=email).first()
            
            if existing_user:
                if existing_user.is_active:
                    flash('This email is already subscribed! 📧', 'info')
                    return redirect(url_for('main.preferences_form', email=email))
                else:
                    existing_user.is_active = True
                    existing_user.date_subscribed = datetime.utcnow()
                    db.session.commit()
                    flash('Welcome back! Your subscription has been reactivated. 🎉', 'success')
                    return redirect(url_for('main.preferences_form', email=email))
            else:
                new_user = User(email=email)
                db.session.add(new_user)
                db.session.commit()
                flash('Successfully subscribed! Now customize your preferences. 🚀', 'success')
                return redirect(url_for('main.preferences_form', email=email))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again later.', 'danger')
            print(f"Subscription error: {e}")
            return redirect(url_for('main.subscribe'))
    
    topics = Topic.query.filter_by(is_active=True).all()
    return render_template('subscribe.html', topics=topics)

@main.route('/preferences')
@main.route('/preferences/<email>')
def preferences_form(email=None):
    """Show user preferences form"""
    if not email:
        return render_template('preferences_search.html')
    
    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        flash('User not found. Please subscribe first.', 'danger')
        return redirect(url_for('main.subscribe'))
    
    topics = Topic.query.filter_by(is_active=True).all()
    timezones = [
        'Asia/Kolkata', 'America/New_York', 'Europe/London', 
        'America/Los_Angeles', 'Europe/Berlin', 'Asia/Tokyo',
        'Australia/Sydney', 'America/Toronto', 'Asia/Shanghai'
    ]
    
    return render_template('preferences.html', 
                         user=user, 
                         topics=topics, 
                         timezones=timezones)

@main.route('/update-preferences', methods=['POST'])
def update_preferences():
    """Update user preferences"""
    try:
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('main.subscribe'))
        
        # Update user settings
        preferred_time_str = request.form.get('preferred_time', '10:00')
        hour, minute = map(int, preferred_time_str.split(':'))
        user.preferred_time = time(hour, minute)
        
        user.timezone = request.form.get('timezone', 'Asia/Kolkata')
        user.frequency = request.form.get('frequency', 'daily')
        user.max_articles = int(request.form.get('max_articles', 5))
        
        # Update topic preferences
        selected_topics = request.form.getlist('topics')
        
        # Remove existing preferences
        UserPreference.query.filter_by(user_id=user.id).delete()
        
        # Add new preferences
        for topic_id in selected_topics:
            priority = request.form.get(f'priority_{topic_id}', 1)
            preference = UserPreference(
                user_id=user.id,
                topic_id=int(topic_id),
                is_active=True,
                priority=int(priority)
            )
            db.session.add(preference)
        
        db.session.commit()
        flash('Preferences updated successfully! 🎉', 'success')
        
        return render_template('preferences_success.html', user=user)
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while updating preferences.', 'danger')
        print(f"Preference update error: {e}")
        return redirect(url_for('main.preferences_form', email=email))

@main.route('/unsubscribe/<email>')
def unsubscribe(email):
    """Handle user unsubscription"""
    try:
        user = User.query.filter_by(email=email.lower()).first()
        
        if user and user.is_active:
            user.is_active = False
            db.session.commit()
            flash('Successfully unsubscribed. We\'ll miss you! 👋', 'info')
        else:
            flash('Email not found or already unsubscribed.', 'info')
            
    except Exception as e:
        db.session.rollback()
        flash('An error occurred.', 'danger')
        print(f"Unsubscription error: {e}")
    
    return render_template('unsubscribe_success.html')

# Preview and Test Routes
@main.route('/preview-email')
def preview_email():
    """Preview email template"""
    sample_articles = [
        {
            'title': 'Breakthrough in Large Language Models: GPT-5 Achieves AGI Milestone',
            'url': 'https://example.com/gpt5-breakthrough',
            'description': 'OpenAI announces GPT-5 with unprecedented reasoning capabilities, marking a significant step toward artificial general intelligence.'
        },
        {
            'title': 'New Computer Vision Model Surpasses Human Performance in Medical Imaging',
            'url': 'https://example.com/medical-cv',
            'description': 'Researchers develop AI system that detects cancer with 99.8% accuracy, outperforming radiologists in clinical trials.'
        }
    ]
    
    return render_template('email_template.html', 
                         articles=sample_articles, 
                         preview=True,
                         preview_date=datetime.now().strftime('%A, %B %d, %Y'))

# API Routes
@main.route('/api/user/<email>')
def get_user_info(email):
    """Get user information via API"""
    try:
        user = User.query.filter_by(email=email.lower()).first()
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/api/topics')
def get_topics():
    """Get all available topics"""
    try:
        topics = Topic.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'topics': [topic.to_dict() for topic in topics]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/test-send-now')
def test_send_now():
    """Manual test email sending"""
    try:
        from news_service import NewsService
        from email_service import send_news_email
        
        users = User.query.filter_by(is_active=True).all()
        if not users:
            return jsonify({
                'success': False,
                'message': 'No active subscribers found.'
            })
        
        news_service = NewsService()
        articles = news_service.fetch_ai_news()
        
        if not articles:
            articles = news_service.get_fallback_news()
        
        results = []
        for user in users:
            success = send_news_email(user.email, articles)
            results.append({
                'email': user.email,
                'success': success
            })
        
        return jsonify({
            'success': True,
            'message': f'Test emails sent to {len(users)} subscribers',
            'results': results,
            'articles_count': len(articles)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Admin Routes
@main.route('/admin')
def admin_dashboard():
    """Basic admin dashboard"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_topics = Topic.query.filter_by(is_active=True).count()
        total_articles = NewsArticle.query.count()
        
        recent_subscribers = User.query.order_by(User.date_subscribed.desc()).limit(10).all()
        popular_topics = db.session.query(Topic, db.func.count(UserPreference.id).label('count'))\
            .join(UserPreference).filter(UserPreference.is_active==True)\
            .group_by(Topic.id).order_by(db.desc('count')).limit(5).all()
        
        return render_template('admin.html',
                             total_users=total_users,
                             active_users=active_users,
                             total_topics=total_topics,
                             total_articles=total_articles,
                             recent_subscribers=recent_subscribers,
                             popular_topics=popular_topics)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error Handlers
@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Health Check
@main.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# Add these routes to your existing routes.py

@main.route('/notifications/setup/<email>')
def notification_setup(email):
    """Setup notification channels for user"""
    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        flash('User not found. Please subscribe first.', 'danger')
        return redirect(url_for('main.subscribe'))
    
    channels = NotificationChannel.query.filter_by(user_id=user.id).all()
    
    return render_template('notification_setup.html', user=user, channels=channels)

@main.route('/notifications/add', methods=['POST'])
def add_notification_channel():
    """Add new notification channel with webhook testing"""
    try:
        email = request.form.get('email', '').strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        channel_type = request.form.get('channel_type')
        channel_name = request.form.get('channel_name', '').strip()
        webhook_url = request.form.get('webhook_url', '').strip()
        
        if not channel_type or not webhook_url:
            return jsonify({'success': False, 'error': 'Channel type and webhook URL required'}), 400
        
        # Validate webhook URL format
        if channel_type == 'slack' and 'hooks.slack.com' not in webhook_url:
            return jsonify({'success': False, 'error': 'Invalid Slack webhook URL format'}), 400
        
        # Test the webhook with a sample message
        from notification_service import NotificationService
        service = NotificationService()
        
        test_articles = [{
            'title': '🧪 Test Notification - AI News Daily Setup Complete!',
            'url': 'https://ai-news-daily.com/test',
            'description': 'This is a test notification to verify your Slack integration is working correctly. Your daily AI news will be delivered here!',
            'summary': '• Your Slack integration has been configured successfully\n• You will receive daily AI news updates with AI-powered summaries\n• Integration test completed - everything is working perfectly!',
            'source': 'AI News Daily',
            'extraction_status': 'success',
            'summary_tokens': 42
        }]
        
        if channel_type == 'slack':
            success, error = service.send_slack_notification(
                webhook_url, test_articles, user.email, channel_name or 'your channel'
            )
        else:
            return jsonify({'success': False, 'error': f'{channel_type} integration not yet implemented'}), 400
        
        if not success:
            return jsonify({'success': False, 'error': f'Webhook test failed: {error}'}), 400
        
        # Check if channel already exists
        existing_channel = NotificationChannel.query.filter_by(
            user_id=user.id,
            channel_type=channel_type,
            webhook_url=webhook_url
        ).first()
        
        if existing_channel:
            existing_channel.is_active = True
            existing_channel.channel_name = channel_name
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Existing {channel_type.title()} channel reactivated! Check your channel for the test message.',
                'channel': existing_channel.to_dict()
            })
        
        # Create new channel
        channel = NotificationChannel(
            user_id=user.id,
            channel_type=channel_type,
            channel_name=channel_name,
            webhook_url=webhook_url,
            is_active=True
        )
        
        db.session.add(channel)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{channel_type.title()} channel added successfully! 🎉 Check your channel for the test message.',
            'channel': channel.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

@main.route('/notifications/test/<int:channel_id>')
def test_notification_channel(channel_id):
    """Test a specific notification channel"""
    try:
        channel = NotificationChannel.query.get_or_404(channel_id)
        
        from notification_service import NotificationService
        service = NotificationService()
        
        test_articles = [{
            'title': f'🧪 Manual Test - {channel.channel_type.title()} Integration Working!',
            'url': 'https://ai-news-daily.com/manual-test',
            'description': f'This is a manual test of your {channel.channel_type} notification integration. Everything looks great!',
            'summary': '• Manual test initiated by user from the web interface\n• Notification system functioning properly across all channels\n• Ready to receive daily AI news updates with summaries',
            'source': 'AI News Daily',
            'extraction_status': 'success',
            'summary_tokens': 35
        }]
        
        if channel.channel_type == 'slack':
            success, error = service.send_slack_notification(
                channel.webhook_url, test_articles, channel.user.email, channel.channel_name
            )
        else:
            return jsonify({'success': False, 'error': f'{channel.channel_type} testing not implemented yet'}), 400
        
        if success:
            channel.last_sent_at = datetime.utcnow()
            db.session.commit()
        
        return jsonify({
            'success': success,
            'message': 'Test notification sent to your channel! 🎉' if success else f'Test failed: {error}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/notifications/toggle/<int:channel_id>', methods=['POST'])
def toggle_notification_channel(channel_id):
    """Toggle notification channel active status"""
    try:
        channel = NotificationChannel.query.get_or_404(channel_id)
        
        channel.is_active = not channel.is_active
        db.session.commit()
        
        status = "enabled" if channel.is_active else "disabled"
        return jsonify({
            'success': True,
            'message': f'{channel.channel_type.title()} channel {status}',
            'is_active': channel.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@main.route('/notifications/delete/<int:channel_id>', methods=['DELETE'])
def delete_notification_channel(channel_id):
    """Delete a notification channel"""
    try:
        channel = NotificationChannel.query.get_or_404(channel_id)
        
        db.session.delete(channel)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{channel.channel_type.title()} channel deleted'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
