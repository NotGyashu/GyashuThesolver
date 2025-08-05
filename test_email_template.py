# test_email_template.py
from app import create_app
from flask import render_template
from datetime import datetime

def test_email_template():
    """Test the enhanced email template with summaries"""
    app = create_app()
    
    with app.app_context():
        print("🧪 Testing Enhanced Email Template with Gemini Summaries")
        print("=" * 60)
        
        # Sample articles with Gemini summaries
        sample_articles = [
            {
                'title': 'OpenAI Releases GPT-5 with Revolutionary Reasoning Capabilities',
                'url': 'https://openai.com/blog/gpt-5-reasoning',
                'description': 'OpenAI\'s latest language model demonstrates unprecedented performance in complex reasoning tasks, setting new benchmarks across multiple domains.',
                'summary': '• GPT-5 achieves 95% accuracy on advanced mathematical reasoning benchmarks, surpassing human performance\n• New architecture enables multi-step logical thinking and planning for complex problem-solving tasks\n• Release includes enhanced safety measures and 40% reduction in computational costs compared to GPT-4',
                'source': 'OpenAI Blog',
                'extraction_status': 'success',
                'summary_tokens': 85
            },
            {
                'title': 'Google DeepMind\'s AlphaFold 3 Predicts All Biological Molecules',
                'url': 'https://deepmind.google/discover/blog/alphafold-3-predicts-all-molecules',
                'description': 'Revolutionary AI system can predict the structure and interactions of all biological molecules, accelerating drug discovery and biological research.',
                'summary': '• AlphaFold 3 extends protein folding predictions to include DNA, RNA, and small molecules interactions\n• Accuracy improved by 50% for protein-drug binding predictions, enabling faster pharmaceutical development\n• Free access provided to researchers worldwide through updated AlphaFold database with 200M+ structures',
                'source': 'Google DeepMind',
                'extraction_status': 'success',
                'summary_tokens': 78
            },
            {
                'title': 'Meta Introduces Llama 3 with Advanced Code Generation',
                'url': 'https://ai.meta.com/blog/llama-3-code-generation',
                'description': 'Meta\'s latest open-source AI model shows significant improvements in programming tasks and software development assistance.',
                'summary': '• Llama 3 achieves 87% pass rate on HumanEval coding benchmark, matching proprietary models\n• New 405B parameter version supports 12 programming languages with context length up to 128k tokens\n• Open-source release includes commercial license allowing deployment in production applications worldwide',
                'source': 'Meta AI',
                'extraction_status': 'success',
                'summary_tokens': 72
            }
        ]
        
        # Render the email template
        html_content = render_template('email_template.html',
                                     articles=sample_articles,
                                     current_date=datetime.now().strftime('%A, %B %d, %Y'),
                                     user_email='test@example.com',
                                     preview=False)
        
        # Save to file for preview
        with open('email_preview.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ Email template rendered successfully!")
        print("📁 Preview saved to 'email_preview.html'")
        print("🌐 Open 'email_preview.html' in your browser to see the result")
        
        print(f"\n📊 Template Stats:")
        print(f"   📰 Articles: {len(sample_articles)}")
        print(f"   🤖 AI Summaries: {len([a for a in sample_articles if a.get('summary')])}")
        print(f"   🎯 Total Tokens: {sum(a.get('summary_tokens', 0) for a in sample_articles)}")

if __name__ == '__main__':
    test_email_template()
