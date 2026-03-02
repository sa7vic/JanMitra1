import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { AlertTriangle, CheckCircle, XCircle, Clock, Filter, Loader2 } from 'lucide-react';

const MyAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('unread');

  useEffect(() => {
    fetchAlerts();
  }, [filter]);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const includeRead = filter === 'all';
      const response = await axios.get(`http://localhost:5000/api/user/alerts?include_read=${includeRead}`);
      setAlerts(response.data.alerts);
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (alertId) => {
    try {
      await axios.post(`http://localhost:5000/api/user/alerts/${alertId}/read`);
      fetchAlerts();
    } catch (error) {
      console.error('Failed to mark alert as read:', error);
    }
  };

  const dismissAlert = async (alertId) => {
    try {
      await axios.post(`http://localhost:5000/api/user/alerts/${alertId}/dismiss`);
      fetchAlerts();
    } catch (error) {
      console.error('Failed to dismiss alert:', error);
    }
  };

  const markActionTaken = async (alertId) => {
    try {
      await axios.post(`http://localhost:5000/api/user/alerts/${alertId}/action-taken`);
      fetchAlerts();
    } catch (error) {
      console.error('Failed to mark action:', error);
    }
  };

  const severityConfig = {
    high: { 
      bg: 'bg-red-50', 
      border: 'border-red-300', 
      text: 'text-red-900', 
      icon: 'text-red-600',
      badge: 'bg-red-600'
    },
    medium: { 
      bg: 'bg-yellow-50', 
      border: 'border-yellow-300', 
      text: 'text-yellow-900', 
      icon: 'text-yellow-600',
      badge: 'bg-yellow-600'
    },
    low: { 
      bg: 'bg-blue-50', 
      border: 'border-blue-300', 
      text: 'text-blue-900', 
      icon: 'text-blue-600',
      badge: 'bg-blue-600'
    }
  };

  const alertTypeLabels = {
    location_based: 'Location Alert',
    occupation_based: 'Occupation Alert',
    health: 'Health Alert',
    economy: 'Economic Alert',
    weather: 'Weather Alert'
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">My Alerts</h1>
          <p className="text-gray-600">Stay informed about issues affecting you</p>
        </motion.div>

        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-2 bg-white rounded-lg p-1 border border-gray-200">
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
                filter === 'unread'
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Unread
            </button>
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition ${
                filter === 'all'
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              All Alerts
            </button>
          </div>

          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Filter className="w-4 h-4" />
            <span>{alerts.length} alerts</span>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
          </div>
        ) : alerts.length > 0 ? (
          <div className="space-y-4">
            {alerts.map((alert, index) => {
              const config = severityConfig[alert.severity] || severityConfig.low;
              return (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`${config.bg} border-2 ${config.border} rounded-xl p-6 ${
                    alert.read ? 'opacity-75' : ''
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <AlertTriangle className={`w-6 h-6 ${config.icon}`} />
                      <div>
                        <h3 className={`text-lg font-bold ${config.text}`}>
                          {alert.title}
                        </h3>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className={`text-xs px-2 py-1 rounded-full ${config.badge} text-white font-semibold uppercase`}>
                            {alert.severity}
                          </span>
                          <span className="text-xs text-gray-600">
                            {alertTypeLabels[alert.alert_type] || alert.alert_type}
                          </span>
                          <span className="text-xs text-gray-500">
                            • {new Date(alert.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {!alert.read && (
                      <button
                        onClick={() => markAsRead(alert.id)}
                        className="text-sm text-primary-600 hover:text-primary-700 font-medium"
                      >
                        Mark as read
                      </button>
                    )}
                  </div>

                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap mb-4">
                    {alert.message}
                  </p>

                  <div className="flex items-center space-x-3">
                    {alert.actionable && !alert.action_taken && (
                      <button
                        onClick={() => markActionTaken(alert.id)}
                        className={`flex items-center space-x-2 px-4 py-2 border-2 ${config.border} rounded-lg font-semibold ${config.text} hover:opacity-80 transition`}
                      >
                        <CheckCircle className="w-4 h-4" />
                        <span>Mark Action Taken</span>
                      </button>
                    )}
                    
                    {alert.action_taken && (
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Action taken</span>
                      </div>
                    )}

                    <button
                      onClick={() => dismissAlert(alert.id)}
                      className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-900 transition"
                    >
                      <XCircle className="w-4 h-4" />
                      <span className="text-sm font-medium">Dismiss</span>
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-white rounded-xl p-12 text-center border-2 border-gray-200"
          >
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">All Clear!</h3>
            <p className="text-gray-600">
              {filter === 'unread' 
                ? "You have no unread alerts. We'll notify you when something important comes up."
                : "No alerts yet. We'll keep you informed about issues in your area."
              }
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default MyAlerts;