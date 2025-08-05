import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Navigation from '@/components/Navigation';
import StatsCard from '@/components/StatsCard';
import ArticleCard from '@/components/ArticleCard';
import { ArrowRight, Users, BookOpen, TrendingUp, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

interface HomeStats {
  total_subscribers: number;
  total_topics: number;
  daily_articles: number;
  recent_articles: Array<{
    id: number;
    title: string;
    description: string;
    url: string;
    source: string;
    published_at?: string;
    topic_name?: string;
    category: string;
  }>;
}

const Home = () => {
  const [stats, setStats] = useState<HomeStats>({
    total_subscribers: 0,
    total_topics: 0,
    daily_articles: 0,
    recent_articles: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
          setStats(data.stats);
        } else {
          console.error('Failed to fetch stats:', data.error);
          // Fallback to basic stats if API fails
          setStats({
            total_subscribers: 0,
            total_topics: 0,
            daily_articles: 0,
            recent_articles: []
          });
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
        // Fallback to basic stats if API fails
        setStats({
          total_subscribers: 0,
          total_topics: 0,
          daily_articles: 0,
          recent_articles: []
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <Navigation />
      
      {/* Hero Section */}
      <section className="relative px-4 pt-20 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-radial from-primary/10 via-transparent to-transparent" />
        <div className="relative max-w-6xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full bg-primary/10 border border-primary/20 animate-fade-in">
            <Sparkles className="w-4 h-4 text-primary" />
            <span className="text-sm font-medium text-primary">AI-Powered News Curation</span>
          </div>
          
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-foreground via-primary to-accent bg-clip-text text-transparent animate-slide-up">
            Stay Ahead with 
            <br />
            <span className="text-primary">AI News Daily</span>
          </h1>
          
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto animate-slide-up [animation-delay:0.2s]">
            Get personalized AI news delivered to your inbox every day. 
            Stay informed about the latest breakthroughs, research, and innovations in artificial intelligence.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up [animation-delay:0.4s]">
            <Button asChild size="lg" className="shadow-elegant hover:shadow-glow transition-all duration-300">
              <Link to="/subscribe">
                Start Your Daily AI News
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link to="/preview">
                Preview Sample Email
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="px-4 py-16 bg-card/50 backdrop-blur-sm">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatsCard
              icon={<Users className="w-6 h-6" />}
              title="Active Subscribers"
              value={loading ? "..." : stats.total_subscribers.toLocaleString()}
              description="Growing community of AI enthusiasts"
              color="blue"
            />
            <StatsCard
              icon={<BookOpen className="w-6 h-6" />}
              title="Topic Categories"
              value={loading ? "..." : stats.total_topics.toString()}
              description="Specialized AI domains covered"
              color="teal"
            />
            <StatsCard
              icon={<TrendingUp className="w-6 h-6" />}
              title="Daily Articles"
              value={loading ? "..." : stats.daily_articles.toString()}
              description="Curated stories delivered daily"
              color="green"
            />
          </div>
        </div>
      </section>

      {/* Recent Articles */}
      <section className="px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Latest AI News</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Here's a preview of the kind of high-quality, curated AI news you'll receive in your daily digest.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {stats.recent_articles.map((article, index) => (
              <ArticleCard
                key={article.id}
                title={article.title}
                description={article.description}
                url={article.url}
                source={article.source}
                published_at={article.published_at}
                category={article.category}
                className="animate-scale-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              />
            ))}
          </div>
          
          <div className="text-center">
            <Button variant="outline" asChild>
              <Link to="/subscribe">
                Get These Stories in Your Inbox
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 py-16 bg-gradient-to-r from-primary/5 to-accent/5">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose AI News Daily?</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-0 shadow-elegant hover:shadow-glow transition-all duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <CardTitle>AI-Powered Curation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Our AI algorithms analyze thousands of sources to bring you only the most relevant and important AI news.
                </p>
              </CardContent>
            </Card>
            
            <Card className="border-0 shadow-elegant hover:shadow-glow transition-all duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-accent" />
                </div>
                <CardTitle>Personalized Content</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Choose your topics of interest and receive content tailored to your preferences and expertise level.
                </p>
              </CardContent>
            </Card>
            
            <Card className="border-0 shadow-elegant hover:shadow-glow transition-all duration-300">
              <CardHeader>
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-green-500" />
                </div>
                <CardTitle>Stay Current</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Never miss important developments in AI. Get breaking news and research updates as they happen.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Transform Your AI Knowledge?</h2>
          <p className="text-muted-foreground mb-8 text-lg">
            Join thousands of professionals staying ahead in the AI revolution.
          </p>
          <Button asChild size="lg" className="shadow-elegant hover:shadow-glow">
            <Link to="/subscribe">
              Start Your Free Subscription
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Home;