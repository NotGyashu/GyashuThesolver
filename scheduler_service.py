# scheduler_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime, time
import atexit

def send_daily_news(app):
    """Function to send daily news to users based on their preferred time and timezone"""
    with app.app_context():
        try:
            # Import inside function to avoid circular imports
            from models import User, EmailLog
            from app import db
            from news_service import NewsService
            from email_service import send_news_email
            from notification_service import NotificationService
            
            current_utc_time = datetime.now(pytz.UTC)
            print(f"📅 Checking for emails to send at {current_utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # Get all active users
            all_users = User.query.filter_by(is_active=True).all()
            
            if not all_users:
                print("ℹ️  No active subscribers found")
                return
            
            # Filter users who should receive emails at this exact time
            users_to_email = []
            for user in all_users:
                # Handle invalid timezones
                try:
                    user_tz = pytz.timezone(user.timezone)
                except pytz.UnknownTimeZoneError:
                    user_tz = pytz.timezone('Asia/Kolkata')  # Default to IST
                    print(f"⚠️  Invalid timezone '{user.timezone}' for {user.email}, using Asia/Kolkata")
                
                # Convert UTC to user's local time
                user_local_time = current_utc_time.astimezone(user_tz)
                
                # Get user's preferred time (with defaults)
                preferred_time = user.preferred_time or time(10, 0)  # Default 10:00 AM
                
                # FIX: Extract preferred time components properly
                preferred_hour = preferred_time.hour
                preferred_minute = preferred_time.minute
                
                # FIX: Compare time components directly
                if user_local_time.hour == preferred_hour and user_local_time.minute == preferred_minute:
                    # Verify frequency preference
                    if user.should_receive_email_today():
                        users_to_email.append(user)
                        print(f"⏰ {user.email} triggered at local {user_local_time.strftime('%H:%M')} "
                              f"(preferred: {preferred_hour:02d}:{preferred_minute:02d} {user_tz.zone})")
                    else:
                        print(f"ℹ️  Skipped {user.email} (already received email today)")
            
            if not users_to_email:
                print("ℹ️  No users scheduled for emails at this exact time")
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
            
            print(f"📊 Email job completed at {datetime.utcnow()}:")
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
        print("⏰ Scheduler runs every minute for exact time matching")
        
        # PRODUCTION MODE: Send emails based on user preferences
        # Check every minute for exact time matches
        scheduler.add_job(
            func=lambda: send_daily_news(app),
            trigger=CronTrigger(minute='*'),  # Every minute
            id='minute_news_check',
            name='Check for users every minute at exact preferred times',
            replace_existing=True,
            max_instances=1,
            coalesce=True
        )
        
        scheduler.start()
        
        # Ensure scheduler shuts down when application exits
        atexit.register(lambda: scheduler.shutdown())
        
        print("✅ Scheduler started successfully")
        print("⏰ PRODUCTION MODE: News will be sent at exact user-preferred times")
        print("🌍 Timezone-aware: Uses each user's configured timezone")
        print("📧 Make sure you have:")
        print("   1. Added your email via the website")
        print("   2. Configured EMAIL_USER and EMAIL_PASS in .env")
        print("   3. (Optional) Set up Slack/Teams webhooks")
        print("   4. Set your preferred time in preferences")
        
        return scheduler
        
    except Exception as e:
        print(f"❌ Error starting scheduler: {e}")
        return None