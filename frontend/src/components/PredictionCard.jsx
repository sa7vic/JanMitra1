import { motion } from 'framer-motion';
import { AlertTriangle, MapPin, Calendar, TrendingUp, Users, DollarSign } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PredictionCard = ({ prediction, index = 0, showActions = false }) => {
  const navigate = useNavigate();

  const severityConfig = {
    high: {
      bg: 'bg-red-50',
      border: 'border-red-300',
      text: 'text-red-900',
      badge: 'bg-red-600',
      icon: 'text-red-600'
    },
    medium: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-300',
      text: 'text-yellow-900',
      badge: 'bg-yellow-600',
      icon: 'text-yellow-600'
    },
    low: {
      bg: 'bg-blue-50',
      border: 'border-blue-300',
      text: 'text-blue-900',
      badge: 'bg-blue-600',
      icon: 'text-blue-600'
    }
  };

  const config = severityConfig[prediction.severity] || severityConfig.low;

  const daysUntil = prediction.predicted_date 
    ? Math.ceil((new Date(prediction.predicted_date) - new Date()) / (1000 * 60 * 60 * 24))
    : null;

  const handleClick = () => {
    if (showActions) {
      navigate(`/government/prediction/${prediction.id}`);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ y: -4 }}
      onClick={handleClick}
      className={`${config.bg} border-2 ${config.border} rounded-xl p-6 hover:shadow-xl transition-all duration-300 ${showActions ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-12 h-12 bg-white rounded-lg flex items-center justify-center`}>
            <AlertTriangle className={`w-6 h-6 ${config.icon}`} />
          </div>
          <div>
            <span className={`px-3 py-1 ${config.badge} text-white rounded-full text-xs font-bold uppercase`}>
              {prediction.severity}
            </span>
          </div>
        </div>
        
        <div className="text-right">
          <div className={`text-2xl font-bold ${config.text}`}>
            {Math.round(prediction.confidence * 100)}%
          </div>
          <div className="text-xs text-gray-600">Confidence</div>
        </div>
      </div>

      <h3 className={`text-xl font-bold ${config.text} mb-3`}>
        {prediction.title}
      </h3>

      <p className="text-gray-700 mb-4 line-clamp-3 leading-relaxed">
        {prediction.description}
      </p>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <MapPin className="w-4 h-4 flex-shrink-0" />
          <span className="font-medium truncate">{prediction.location}</span>
        </div>

        {daysUntil !== null && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Calendar className="w-4 h-4 flex-shrink-0" />
            <span className="font-medium">
              {daysUntil > 0 ? `${daysUntil} days` : 'Imminent'}
            </span>
          </div>
        )}

        {prediction.affected_population && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Users className="w-4 h-4 flex-shrink-0" />
            <span className="font-medium">{prediction.affected_population.toLocaleString()}</span>
          </div>
        )}

        {prediction.economic_impact && (
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <DollarSign className="w-4 h-4 flex-shrink-0" />
            <span className="font-medium">₹{prediction.economic_impact.toFixed(0)}Cr</span>
          </div>
        )}
      </div>

      {prediction.category && (
        <div className="pt-3 border-t border-gray-300">
          <span className="inline-flex items-center space-x-1 text-xs font-semibold text-gray-600 bg-white px-2 py-1 rounded-full">
            <TrendingUp className="w-3 h-3" />
            <span className="capitalize">{prediction.category}</span>
          </span>
        </div>
      )}
    </motion.div>
  );
};

export default PredictionCard;