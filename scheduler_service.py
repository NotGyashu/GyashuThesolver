# scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime
import atexit

def send_daily_news(app):
    """Function to send daily news to users based on their preferred time"""
    with app.app_context():
        try:
            # Import inside function to avoid circular imports
            from models import User, EmailLog
            from app import db
            from news_service import NewsService
            from email_service import send_news_email
            from notification_service import NotificationService
            
            current_time = datetime.now()
            print(f"📅 Checking for emails to send at {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get all active users
            all_users = User.query.filter_by(is_active=True).all()
            
            if not all_users:
                print("ℹ️  No active subscribers found")
                return
            
            # Filter users who should receive emails at this time
            users_to_email = []
            for user in all_users:
                user_tz = pytz.timezone(user.timezone or 'Asia/Kolkata')
                current_user_time = current_time.astimezone(user_tz)
                user_preferred_hour = user.preferred_time.hour if user.preferred_time else 10
                user_preferred_minute = user.preferred_time.minute if user.preferred_time else 0
                
                # Check if current time matches user's preferred time (within the hour)
                if (current_user_time.hour == user_preferred_hour and 
                    0 <= current_user_time.minute <= 59):
                    
                    # Check if user should receive email today (based on frequency)
                    if user.should_receive_email_today():
                        users_to_email.append(user)
                        print(f"� {user.email} scheduled for email (preferred time: {user_preferred_hour:02d}:{user_preferred_minute:02d} {user.timezone})")
            
            if not users_to_email:
                print("ℹ️  No users scheduled for emails at this time")
                return
            
            print(f"👥 Found {len(users_to_email)} users to email out of {len(all_users)} total subscribers")
            
            # Fetch latest AI news
            news_service = NewsService()
            print("📡 Fetching news articles...")
            news_articles = news_service.fetch_ai_news()
            
            if not news_articles:
                print("⚠️  No news articles from API, using fallback")
                news_articles = news_service.get_fallback_news()
            
            print(f"📰 Sending {len(news_articles)} articles to {len(users_to_email)} subscribers")
            
            # Initialize notification service
            notification_service = NotificationService()
            
            # Track email sending
            successful_sends = 0
            failed_sends = 0
            
            # Send emails and notifications to all users
            for user in users_to_email:
                try:
                    print(f"📧 Processing user: {user.email}...")
                    
                    # Limit articles based on user preference
                    user_articles = news_articles[:user.max_articles]
                    print(f"📊 Sending {len(user_articles)} articles to {user.email} (user limit: {user.max_articles})")
                    
                    # Send email (existing functionality)
                    email_success = send_news_email(user.email, user_articles)
                    
                    # Send to other notification channels (Slack, Teams, etc.)
                    notification_results = notification_service.send_notifications_to_user(user, user_articles)
                    
                    # Log email attempt
                    email_log = EmailLog(
                        user_id=user.id,
                        articles_count=len(news_articles),
                        status='sent' if email_success else 'failed'
                    )
                    
                    if email_success:
                        successful_sends += 1
                        user.last_email_sent = datetime.utcnow()
                        print(f"✅ Email sent successfully to {user.email}")
                    else:
                        failed_sends += 1
                        email_log.error_message = "Failed to send email"
                        print(f"❌ Failed to send email to {user.email}")
                    
                    # Log notification results
                    channels_sent = []
                    for channel_type, result in notification_results.items():
                        if result['sent']:
                            channels_sent.append(channel_type)
                    
                    if channels_sent:
                        print(f"✅ Also sent to {user.email} via: {', '.join(channels_sent)}")
                    
                    db.session.add(email_log)
                    
                except Exception as e:
                    failed_sends += 1
                    print(f"❌ Error sending to {user.email}: {e}")
                    
                    # Log the error
                    try:
                        error_log = EmailLog(
                            user_id=user.id,
                            articles_count=len(news_articles),
                            status='failed',
                            error_message=str(e)
                        )
                        db.session.add(error_log)
                    except Exception as log_error:
                        print(f"❌ Error logging failure: {log_error}")
            
            # Commit all changes
            try:
                db.session.commit()
                print("💾 Database updated successfully")
            except Exception as e:
                print(f"❌ Error committing to database: {e}")
                db.session.rollback()
            
            print(f"📊 Email job completed at {datetime.now()}:")
            print(f"   ✅ Successful sends: {successful_sends}")
            print(f"   ❌ Failed sends: {failed_sends}")
            print(f"   📰 Articles sent: {len(news_articles)}")
            print(f"   👥 Users emailed: {len(users_to_email)}")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error in send_daily_news: {e}")
            try:
                from app import db
                db.session.rollback()
            except Exception as rollback_error:
                print(f"❌ Error during rollback: {rollback_error}")

def start_scheduler(app):
    """Start the background scheduler with user preference-based timing"""
    try:
        scheduler = BackgroundScheduler(daemon=True)
        
        print("🚀 STARTING PRODUCTION MODE - Emails sent at user-preferred times")
        
        # PRODUCTION MODE: Send emails based on user preferences
        # We'll check every hour for users who should receive emails
        scheduler.add_job(
            func=lambda: send_daily_news(app),
            trigger=CronTrigger(minute=0),  # Every hour at minute 0
            id='hourly_news_check',
            name='Check for users who should receive news this hour',
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        
        scheduler.start()
        
        # Ensure scheduler shuts down when application exits
        atexit.register(lambda: scheduler.shutdown())
        
        print("✅ Scheduler started successfully")
        print("⏰ PRODUCTION MODE: News will be sent at user-preferred times")
        print("📧 Default time: 10:00 AM IST for new users")
        print("📧 Make sure you have:")
        print("   1. Added your email via the website")
        print("   2. Configured EMAIL_USER and EMAIL_PASS in .env")
        print("   3. (Optional) Set up Slack/Teams webhooks")
        print("   4. Set your preferred time in preferences")
        
        return scheduler
        
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        return None
