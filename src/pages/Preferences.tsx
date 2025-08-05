import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import Navigation from '@/components/Navigation';
import SlackIntegration from '@/components/SlackIntegration';
import { Settings, Clock, Globe, Mail, CheckCircle, AlertCircle } from 'lucide-react';
import { useParams, useSearchParams } from 'react-router-dom';

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

const timezones = [
  'Asia/Kolkata', 'America/New_York', 'Europe/London', 
  'America/Los_Angeles', 'Europe/Berlin', 'Asia/Tokyo',
  'Australia/Sydney', 'America/Toronto', 'Asia/Shanghai'
];

const Preferences = () => {
  const { email: emailParam } = useParams();
  const [searchParams] = useSearchParams();
  const emailFromQuery = searchParams.get('email');
  
  const [email, setEmail] = useState(emailParam || emailFromQuery || '');
  const [showForm, setShowForm] = useState(!!emailParam || !!emailFromQuery);
  const [showSlackIntegration, setShowSlackIntegration] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  
  const [preferences, setPreferences] = useState({
    preferredTime: '10:00',
    timezone: 'Asia/Kolkata',
    frequency: 'daily',
    maxArticles: 5,
    selectedTopics: [] as number[],
    topicPriorities: {} as Record<number, number>
  });

  useEffect(() => {
    if (email) {
      // In real app, fetch user preferences
      // fetchUserPreferences(email);
    }
  }, [email]);

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setStatus('error');
      setMessage('Please enter a valid email address.');
      return;
    }
    
    setShowForm(true);
    setStatus('idle');
  };

  const handleTopicChange = (topicId: number, checked: boolean) => {
    if (checked) {
      setPreferences(prev => ({
        ...prev,
        selectedTopics: [...prev.selectedTopics, topicId],
        topicPriorities: { ...prev.topicPriorities, [topicId]: 1 }
      }));
    } else {
      setPreferences(prev => ({
        ...prev,
        selectedTopics: prev.selectedTopics.filter(id => id !== topicId),
        topicPriorities: { ...prev.topicPriorities, [topicId]: undefined }
      }));
    }
  };

  const handlePriorityChange = (topicId: number, priority: number) => {
    setPreferences(prev => ({
      ...prev,
      topicPriorities: { ...prev.topicPriorities, [topicId]: priority }
    }));
  };

  const handlePreferencesSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (preferences.selectedTopics.length === 0) {
      setStatus('error');
      setMessage('Please select at least one topic.');
      return;
    }
    
    setLoading(true);
    
    try {
      // In real app, submit to Flask API
      // const response = await fetch('/update-preferences', { method: 'POST', ... });
      
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setStatus('success');
      setMessage('Preferences updated successfully! 🎉');
      setShowSlackIntegration(true);
      
    } catch (error) {
      setStatus('error');
      setMessage('An error occurred while updating preferences.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <Navigation />
      
      <div className="px-4 pt-20 pb-16">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-foreground to-primary bg-clip-text text-transparent">
              Customize Your Preferences
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Personalize your AI news experience to get exactly what you want, when you want it.
            </p>
          </div>

          {!showForm ? (
            <Card className="max-w-md mx-auto shadow-elegant">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="w-5 h-5 text-primary" />
                  Find Your Account
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleEmailSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email address"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="mt-1"
                    />
                  </div>
                  
                  {status === 'error' && (
                    <Alert className="border-destructive/20 bg-destructive/10">
                      <AlertCircle className="w-4 h-4 text-destructive" />
                      <AlertDescription className="text-destructive">
                        {message}
                      </AlertDescription>
                    </Alert>
                  )}
                  
                  <Button type="submit" className="w-full">
                    Continue
                  </Button>
                </form>
              </CardContent>
            </Card>
          ) : (
            <form onSubmit={handlePreferencesSubmit} className="space-y-8">
              {/* Email Display */}
              <Card className="shadow-elegant">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Mail className="w-5 h-5 text-primary" />
                    Account: {email}
                  </CardTitle>
                </CardHeader>
              </Card>

              {/* Delivery Settings */}
              <Card className="shadow-elegant">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="w-5 h-5 text-primary" />
                    Delivery Settings
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <Label htmlFor="preferredTime">Preferred Time</Label>
                      <Input
                        id="preferredTime"
                        type="time"
                        value={preferences.preferredTime}
                        onChange={(e) => setPreferences(prev => ({ ...prev, preferredTime: e.target.value }))}
                        className="mt-1"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="timezone">Timezone</Label>
                      <Select value={preferences.timezone} onValueChange={(value) => setPreferences(prev => ({ ...prev, timezone: value }))}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select timezone" />
                        </SelectTrigger>
                        <SelectContent>
                          {timezones.map((tz) => (
                            <SelectItem key={tz} value={tz}>{tz}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="frequency">Frequency</Label>
                      <Select value={preferences.frequency} onValueChange={(value) => setPreferences(prev => ({ ...prev, frequency: value }))}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select frequency" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="daily">Daily</SelectItem>
                          <SelectItem value="weekly">Weekly</SelectItem>
                          <SelectItem value="monthly">Monthly</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="maxArticles">Max Articles per Email</Label>
                      <Select value={preferences.maxArticles.toString()} onValueChange={(value) => setPreferences(prev => ({ ...prev, maxArticles: parseInt(value) }))}>
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select number" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="3">3 articles</SelectItem>
                          <SelectItem value="5">5 articles</SelectItem>
                          <SelectItem value="10">10 articles</SelectItem>
                          <SelectItem value="15">15 articles</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Topic Preferences */}
              <Card className="shadow-elegant">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="w-5 h-5 text-primary" />
                    Topic Preferences
                  </CardTitle>
                  <p className="text-sm text-muted-foreground">
                    Select the topics you're interested in and set their priority (1=High, 2=Medium, 3=Low)
                  </p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 gap-4">
                    {topics.map((topic) => (
                      <div key={topic.id} className="flex items-center gap-4 p-4 rounded-lg border hover:bg-accent/5 transition-colors">
                        <Checkbox
                          id={`topic-${topic.id}`}
                          checked={preferences.selectedTopics.includes(topic.id)}
                          onCheckedChange={(checked) => handleTopicChange(topic.id, checked as boolean)}
                        />
                        
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-lg">{topic.icon}</span>
                            <Label htmlFor={`topic-${topic.id}`} className="font-medium cursor-pointer">
                              {topic.name}
                            </Label>
                            <Badge variant="outline" className="text-xs">
                              AI
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{topic.description}</p>
                        </div>
                        
                        {preferences.selectedTopics.includes(topic.id) && (
                          <Select 
                            value={preferences.topicPriorities[topic.id]?.toString() || '1'} 
                            onValueChange={(value) => handlePriorityChange(topic.id, parseInt(value))}
                          >
                            <SelectTrigger className="w-24">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="1">High</SelectItem>
                              <SelectItem value="2">Medium</SelectItem>
                              <SelectItem value="3">Low</SelectItem>
                            </SelectContent>
                          </Select>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Status Alert */}
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

              {/* Slack Integration - Show after successful preferences save */}
              {showSlackIntegration && status === 'success' && (
                <SlackIntegration 
                  userEmail={email} 
                  onIntegrationComplete={() => {
                    // Optional: Handle completion
                    console.log('Slack integration completed');
                  }}
                />
              )}

              {/* Submit Button */}
              <div className="flex gap-4">
                <Button 
                  type="submit" 
                  className="flex-1 h-12" 
                  disabled={loading || preferences.selectedTopics.length === 0}
                >
                  {loading ? 'Saving Preferences...' : 'Save Preferences'}
                </Button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default Preferences;