# notification_service.py - Complete Slack Integration
import requests
import json
from datetime import datetime
from models import NotificationChannel, EmailLog
from app import db

class NotificationService:
    def __init__(self):
        self.slack_timeout = 10
        self.teams_timeout = 10
        print("📢 NotificationService initialized with Slack integration")
        
    def format_articles_for_slack(self, articles, user_email):
        """Format articles for Slack message with rich blocks"""
        if not articles:
            return {
                "text": "🤖 Daily AI News Update - No articles today",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "🤖 Daily AI News Update"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "No AI news articles available today. Check back tomorrow! 📰"
                        }
                    }
                ]
            }
        
        # Create rich Slack blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🤖 Daily AI News Update ({len(articles)} articles)",
                    "emoji": True
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📅 {datetime.now().strftime('%A, %B %d, %Y')} • For: `{user_email}` • Powered by Gemini AI"
                    }
                ]
            },
            {
                "type": "divider"
            }
        ]
        
        # Add each article as a rich block
        for i, article in enumerate(articles[:4], 1):  # Limit to 4 for Slack readability
            # Article header with title and source
            article_blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{i}. {article['title']}*\n_{article.get('source', 'Unknown Source')}_"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📖 Read Article",
                            "emoji": True
                        },
                        "url": article['url'],
                        "action_id": f"read_article_{i}"
                    }
                }
            ]
            
            # Add AI summary if available
            if article.get('summary'):
                # Clean up the summary for Slack
                summary_text = article['summary'].replace('•', '▪').replace('\n', '\n')
                article_blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🧠 *AI Summary (Gemini):*\n{summary_text}"
                    }
                })
            
            # Add brief description
            article_blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"📄 {article['description']}"
                    }
                ]
            })
            
            # Add extraction status if available
            if article.get('extraction_status'):
                status_emoji = "✅" if article['extraction_status'] == 'success' else "⚠️"
                tokens_text = f" • ~{article.get('summary_tokens', 0)} tokens" if article.get('summary_tokens') else ""
                article_blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"{status_emoji} Status: {article['extraction_status'].title()}{tokens_text}"
                        }
                    ]
                })
            
            # Add divider between articles (except last one)
            if i < min(len(articles), 4):
                article_blocks.append({"type": "divider"})
            
            blocks.extend(article_blocks)
        
        # Add footer
        blocks.extend([
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🚀 *AI News Daily* • Stay ahead with AI-powered summaries delivered to your channels!"
                }
            }
        ])
        
        return {
            "text": f"🤖 Daily AI News Update - {len(articles)} articles with AI summaries",
            "blocks": blocks,
            "unfurl_links": False,
            "unfurl_media": False
        }
    
    def send_slack_notification(self, webhook_url, articles, user_email, channel_name=""):
        """Send notification to Slack"""
        try:
            payload = self.format_articles_for_slack(articles, user_email)
            
            print(f"📤 Sending Slack notification to {channel_name or 'webhook'}...")
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=self.slack_timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            
            if response.text.strip() == "ok":
                print(f"✅ Slack notification sent successfully to {channel_name}!")
                return True, "Notification sent successfully"
            else:
                error_msg = f"Slack API returned: {response.text}"
                print(f"❌ {error_msg}")
                return False, error_msg
            
        except requests.exceptions.Timeout:
            error_msg = "Slack webhook request timed out"
            print(f"❌ {error_msg}")
            return False, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Slack webhook request failed: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error sending Slack notification: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg
    
    def send_notifications_to_user(self, user, articles):
        """Send notifications to all active channels for a user"""
        results = {
            'email': {'sent': False, 'error': None},
            'slack': {'sent': False, 'error': None},
            'teams': {'sent': False, 'error': None},
            'whatsapp': {'sent': False, 'error': None}
        }
        
        try:
            # Check if user has any notification channels
            if not hasattr(user, 'notification_channels') or not user.notification_channels:
                print(f"📢 No notification channels configured for {user.email}")
                return results
            
            # Send to all active notification channels
            for channel in user.notification_channels:
                if not channel.is_active:
                    continue
                
                if channel.channel_type == 'slack' and channel.webhook_url:
                    success, error = self.send_slack_notification(
                        channel.webhook_url, 
                        articles, 
                        user.email, 
                        channel.channel_name
                    )
                    results['slack'] = {'sent': success, 'error': error}
                    if success:
                        channel.last_sent_at = datetime.utcnow()
                
                elif channel.channel_type == 'teams' and channel.webhook_url:
                    # Teams integration - placeholder for now
                    print(f"📤 Teams integration not yet implemented for {channel.channel_name}")
                    results['teams'] = {'sent': False, 'error': 'Not implemented yet'}
            
            # Commit channel updates
            db.session.commit()
            
        except Exception as e:
            print(f"❌ Error sending notifications to user {user.email}: {e}")
            db.session.rollback()
        
        return results

# Test function
def test_slack_notification():
    """Test Slack notification with sample data"""
    service = NotificationService()
    
    sample_articles = [
        {
            'title': 'OpenAI Releases GPT-5 with Enhanced Reasoning Capabilities',
            'url': 'https://openai.com/blog/gpt-5',
            'description': 'Revolutionary AI model demonstrates unprecedented reasoning capabilities across multiple domains.',
            'summary': '• GPT-5 achieves 95% accuracy on complex reasoning tasks, surpassing human performance\n• New architecture enables multi-step logical thinking and planning capabilities\n• 40% reduction in computational costs compared to GPT-4 with improved efficiency',
            'source': 'OpenAI',
            'extraction_status': 'success',
            'summary_tokens': 85
        },
        {
            'title': 'Google DeepMind Announces AlphaFold 3 for All Biological Molecules',
            'url': 'https://deepmind.google/alphafold-3',
            'description': 'Revolutionary AI system extends protein folding predictions to all biological molecules.',
            'summary': '• AlphaFold 3 predicts structure of DNA, RNA, and small molecules with 95% accuracy\n• Free access provided to researchers worldwide through updated database interface\n• Drug discovery timelines expected to reduce by 50% with new molecular predictions',
            'source': 'Google DeepMind',
            'extraction_status': 'success',
            'summary_tokens': 78
        }
    ]
    
    # Replace with your actual Slack webhook URL for testing
    test_webhook = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    
    print("🧪 Testing Slack notification...")
    print("⚠️  Update test_webhook variable with your actual Slack webhook URL")
    
    if "YOUR/SLACK/WEBHOOK" in test_webhook:
        print("❌ Please update the webhook URL in test_slack_notification() function")
        return
    
    success, error = service.send_slack_notification(
        test_webhook, 
        sample_articles, 
        "test@example.com",
        "#ai-news"
    )
    
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
    if error:
        print(f"Error: {error}")

if __name__ == '__main__':
    test_slack_notification()
