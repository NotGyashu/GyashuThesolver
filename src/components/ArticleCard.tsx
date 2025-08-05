import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Clock, User } from 'lucide-react';

interface ArticleCardProps {
  title: string;
  description: string;
  url: string;
  source: string;
  published_at?: string;
  category?: string;
  className?: string;
}

const ArticleCard = ({ 
  title, 
  description, 
  url, 
  source, 
  published_at, 
  category,
  className 
}: ArticleCardProps) => {
  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card className={`hover:shadow-md transition-shadow ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <CardTitle className="text-lg leading-tight line-clamp-2">
            {title}
          </CardTitle>
          {category && (
            <Badge variant="outline" className="text-xs">
              {category}
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <p className="text-muted-foreground text-sm leading-relaxed line-clamp-3">
          {description}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <User className="w-3 h-3" />
              {source}
            </div>
            {published_at && (
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatDate(published_at)}
              </div>
            )}
          </div>
          
          <Button 
            variant="ghost" 
            size="sm" 
            asChild
            className="text-primary hover:text-primary/80"
          >
            <a 
              href={url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-1"
            >
              Read more
              <ExternalLink className="w-3 h-3" />
            </a>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ArticleCard;
