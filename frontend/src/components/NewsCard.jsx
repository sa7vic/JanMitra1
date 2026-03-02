import { motion } from 'framer-motion';
import { ExternalLink, Calendar, Tag } from 'lucide-react';

const NewsCard = ({ article, index = 0 }) => {
  const getCategoryColor = (category) => {
    const colors = {
      politics: 'bg-blue-100 text-blue-700',
      economy: 'bg-green-100 text-green-700',
      health: 'bg-red-100 text-red-700',
      technology: 'bg-purple-100 text-purple-700',
      agriculture: 'bg-yellow-100 text-yellow-700',
      environment: 'bg-teal-100 text-teal-700',
      default: 'bg-gray-100 text-gray-700'
    };
    return colors[category] || colors.default;
  };

  const getSentimentColor = (sentiment) => {
    if (sentiment > 0.3) return 'text-green-600';
    if (sentiment < -0.3) return 'text-red-600';
    return 'text-gray-600';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -8 }}
      className="bg-white rounded-xl shadow-lg border-2 border-gray-200 overflow-hidden hover:shadow-2xl transition-all duration-300 group"
    >
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          {article.category && (
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${getCategoryColor(article.category)}`}>
              {article.category}
            </span>
          )}
          
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Calendar className="w-4 h-4" />
            <span>{formatDate(article.published_at || article.created_at)}</span>
          </div>
        </div>

        <h3 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 group-hover:text-primary-600 transition">
          {article.title}
        </h3>

        <p className="text-gray-600 text-sm mb-4 line-clamp-3 leading-relaxed">
          {article.content}
        </p>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div className="flex items-center space-x-4">
            {article.source && (
              <span className="text-xs text-gray-500 font-medium">
                {article.source}
              </span>
            )}
            
            {article.sentiment !== undefined && (
              <span className={`text-xs font-semibold ${getSentimentColor(article.sentiment)}`}>
                {article.sentiment > 0.3 ? '😊 Positive' : 
                 article.sentiment < -0.3 ? '😟 Negative' : 
                 '😐 Neutral'}
              </span>
            )}
          </div>

          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 text-sm font-semibold"
            >
              <span>Read more</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default NewsCard;