import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  AlertTriangle, MapPin, Calendar, Filter, 
  Loader2, ChevronRight, TrendingUp 
} from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

const AllPredictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ severity: 'all', category: 'all' });
  const navigate = useNavigate();

  useEffect(() => {
    fetchPredictions();
  }, []);

  const fetchPredictions = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/predictions?status=active`);
      setPredictions(response.data.predictions);
    } catch (error) {
      console.error('Failed to fetch predictions:', error);
    } finally {
      setLoading(false);
    }
  };

  const severityConfig = {
    high: { 
      color: 'text-red-600', 
      bg: 'bg-red-50', 
      border: 'border-red-300',
      badge: 'bg-red-600'
    },
    medium: { 
      color: 'text-yellow-600', 
      bg: 'bg-yellow-50', 
      border: 'border-yellow-300',
      badge: 'bg-yellow-600'
    },
    low: { 
      color: 'text-blue-600', 
      bg: 'bg-blue-50', 
      border: 'border-blue-300',
      badge: 'bg-blue-600'
    }
  };

  const categories = [...new Set(predictions.map(p => p.category))];
  
  const filteredPredictions = predictions.filter(p => {
    if (filter.severity !== 'all' && p.severity !== filter.severity) return false;
    if (filter.category !== 'all' && p.category !== filter.category) return false;
    return true;
  });

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-red-600 to-orange-600 rounded-2xl p-8 text-white shadow-2xl">
            <h1 className="text-4xl font-bold mb-2 flex items-center space-x-3">
              <AlertTriangle className="w-10 h-10" />
              <span>Active Crisis Predictions</span>
            </h1>
            <p className="text-white/90 text-lg">AI-powered early warning system for national crises</p>
          </div>
        </motion.div>

        <div className="mb-6 bg-white rounded-xl p-4 shadow-lg border-2 border-gray-200">
          <div className="flex items-center space-x-2 mb-2">
            <Filter className="w-5 h-5 text-gray-600" />
            <span className="font-semibold text-gray-900">Filters</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Severity</label>
              <select
                value={filter.severity}
                onChange={(e) => setFilter({...filter, severity: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Severities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={filter.category}
                onChange={(e) => setFilter({...filter, category: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            Showing {filteredPredictions.length} of {predictions.length} predictions
          </div>
        </div>

        {filteredPredictions.length > 0 ? (
          <div className="space-y-4">
            {filteredPredictions.map((prediction, index) => {
              const config = severityConfig[prediction.severity] || severityConfig.low;
              const daysUntil = prediction.predicted_date 
                ? Math.ceil((new Date(prediction.predicted_date) - new Date()) / (1000 * 60 * 60 * 24))
                : 0;

              return (
                <motion.div
                  key={prediction.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`${config.bg} border-2 ${config.border} rounded-xl p-6 hover:shadow-xl transition cursor-pointer`}
                  onClick={() => navigate(`/government/prediction/${prediction.id}`)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        <span className={`px-4 py-1 ${config.badge} text-white rounded-full text-sm font-bold uppercase`}>
                          {prediction.severity}
                        </span>
                        <span className="px-3 py-1 bg-white/50 rounded-full text-sm font-bold text-gray-900">
                          {Math.round(prediction.confidence * 100)}% Confidence
                        </span>
                        {prediction.category && (
                          <span className="px-3 py-1 bg-gray-200 rounded-full text-sm font-semibold text-gray-700 capitalize">
                            {prediction.category}
                          </span>
                        )}
                      </div>

                      <h3 className={`text-2xl font-bold ${config.color} mb-3`}>
                        {prediction.title}
                      </h3>

                      <p className="text-gray-700 mb-4 leading-relaxed">
                        {prediction.description}
                      </p>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <MapPin className="w-4 h-4" />
                          <span className="font-medium">{prediction.location}</span>
                        </div>

                        {daysUntil > 0 && (
                          <div className="flex items-center space-x-2 text-sm text-gray-600">
                            <Calendar className="w-4 h-4" />
                            <span className="font-medium">{daysUntil} days</span>
                          </div>
                        )}

                        {prediction.affected_population && (
                          <div className="text-sm text-gray-600">
                            <span className="font-bold">{prediction.affected_population.toLocaleString()}</span> affected
                          </div>
                        )}

                        {prediction.economic_impact && (
                          <div className="text-sm text-gray-600">
                            <span className="font-bold">₹{prediction.economic_impact.toFixed(0)}Cr</span> impact
                          </div>
                        )}
                      </div>
                    </div>

                    <ChevronRight className={`w-8 h-8 ${config.color} flex-shrink-0 ml-4`} />
                  </div>
                </motion.div>
              );
            })}
          </div>
        ) : (
          <div className="bg-white rounded-xl p-12 text-center border-2 border-gray-200">
            <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Predictions Found</h3>
            <p className="text-gray-600">Try adjusting your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AllPredictions;