import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  MessageSquare, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  Zap, 
  Brain, 
  Smartphone, 
  Link as LinkIcon,
  TestTube,
  CheckCircle,
  AlertCircle 
} from 'lucide-react';

interface SlackIntegrationProps {
  userEmail: string;
  onIntegrationComplete?: () => void;
}

const SlackIntegration = ({ userEmail, onIntegrationComplete }: SlackIntegrationProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  
  const [slackForm, setSlackForm] = useState({
    channelName: '',
    webhookUrl: ''
  });

  const handleSlackSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!slackForm.webhookUrl) {
      setStatus('error');
      setMessage('Please provide a Slack webhook URL');
      return;
    }

    if (!slackForm.webhookUrl.includes('hooks.slack.com')) {
      setStatus('error');
      setMessage('Please provide a valid Slack webhook URL');
      return;
    }

    setIsSubmitting(true);
    setStatus('idle');
    
    try {
      // Test the webhook first
      const testResponse = await fetch('/api/slack/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          webhook_url: slackForm.webhookUrl,
          channel_name: slackForm.channelName || '#ai-news'
        }),
      });

      if (!testResponse.ok) {
        throw new Error('Failed to test Slack webhook');
      }

      // If test passes, save the integration
      const response = await fetch('/api/notifications/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail,
          channel_type: 'slack',
          webhook_url: slackForm.webhookUrl,
          channel_name: slackForm.channelName || '#ai-news',
          enabled: true
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save Slack integration');
      }

      setStatus('success');
      setMessage('🎉 Slack integration added successfully! You\'ll receive a test message shortly.');
      
      // Reset form
      setSlackForm({ channelName: '', webhookUrl: '' });
      
      // Call completion callback
      if (onIntegrationComplete) {
        onIntegrationComplete();
      }
      
    } catch (error) {
      setStatus('error');
      setMessage('Failed to set up Slack integration. Please check your webhook URL and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setSlackForm(prev => ({ ...prev, [field]: value }));
    // Clear status when user starts typing
    if (status !== 'idle') {
      setStatus('idle');
      setMessage('');
    }
  };

  return (
    <Card className="shadow-elegant border-primary/20">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
            <MessageSquare className="w-4 h-4 text-white" />
          </div>
          <div>
            <CardTitle className="text-xl">📫 Want AI News in Slack Too?</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Get your daily AI updates delivered directly to your Slack channels with rich formatting!
            </p>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Benefits Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 rounded-lg bg-primary/5 border border-primary/10">
            <Brain className="w-6 h-6 mx-auto mb-2 text-primary" />
            <p className="text-xs font-medium">AI Summaries</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-primary/5 border border-primary/10">
            <Zap className="w-6 h-6 mx-auto mb-2 text-primary" />
            <p className="text-xs font-medium">Instant Delivery</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-primary/5 border border-primary/10">
            <Smartphone className="w-6 h-6 mx-auto mb-2 text-primary" />
            <p className="text-xs font-medium">Rich Formatting</p>
          </div>
          <div className="text-center p-3 rounded-lg bg-primary/5 border border-primary/10">
            <LinkIcon className="w-6 h-6 mx-auto mb-2 text-primary" />
            <p className="text-xs font-medium">One-Click Reading</p>
          </div>
        </div>

        {/* Toggle Setup */}
        <div className="text-center">
          <Collapsible open={isOpen} onOpenChange={setIsOpen}>
            <CollapsibleTrigger asChild>
              <Button 
                variant="outline" 
                size="lg" 
                className="shadow-sm border-primary/20 hover:bg-primary/5"
              >
                📫 Add Slack Integration
                {isOpen ? (
                  <ChevronUp className="w-4 h-4 ml-2" />
                ) : (
                  <ChevronDown className="w-4 h-4 ml-2" />
                )}
              </Button>
            </CollapsibleTrigger>
            <p className="text-sm text-muted-foreground mt-2">⏱️ Takes only 2 minutes!</p>

            <CollapsibleContent className="mt-6">
              <div className="space-y-6">
                {/* Setup Steps */}
                <div className="space-y-4">
                  <h4 className="font-semibold text-lg">🚀 Quick Slack Setup</h4>
                  <p className="text-muted-foreground">Follow these simple steps to get AI news in your Slack:</p>
                  
                  {/* Step 1 */}
                  <div className="flex gap-4 p-4 rounded-lg bg-muted/30 border">
                    <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                      1
                    </div>
                    <div className="flex-1">
                      <h5 className="font-medium mb-2">Get Your Slack Webhook</h5>
                      <p className="text-sm text-muted-foreground mb-3">
                        Click the button below to create a webhook in your Slack workspace:
                      </p>
                      <Button variant="outline" asChild className="mb-2">
                        <a 
                          href="https://slack.com/apps/A0F7XDUAZ-incoming-webhooks" 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="flex items-center gap-2"
                        >
                          🔗 Create Slack Webhook
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </Button>
                      <p className="text-xs text-muted-foreground">
                        Choose the channel where you want AI news (e.g., #ai-news)
                      </p>
                    </div>
                  </div>

                  {/* Step 2 */}
                  <div className="flex gap-4 p-4 rounded-lg bg-muted/30 border">
                    <div className="w-8 h-8 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                      2
                    </div>
                    <div className="flex-1">
                      <h5 className="font-medium mb-4">Add Webhook to Your Account</h5>
                      
                      <form onSubmit={handleSlackSubmit} className="space-y-4">
                        <div>
                          <Label htmlFor="channelName">📍 Channel Name (optional):</Label>
                          <Input
                            id="channelName"
                            type="text"
                            placeholder="#ai-news"
                            value={slackForm.channelName}
                            onChange={(e) => handleInputChange('channelName', e.target.value)}
                            className="mt-1"
                          />
                        </div>
                        
                        <div>
                          <Label htmlFor="webhookUrl">🔗 Paste Your Webhook URL: *</Label>
                          <Input
                            id="webhookUrl"
                            type="url"
                            placeholder="https://hooks.slack.com/services/..."
                            value={slackForm.webhookUrl}
                            onChange={(e) => handleInputChange('webhookUrl', e.target.value)}
                            className="mt-1"
                            required
                          />
                          <p className="text-xs text-muted-foreground mt-1">
                            Paste the webhook URL from step 1
                          </p>
                        </div>

                        {status !== 'idle' && (
                          <Alert className={status === 'success' ? 'border-green-500/20 bg-green-500/10' : 'border-destructive/20 bg-destructive/10'}>
                            {status === 'success' ? (
                              <CheckCircle className="w-4 h-4 text-green-500" />
                            ) : (
                              <AlertCircle className="w-4 h-4 text-destructive" />
                            )}
                            <AlertDescription className={status === 'success' ? 'text-green-700' : 'text-destructive'}>
                              {message}
                            </AlertDescription>
                          </Alert>
                        )}
                        
                        <Button 
                          type="submit" 
                          className="w-full"
                          disabled={isSubmitting || !slackForm.webhookUrl}
                        >
                          {isSubmitting ? (
                            'Testing & Adding...'
                          ) : (
                            <>
                              <TestTube className="w-4 h-4 mr-2" />
                              🧪 Test & Add Slack
                            </>
                          )}
                        </Button>
                      </form>
                    </div>
                  </div>
                </div>

                {/* Slack Preview */}
                <div className="space-y-3">
                  <h5 className="font-medium">📱 Preview: How it looks in Slack</h5>
                  <div className="p-4 rounded-lg bg-gray-100 border border-gray-200 font-mono text-sm">
                    <div className="font-bold text-gray-800 mb-1">🤖 Daily AI News Update (2 articles)</div>
                    <div className="text-gray-600 text-xs mb-3">📅 Today • For: {userEmail}</div>
                    <div className="bg-white p-3 rounded border-l-4 border-blue-500 mb-2">
                      <div className="font-semibold">1. OpenAI Releases GPT-5 with Enhanced Reasoning</div>
                      <div className="text-gray-600 text-xs">OpenAI</div>
                      <div className="mt-1">
                        <span className="font-medium">🧠 AI Summary:</span> GPT-5 achieves 95% accuracy on complex reasoning tasks...
                      </div>
                    </div>
                    <Button variant="outline" size="sm" className="text-xs">
                      📖 Read Article
                    </Button>
                  </div>
                </div>
              </div>
            </CollapsibleContent>
          </Collapsible>
        </div>
      </CardContent>
    </Card>
  );
};

export default SlackIntegration;
