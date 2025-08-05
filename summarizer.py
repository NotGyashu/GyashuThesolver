# summarizer.py - Gemini Version
import os
import google.generativeai as genai
from newspaper import Article
import requests
from datetime import datetime
import time

# Configuration
GEMINI_API_KEY = os.environ.get('')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class NewsSummarizer:
    def __init__(self):
        self.use_gemini = bool(GEMINI_API_KEY)
        self.model = None
        
        if self.use_gemini:
            try:
                # Use Gemini 1.5 Flash for fast, cost-effective summarization
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini AI initialized successfully")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
                self.use_gemini = False
        
    def extract_article_text(self, url):
        """Extract full text from article URL using newspaper3k"""
        try:
            print(f"📰 Extracting text from: {url[:50]}...")
            
            article = Article(url)
            article.download()
            article.parse()
            
            # Validate extracted content
            if not article.text or len(article.text.strip()) < 100:
                return {
                    'title': article.title,
                    'text': None,
                    'authors': article.authors,
                    'publish_date': article.publish_date,
                    'status': 'failed',
                    'error': 'Article text too short or empty'
                }
            
            print(f"✅ Extracted {len(article.text)} characters")
            
            return {
                'title': article.title,
                'text': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'status': 'success'
            }
            
        except Exception as e:
            print(f"❌ Error extracting article from {url}: {e}")
            return {
                'title': None,
                'text': None,
                'authors': [],
                'publish_date': None,
                'status': 'failed',
                'error': str(e)
            }
    
    def count_tokens_estimate(self, text):
        """Estimate token count (Gemini pricing is per character, but this helps track usage)"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def summarize_with_gemini(self, text, max_chars=4000):
        """Summarize text using Google Gemini"""
        try:
            # Truncate text if too long (Gemini 1.5 Flash can handle large texts, but let's be safe)
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
                print(f"📝 Truncated text to {max_chars} characters")
            
            prompt = f"""
Please summarize the following news article in exactly 3 bullet points. 
Each bullet point should be:
- Maximum 25 words
- Focus on key facts and important information
- Written in clear, concise language
- Start with a bullet point symbol (•)

Format your response exactly like this:
• [First key point about the article]
• [Second important detail or development]  
• [Third significant fact or implication]

Article to summarize:
{text}
"""
            
            print("🤖 Generating summary with Gemini...")
            
            # Generate response with Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    candidate_count=1,
                    max_output_tokens=200,  # Keep summaries concise
                    temperature=0.3,  # Lower temperature for more consistent summaries
                )
            )
            
            if response.candidates and response.candidates[0].content:
                summary = response.candidates[0].content.parts[0].text.strip()
                
                # Clean up the summary
                summary = self._clean_summary(summary)
                
                # Estimate tokens used (for tracking purposes)
                input_tokens = self.count_tokens_estimate(text)
                output_tokens = self.count_tokens_estimate(summary)
                total_tokens = input_tokens + output_tokens
                
                print(f"✅ Summary generated ({len(summary)} chars, ~{total_tokens} tokens)")
                
                return summary, total_tokens
            else:
                print("⚠️ Gemini returned empty response")
                return self.fallback_summary(text), 0
                
        except Exception as e:
            print(f"❌ Gemini summarization error: {e}")
            # Add small delay before fallback to avoid rate limits
            time.sleep(1)
            return self.fallback_summary(text), 0
    
    def _clean_summary(self, summary):
        """Clean and format the Gemini response"""
        lines = summary.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            # Ensure line starts with bullet point
            if line and not line.startswith('•'):
                if line.startswith('-') or line.startswith('*'):
                    line = '•' + line[1:]
                elif line:
                    line = '• ' + line
            
            if line.startswith('•') and len(line) > 3:
                bullet_points.append(line)
        
        # Ensure we have exactly 3 bullet points
        if len(bullet_points) >= 3:
            return '\n'.join(bullet_points[:3])
        elif len(bullet_points) > 0:
            return '\n'.join(bullet_points)
        else:
            return summary  # Return original if formatting failed
    
    def fallback_summary(self, text):
        """Simple extractive summary fallback"""
        try:
            sentences = text.replace('\n', ' ').split('. ')
            # Clean and filter sentences
            clean_sentences = []
            for sentence in sentences[:5]:  # Take first 5 sentences
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 150:  # Reasonable length
                    clean_sentences.append(sentence)
            
            # Take best 3 sentences
            summary_sentences = clean_sentences[:3]
            if summary_sentences:
                return '\n'.join([f'• {s.strip()}.' for s in summary_sentences])
            else:
                return '• Article content could not be summarized automatically.\n• Please visit the link to read the full article.\n• Summary generation failed due to content extraction issues.'
        except Exception as e:
            print(f"❌ Fallback summary error: {e}")
            return '• Summary not available for this article.\n• Please click the link to read the full content.\n• Automatic summarization encountered an error.'
    
    def summarize_article(self, url, existing_text=None):
        """Main method to extract and summarize article"""
        result = {
            'url': url,
            'extraction_status': 'pending',
            'full_text': None,
            'summary': None,
            'summary_tokens': 0,
            'error': None
        }
        
        # Extract text if not provided
        if existing_text:
            article_text = existing_text
            result['extraction_status'] = 'success'
            result['full_text'] = article_text[:1000] + '...' if len(article_text) > 1000 else article_text
        else:
            extracted = self.extract_article_text(url)
            if extracted['status'] == 'success' and extracted['text']:
                article_text = extracted['text']
                result['full_text'] = article_text[:1000] + '...' if len(article_text) > 1000 else article_text
                result['extraction_status'] = 'success'
            else:
                result['extraction_status'] = 'failed'
                result['error'] = extracted.get('error', 'Failed to extract text')
                # Still try to create a fallback summary from description
                result['summary'] = self.fallback_summary("Article content not available")
                return result
        
        # Summarize the text
        if self.use_gemini and len(article_text.strip()) > 50:
            summary, tokens = self.summarize_with_gemini(article_text)
        else:
            summary = self.fallback_summary(article_text)
            tokens = self.count_tokens_estimate(article_text)
        
        result['summary'] = summary
        result['summary_tokens'] = tokens
        
        return result

# Test function
def test_gemini_summarizer():
    """Test the Gemini summarizer with sample articles"""
    summarizer = NewsSummarizer()
    
    print("🧪 Testing Gemini News Summarizer")
    print("=" * 50)
    
    # Test URLs - use real news URLs for testing
    test_urls = [
        "https://techcrunch.com/2025/01/01/artificial-intelligence-trends-2025/",
        "https://www.theverge.com/2024/12/31/ai-breakthrough-machine-learning",
        "https://arstechnica.com/ai/2024/12/gpt-4-successor-announced/"
    ]
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🔬 Test {i}: {url}")
        print("-" * 30)
        
        result = summarizer.summarize_article(url)
        
        print(f"Extraction Status: {result['extraction_status']}")
        
        if result['summary']:
            print(f"Summary:\n{result['summary']}")
            print(f"Estimated Tokens: {result['summary_tokens']}")
        
        if result['error']:
            print(f"Error: {result['error']}")
        
        print("\n" + "="*50)
    
    # Test with sample text
    print("\n🔬 Testing with sample text:")
    sample_text = """
    OpenAI has announced a major breakthrough in artificial intelligence with the release of GPT-5, 
    which demonstrates unprecedented capabilities in reasoning and problem-solving. The new model 
    shows significant improvements over previous versions in mathematical reasoning, code generation, 
    and creative writing tasks. Industry experts believe this could accelerate AI adoption across 
    multiple sectors including healthcare, finance, and education. The company plans to make GPT-5 
    available through its API in the coming months, with enhanced safety features and reduced 
    computational requirements.
    """
    
    result = summarizer.summarize_article("test-url", existing_text=sample_text)
    print(f"Sample Summary:\n{result['summary']}")

if __name__ == '__main__':
    test_gemini_summarizer()
