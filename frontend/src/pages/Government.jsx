import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  AlertTriangle, TrendingUp, Users, FileText, 
  MapPin, Activity, Loader2, ChevronRight, Shield 
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import IndiaMap from '../components/IndiaMap';

const Government = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, predictionsRes, reportsRes] = await Promise.all([
        axios.get('http://localhost:5000/api/stats'),
        axios.get('http://localhost:5000/api/predictions?status=active'),
        axios.get('http://localhost:5000/api/reports?verified=true&time_range=24')
      ]);

      setStats(statsRes.data);
      setPredictions(predictionsRes.data.predictions);
      setRecentReports(reportsRes.data.reports);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
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

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
      </div>
    );
  }

  const statCards = [
    {
      icon: AlertTriangle,
      label: 'Active Predictions',
      value: predictions.length,
      change: '+3 this week',
      color: 'text-red-600',
      bg: 'bg-red-50'
    },
    {
      icon: Users,
      label: 'Citizen Reports (24h)',
      value: recentReports.length,
      change: '+12% vs yesterday',
      color: 'text-blue-600',
      bg: 'bg-blue-50'
    },
    {
      icon: FileText,
      label: 'Total Articles',
      value: stats?.articles || 0,
      change: 'Updated hourly',
      color: 'text-green-600',
      bg: 'bg-green-50'
    },
    {
      icon: Activity,
      label: 'System Health',
      value: '98%',
      change: 'All systems operational',
      color: 'text-purple-600',
      bg: 'bg-purple-50'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-primary-600 to-orange-600 rounded-2xl p-8 text-white shadow-2xl">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <Shield className="w-10 h-10" />
                  <h1 className="text-4xl font-bold">JanMitra Intelligence</h1>
                </div>
                <p className="text-white/90 text-lg">National Crisis Command Center</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-white/80 mb-1">Last Updated</div>
                <div className="text-xl font-bold">{new Date().toLocaleTimeString()}</div>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl p-6 shadow-lg border-2 border-gray-200 hover:shadow-xl transition"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 ${stat.bg} rounded-lg flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                  </div>
                </div>
                <div className="text-sm font-medium text-gray-900 mb-1">{stat.label}</div>
                <div className="text-xs text-gray-600">{stat.change}</div>
              </motion.div>
            );
          })}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.35 }}
          className="mb-8"
        >
          <div className="bg-white rounded-xl shadow-lg border-2 border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-green-600 to-teal-600 p-6">
              <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
                <MapPin className="w-6 h-6" />
                <span>🗺️ Live Threat Map</span>
              </h2>
              <p className="text-white/90 text-sm mt-1">Real-time visualization of active predictions across India</p>
            </div>
            <div className="p-6">
              <IndiaMap predictions={predictions} />
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-white rounded-xl shadow-lg border-2 border-gray-200 overflow-hidden"
            >
              <div className="bg-gradient-to-r from-red-600 to-orange-600 p-6">
                <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
                  <AlertTriangle className="w-6 h-6" />
                  <span>Active Crisis Predictions</span>
                </h2>
              </div>

              <div className="p-6">
                {predictions.length > 0 ? (
                  <div className="space-y-4">
                    {predictions.slice(0, 5).map((prediction, index) => {
                      const config = severityConfig[prediction.severity] || severityConfig.low;
                      return (
                        <motion.div
                          key={prediction.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className={`${config.bg} border-2 ${config.border} rounded-xl p-5 hover:shadow-lg transition cursor-pointer`}
                          onClick={() => navigate(`/government/prediction/${prediction.id}`)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3 mb-2">
                                <span className={`px-3 py-1 ${config.badge} text-white rounded-full text-xs font-bold uppercase`}>
                                  {prediction.severity}
                                </span>
                                <span className="text-sm text-gray-600">
                                  {Math.round(prediction.confidence * 100)}% Confidence
                                </span>
                              </div>
                              <h3 className={`text-lg font-bold ${config.color} mb-2`}>
                                {prediction.title}
                              </h3>
                              <p className="text-gray-700 text-sm mb-3 line-clamp-2">
                                {prediction.description}
                              </p>
                              <div className="flex items-center space-x-4 text-sm text-gray-600">
                                <div className="flex items-center space-x-1">
                                  <MapPin className="w-4 h-4" />
                                  <span>{prediction.location}</span>
                                </div>
                                {prediction.predicted_date && (
                                  <div>
                                    Expected: {new Date(prediction.predicted_date).toLocaleDateString()}
                                  </div>
                                )}
                              </div>
                            </div>
                            <ChevronRight className={`w-6 h-6 ${config.color} flex-shrink-0`} />
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <AlertTriangle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">No active predictions at this time</p>
                  </div>
                )}
              </div>
            </motion.div>
          </div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="bg-white rounded-xl shadow-lg border-2 border-gray-200 overflow-hidden"
            >
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6">
                <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>Citizen Intel (24h)</span>
                </h2>
              </div>

              <div className="p-6">
                {recentReports.length > 0 ? (
                  <div className="space-y-3">
                    {recentReports.slice(0, 8).map((report, index) => (
                      <motion.div
                        key={report.id}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="font-semibold text-gray-900 text-sm mb-1">
                              {report.title || report.report_type}
                            </div>
                            <div className="text-xs text-gray-600 flex items-center space-x-2">
                              <MapPin className="w-3 h-3" />
                              <span>{report.city}</span>
                              <span>•</span>
                              <span>{new Date(report.created_at).toLocaleTimeString()}</span>
                            </div>
                          </div>
                          {report.verified && (
                            <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0 mt-1.5"></div>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-600">No recent reports</p>
                  </div>
                )}

                <button 
                  onClick={() => navigate('/government/reports')}
                  className="w-full mt-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:border-gray-400 transition text-sm"
                >
                  View All Reports
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="bg-gradient-to-br from-primary-600 to-orange-600 rounded-xl p-6 text-white shadow-lg"
            >
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button 
                  onClick={() => navigate('/government/predictions')}
                  className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg font-semibold transition text-left px-4"
                >
                  View All Predictions
                </button>
                <button 
                  onClick={() => navigate('/government/reports')}
                  className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg font-semibold transition text-left px-4"
                >
                  Citizen Reports Dashboard
                </button>
                <button 
                  onClick={() => navigate('/government/analytics')}
                  className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg font-semibold transition text-left px-4"
                >
                  Analytics & Insights
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Government;