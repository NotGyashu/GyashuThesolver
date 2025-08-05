# migrate_slack_integration.py
from app import create_app, db
from models import NotificationChannel

def migrate_slack_integration():
    """Ensure notification_channels table exists"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Setting up Slack integration...")
        
        try:
            # Create tables if they don't exist
            db.create_all()
            print("✅ Database tables ready")
            
            # Check existing channels
            channels = NotificationChannel.query.all()
            print(f"📊 Found {len(channels)} existing notification channels")
            
            print("🎉 Slack integration setup complete!")
            print("📱 Users can now setup Slack channels at: /notifications/setup/<email>")
            
        except Exception as e:
            print(f"❌ Error setting up Slack integration: {e}")

if __name__ == '__main__':
    migrate_slack_integration()
