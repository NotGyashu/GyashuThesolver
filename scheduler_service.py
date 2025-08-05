# scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime
import atexit

def send_daily_news(app):
    """Function to send daily news to all active users with multi-channel notifications"""
    with app.app_context():
        try:
            # Import inside function to avoid circular imports
            from models import User, EmailLog
            from app import db
            from news_service import NewsService
            from email_service import send_news_email
            from notification_service import NotificationService
            
            print(f"🧪 Starting TEST news job at {datetime.now()}")
            
            # Get all active users
            users = User.query.filter_by(is_active=True).all()
            print(f"👥 Found {len(users)} active subscribers")
            
            if not users:
                print("ℹ️  No active subscribers found")
                print("💡 Go to http://localhost:5000 and subscribe with your email first!")
                return
            
            # Fetch latest AI news
            news_service = NewsService()
            print("📡 Fetching news articles...")
            news_articles = news_service.fetch_ai_news()
            
            if not news_articles:
                print("⚠️  No news articles from API, using fallback")
                news_articles = news_service.get_fallback_news()
            
            print(f"📰 Sending {len(news_articles)} articles to {len(users)} subscribers")
            
            # Initialize notification service
            notification_service = NotificationService()
            
            # Track email sending
            successful_sends = 0
            failed_sends = 0
            
            # Send emails and notifications to all users
            for user in users:
                try:
                    print(f"📧 Processing user: {user.email}...")
                    
                    # Send email (existing functionality)
                    email_success = send_news_email(user.email, news_articles)
                    
                    # Send to other notification channels (Slack, Teams, etc.)
                    notification_results = notification_service.send_notifications_to_user(user, news_articles)
                    
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
            
            print(f"📊 TEST email job completed at {datetime.now()}:")
            print(f"   ✅ Successful sends: {successful_sends}")
            print(f"   ❌ Failed sends: {failed_sends}")
            print(f"   📰 Articles sent: {len(news_articles)}")
            print(f"   ⏰ Next email in 2 minutes...")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Error in send_daily_news: {e}")
            try:
                from app import db
                db.session.rollback()
            except Exception as rollback_error:
                print(f"❌ Error during rollback: {rollback_error}")

def start_scheduler(app):
    """Start the background scheduler"""
    try:
        scheduler = BackgroundScheduler(daemon=True)
        
        print("🧪 STARTING TEST MODE - Emails every 2 minutes")
        print("⚠️  Remember to change back to production schedule after testing!")
        
        # TEST MODE: Run every 2 minutes for immediate testing
        scheduler.add_job(
            func=lambda: send_daily_news(app),
            trigger=CronTrigger(minute='*/2'),  # Every 2 minutes
            id='test_news_job',
            name='Send AI news every 2 minutes (TEST MODE)',
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        
        # PRODUCTION MODE: Uncomment this for 10:00 AM IST daily
        # ist = pytz.timezone('Asia/Kolkata')
        # scheduler.add_job(
        #     func=lambda: send_daily_news(app),
        #     trigger=CronTrigger(hour=10, minute=0, timezone=ist),
        #     id='daily_news_job',
        #     name='Send daily AI news at 10:00 AM IST',
        #     replace_existing=True,
        #     max_instances=1,
        #     coalesce=True
        # )
        
        scheduler.start()
        
        # Ensure scheduler shuts down when application exits
        atexit.register(lambda: scheduler.shutdown())
        
        print("✅ Scheduler started successfully")
        print("⏰ TEST MODE: News will be sent every 2 minutes")
        print("📧 Make sure you have:")
        print("   1. Added your email via the website")
        print("   2. Configured EMAIL_USER and EMAIL_PASS in .env")
        print("   3. (Optional) Set up Slack/Teams webhooks")
        
        return scheduler
        
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        return None
