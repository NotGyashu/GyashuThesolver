 from 'react-router-dom';

const topics = [
  { id: 1, name: 'Machine Learning', icon: '🧠', description: 'ML algorithms, neural networks, and model developments' },
  { id: 2, name: 'Natural Language Processing', icon: '💬', description: 'Language models, chatbots, and text analysis' },
  { id: 3, name: 'Computer Vision', icon: '👁️', description: 'Image recognition, object detection, and visual AI' },
  { id: 4, name: 'AI Ethics & Safety', icon: '⚖️', description: 'Responsible AI, bias prevention, and safety measures' },
  { id: 5, name: 'AI Tools & Frameworks', icon: '🛠️', description: 'New AI tools, platforms, and development frameworks' },
  { id: 6, name: 'AI Startups & Business', icon: '🚀', description: 'AI startup news, funding, and business applications' },
  { id: 7, name: 'Robotics & Automation', icon: '🤖', description: 'Robotics advances and automation technologies' },
  { id: 8, name: 'AI Research & Papers', icon: '📚', description: 'Latest research publications and scientific breakthroughs' }
];

const Subscribe = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email) {
      setStatus('error');
      setMessage('Please enter an email address.');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setStatus('error');
      setMessage('Please enter a valid email address.');
      return;
    }

    setLoading(true);
    
    try {
      // In a real app, this would call your Flask API
      // const response = await fetch('/subscribe', { method: 'POST', ... });
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setStatus('success');
      setMessage('Successfully subscribed! Redirecting to preferences...');
      
      // Simulate redirect to preferences
      setTimeout(() => {
        // In real app: window.location.href = `/preferences/${email}`;
        console.log(`Would redirect to preferences for ${email}`);
      }, 2000);
      
    } catch (error) {
      setStatus('error');
      setMessage('An error occurred. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <Navigation />
      
      <div className="px-4 pt-20 pb-16">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-full bg-primary/10 border border-primary/20">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-primary">Free Subscription</span>
            </div>
            
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
              Subscribe to AI News Daily
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Join our community of AI enthusiasts and get personalized news delivered to your inbox every day.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Subscription Form */}
            <div className="space-y-8">
              <Card className="shadow-elegant">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mail className="w-5 h-5 text-primary" />
                    Start Your Subscription
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                      <Input
                        type="email"
                        placeholder="Enter your email address"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="h-12"
                        disabled={loading}
                      />
                    </div>
                    
                    {status !== 'idle' && (
                      <Alert className={status === 'success' ? 'border-green-500/20 bg-green-500/10' : 'border-destructive/20 bg-destructive/10'}>
                        {status === 'success' ? 
                          <CheckCircle className="w-4 h-4 text-green-500" /> : 
                          <AlertCircle className="w-4 h-4 text-destructive" />
                        }
                        <AlertDescription className={status === 'success' ? 'text-green-700' : 'text-destructive'}>
                          {message}
                        </AlertDescription>
                      </Alert>
                    )}
                    
                    <Button 
                      type="submit" 
                      className="w-full h-12" 
                      disabled={loading}
                    >
                      {loading ? 'Subscribing...' : 'Subscribe Now'}
                    </Button>
                  </form>
                  
                  <div className="mt-4 text-sm text-muted-foreground">
                    Already subscribed?{' '}
                    <Link to="/preferences" className="text-primary hover:underline">
                      Update your preferences
                    </Link>
                  </div>
                </CardContent>
              </Card>

              {/* What You Get */}
              <Card className="shadow-elegant">
                <CardHeader>
                  <CardTitle>What You'll Get</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium">Daily AI News Digest</h4>
                      <p className="text-sm text-muted-foreground">Curated articles delivered to your inbox every morning</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium">Personalized Content</h4>
                      <p className="text-sm text-muted-foreground">Choose topics that matter to you</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium">Breaking News Alerts</h4>
                      <p className="text-sm text-muted-foreground">Get notified about major AI breakthroughs</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                    <div>
                      <h4 className="font-medium">Unsubscribe Anytime</h4>
                      <p className="text-sm text-muted-foreground">No commitment, cancel whenever you want</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Topic Categories */}
            <div>
              <h3 className="text-xl font-semibold mb-6">Choose Your Interests</h3>
              <p className="text-muted-foreground mb-6">
                Select the AI topics you're most interested in. You can customize these preferences after subscribing.
              </p>
              
              <div className="grid grid-cols-1 gap-3">
                {topics.map((topic) => (
                  <Card key={topic.id} className="hover:shadow-md transition-shadow cursor-default">
                    <CardContent className="p-4">
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">{topic.icon}</span>
                        <div className="flex-1">
                          <h4 className="font-medium text-sm">{topic.name}</h4>
                          <p className="text-xs text-muted-foreground mt-1">{topic.description}</p>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          Popular
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Subscribe;