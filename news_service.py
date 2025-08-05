# news_service.py - Updated for Gemini
import requests
import os
from datetime import datetime, timedelta
from summarizer import NewsSummarizer

class NewsService:
    def __init__(self):
        self.api_key = os.environ.get('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
        self.summarizer = NewsSummarizer()
    
    def fetch_ai_news(self, include_summaries=True):
        """Fetch latest AI-related news articles with Gemini summarization"""
        try:
            if not self.api_key:
                print("⚠️  News API key not configured, using fallback news")
                return self.get_fallback_news_with_summaries() if include_summaries else self.get_fallback_news()
            
            params = {
                'q': 'artificial intelligence OR machine learning OR AI OR "deep learning" OR "neural networks" OR OpenAI OR ChatGPT',
                'language': 'en',
                'sortBy': 'publishedAt',
                'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'pageSize': 8,  # Get more articles since some might fail extraction
                'apiKey': self.api_key
            }
            
            print("📡 Fetching AI news from API...")
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            news_data = []
            successful_summaries = 0
            
            for i, article in enumerate(articles):
                if len(news_data) >= 5:  # Limit to 5 final articles
                    break
                    
                if (article.get('title') and 
                    article.get('url') and 
                    article.get('description') and
                    article.get('title') != '[Removed]' and
                    'removed' not in article.get('description', '').lower()):
                    
                    print(f"📄 Processing article {i+1}: {article['title'][:60]}...")
                    
                    article_data = {
                        'title': article['title'],
                        'url': article['url'],
                        'description': self._truncate_description(article['description']),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'published_at': article.get('publishedAt')
                    }
                    
                    # Add Gemini summarization if enabled
                    if include_summaries:
                        summary_result = self.summarizer.summarize_article(article['url'])
                        
                        article_data.update({
                            'full_text': summary_result['full_text'],
                            'summary': summary_result['summary'],
                            'summary_tokens': summary_result['summary_tokens'],
                            'extraction_status': summary_result['extraction_status']
                        })
                        
                        if summary_result['extraction_status'] == 'success':
                            successful_summaries += 1
                        
                        if summary_result['error']:
                            print(f"⚠️  Summarization warning: {summary_result['error']}")
                    
                    news_data.append(article_data)
                    
                    # Small delay between requests to be respectful
                    if include_summaries and i < len(articles) - 1:
                        import time
                        time.sleep(0.5)
            
            print(f"✅ Processed {len(news_data)} articles")
            if include_summaries:
                print(f"🤖 Successfully generated {successful_summaries} Gemini summaries")
            
            return news_data
        
        except requests.RequestException as e:
            print(f"❌ Error fetching news from API: {e}")
            return self.get_fallback_news_with_summaries() if include_summaries else self.get_fallback_news()
        except Exception as e:
            print(f"❌ Unexpected error in news fetching: {e}")
            return self.get_fallback_news_with_summaries() if include_summaries else self.get_fallback_news()
    
    def _truncate_description(self, description):
        """Truncate description to reasonable length"""
        if len(description) > 250:
            return description[:247] + '...'
        return description
    
    def get_fallback_news_with_summaries(self):
        """Fallback news with Gemini-style summaries"""
        return [
            {
                'title': 'Google Gemini Ultra Achieves New AI Reasoning Milestones',
                'url': 'https://blog.google/technology/ai/google-gemini-ultra-reasoning/',
                'description': 'Google announces breakthrough performance in AI reasoning tasks with Gemini Ultra model.',
                'summary': '• Google Gemini Ultra demonstrates superior performance on complex reasoning benchmarks\n• New model architecture enables better mathematical and logical problem-solving capabilities\n• Release planned for developers with enhanced safety features and API integration',
                'source': 'Google AI',
                'extraction_status': 'fallback',
                'summary_tokens': 45
            },
            {
                'title': 'OpenAI Introduces Advanced Function Calling in GPT-4 Turbo',
                'url': 'https://openai.com/blog/gpt-4-turbo-function-calling',
                'description': 'Enhanced function calling capabilities enable more sophisticated AI agent development.',
                'summary': '• GPT-4 Turbo now supports parallel function calling for complex multi-step operations\n• Improved accuracy in tool selection and parameter extraction for agent workflows\n• New pricing model reduces costs by 40% for function calling applications',
                'source': 'OpenAI',
                'extraction_status': 'fallback',
                'summary_tokens': 42
            },
            {
                'title': 'Meta Releases Code Llama 70B with Enhanced Programming Capabilities',
                'url': 'https://ai.meta.com/blog/code-llama-70b-programming/',
                'description': 'Meta\'s largest code generation model shows significant improvements in software development tasks.',
                'summary': '• Code Llama 70B achieves state-of-the-art performance on programming benchmarks\n• Model supports over 20 programming languages with improved code completion accuracy\n• Open source release enables developers to fine-tune for specific use cases',
                'source': 'Meta AI',
                'extraction_status': 'fallback',
                'summary_tokens': 40
            }
        ]
    
    def get_fallback_news(self):
        """Original fallback news without summaries"""
        return [
            {
                'title': 'Latest Developments in Artificial Intelligence Research',
                'url': 'https://www.nature.com/subjects/machine-learning',
                'description': 'Stay updated with cutting-edge research in AI and machine learning from leading scientific journals.',
                'source': 'Nature',
                'extraction_status': 'fallback'
            }
        ]

    def test_api_connection(self):
        """Test if the News API is working"""
        try:
            if not self.api_key:
                return False, "API key not configured"
            
            params = {
                'q': 'artificial intelligence',
                'pageSize': 1,
                'apiKey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            return True, "API connection successful"
        
        except Exception as e:
            return False, f"API connection failed: {e}"
