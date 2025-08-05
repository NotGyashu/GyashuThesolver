# test_gemini_summarization.py
from app import create_app
from news_service import NewsService
from summarizer import NewsSummarizer

def test_gemini_integration():
    """Test Gemini integration with the news service"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Gemini AI News Summarization Integration")
        print("="*60)
        
        # Test individual summarizer
        print("\n1️⃣ Testing Gemini Summarizer directly:")
        summarizer = NewsSummarizer()
        
        sample_text = """
        Anthropic has released Claude 3, a new family of AI models that demonstrates 
        significant improvements in reasoning, math, and coding capabilities. The models 
        come in three sizes: Haiku, Sonnet, and Opus, with Opus being the most capable. 
        Claude 3 Opus outperforms GPT-4 on most benchmarks and shows better understanding 
        of nuanced instructions. The company emphasizes safety and has implemented 
        constitutional AI training methods to reduce harmful outputs.
        """
        
        result = summarizer.summarize_article("test", existing_text=sample_text)
        print(f"Summary: {result['summary']}")
        print(f"Tokens: {result['summary_tokens']}")
        
        # Test news service integration
        print("\n2️⃣ Testing News Service with Gemini:")
        news_service = NewsService()
        articles = news_service.fetch_ai_news(include_summaries=True)
        
        print(f"\n📊 Results: {len(articles)} articles processed")
        
        for i, article in enumerate(articles[:2], 1):
            print(f"\n📰 Article {i}:")
            print(f"Title: {article['title']}")
            print(f"Source: {article.get('source', 'Unknown')}")
            print(f"Status: {article.get('extraction_status', 'unknown')}")
            
            if article.get('summary'):
                print(f"Gemini Summary:\n{article['summary']}")
                print(f"Tokens: {article.get('summary_tokens', 0)}")
            
            print("-" * 40)

if __name__ == '__main__':
    test_gemini_integration()
