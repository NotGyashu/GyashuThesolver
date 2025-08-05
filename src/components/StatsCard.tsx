import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface StatsCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  description: string;
  color?: 'blue' | 'teal' | 'green' | 'purple';
  trend?: string;
  className?: string;
}

const StatsCard = ({ 
  icon, 
  title, 
  value, 
  description, 
  color = 'blue', 
  trend, 
  className 
}: StatsCardProps) => {
  const colorVariants = {
    blue: 'bg-primary/10 text-primary border-primary/20',
    teal: 'bg-accent/10 text-accent border-accent/20',
    green: 'bg-green-500/10 text-green-500 border-green-500/20',
    purple: 'bg-purple-500/10 text-purple-500 border-purple-500/20'
  };

  return (
    <Card className={cn('shadow-elegant hover:shadow-glow transition-all duration-300', className)}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className={cn(
              'w-12 h-12 rounded-lg flex items-center justify-center mb-4 border',
              colorVariants[color]
            )}>
              {icon}
            </div>
            <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
            <h3 className="text-2xl font-bold mb-2">{value}</h3>
            <p className="text-sm text-muted-foreground">{description}</p>
          </div>
          {trend && (
            <div className="text-right">
              <span className="text-xs text-green-500 font-medium">{trend}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default StatsCard;