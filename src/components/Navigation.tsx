import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Menu, X, Mail, Sparkles } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 font-bold text-xl group">
            <div className="w-8 h-8 bg-gradient-to-r from-primary to-accent rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              AI News Daily
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link 
              to="/" 
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/') ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Home
            </Link>
            <Link 
              to="/subscribe" 
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/subscribe') ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Subscribe
            </Link>
            <Link 
              to="/preferences" 
              className={`text-sm font-medium transition-colors hover:text-primary ${
                isActive('/preferences') ? 'text-primary' : 'text-muted-foreground'
              }`}
            >
              Preferences
            </Link>
            <Button asChild size="sm" className="shadow-elegant">
              <Link to="/subscribe">
                <Mail className="w-4 h-4 mr-2" />
                Get Started
              </Link>
            </Button>
          </div>

          {/* Mobile Menu Button */}
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </Button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden bg-background/95 backdrop-blur-md border-t border-border animate-slide-up">
            <div className="px-4 py-6 space-y-4">
              <Link 
                to="/" 
                className={`block py-2 text-sm font-medium transition-colors ${
                  isActive('/') ? 'text-primary' : 'text-muted-foreground'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Home
              </Link>
              <Link 
                to="/subscribe" 
                className={`block py-2 text-sm font-medium transition-colors ${
                  isActive('/subscribe') ? 'text-primary' : 'text-muted-foreground'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Subscribe
              </Link>
              <Link 
                to="/preferences" 
                className={`block py-2 text-sm font-medium transition-colors ${
                  isActive('/preferences') ? 'text-primary' : 'text-muted-foreground'
                }`}
                onClick={() => setIsOpen(false)}
              >
                Preferences
              </Link>
              <Button asChild className="w-full mt-4">
                <Link to="/subscribe" onClick={() => setIsOpen(false)}>
                  <Mail className="w-4 h-4 mr-2" />
                  Get Started
                </Link>
              </Button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;