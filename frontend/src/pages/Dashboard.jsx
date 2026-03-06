import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  AlertTriangle, TrendingUp, Award, MapPin, Bell, 
  Loader2, ArrowRight, CheckCircle, Clock, AlertCircle 
} from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    if (user && !user.profile_completed) {
      navigate('/onboarding');
      return;
    }
    fetchDashboard();
  }, [user]);

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user/dashboard`);
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleActionTaken = async (alertId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/user/alerts/${alertId}/action-taken`);
      fetchDashboard();
    } catch (error) {
      console.error('Failed to mark action:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Failed to load dashboard</p>
      </div>
    );
  }

  const { alerts, enrolled_schemes, eligible_schemes, trending_issues, local_prices, reputation_score, profile_completeness } = dashboardData;

  const severityConfig = {
    high: { bg: 'bg-red-50', border: 'border-red-300', text: 'text-red-900', icon: 'text-red-600' },
    medium: { bg: 'bg-yellow-50', border: 'border-yellow-300', text: 'text-yellow-900', icon: 'text-yellow-600' },
    low: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-900', icon: 'text-blue-600' }
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gradient-to-r from-primary-600 to-orange-600 rounded-2xl p-8 text-white shadow-xl"
          >
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-3xl font-bold mb-2">
                  Good {new Date().getHours() < 12 ? 'Morning' : new Date().getHours() < 18 ? 'Afternoon' : 'Evening'}, {user?.name || 'User'}!
                </h1>
                <div className="flex items-center space-x-4 text-white/90">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4" />
                    <span>{user?.city}, {user?.state}</span>
                  </div>
                  {user?.occupation && (
                    <div className="flex items-center space-x-2">
                      <span>•</span>
                      <span>{user.occupation}</span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-4xl font-bold mb-1">{reputation_score || 0}</div>
                <div className="text-sm text-white/80">Reputation Score</div>
              </div>
            </div>

            {profile_completeness < 100 && (
              <div className="mt-6 p-4 bg-white/10 rounded-lg backdrop-blur">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Profile Completeness</span>
                  <span className="text-sm font-bold">{profile_completeness}%</span>
                </div>
                <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-white rounded-full transition-all duration-500"
                    style={{ width: `${profile_completeness}%` }}
                  />
                </div>
              </div>
            )}
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
                  <Bell className="w-6 h-6 text-primary-600" />
                  <span>Alerts for You</span>
                </h2>
                {alerts && alerts.length > 0 && (
                  <span className="px-3 py-1 bg-red-100 text-red-600 rounded-full text-sm font-semibold">
                    {alerts.length} Active
                  </span>
                )}
              </div>

              {alerts && alerts.length > 0 ? (
                <div className="space-y-4">
                  {alerts.map((alert, index) => {
                    const config = severityConfig[alert.severity] || severityConfig.low;
                    return (
                      <motion.div
                        key={alert.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className={`${config.bg} border-2 ${config.border} rounded-xl p-6 hover:shadow-lg transition`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <AlertTriangle className={`w-6 h-6 ${config.icon}`} />
                              <h3 className={`text-lg font-bold ${config.text}`}>
                                {alert.title}
                              </h3>
                            </div>
                            <p className="text-gray-700 mb-4 leading-relaxed whitespace-pre-wrap">
                              {alert.message}
                            </p>
                            <div className="flex items-center space-x-3">
                              {alert.actionable && !alert.action_taken && (
                                <button 
                                  onClick={() => handleActionTaken(alert.id)}
                                  className={`flex items-center space-x-2 px-4 py-2 ${config.border} border-2 rounded-lg font-semibold ${config.text} hover:opacity-80 transition`}
                                >
                                  <span>Take Action</span>
                                  <ArrowRight className="w-4 h-4" />
                                </button>
                              )}
                              {alert.action_taken && (
                                <div className="flex items-center space-x-2 text-green-600">
                                  <CheckCircle className="w-4 h-4" />
                                  <span className="text-sm font-medium">Action taken ✓</span>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              ) : (
                <div className="bg-white rounded-xl p-12 text-center border-2 border-gray-200">
                  <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                  <h3 className="text-xl font-bold text-gray-900 mb-2">All Clear!</h3>
                  <p className="text-gray-600">No active alerts for your area. We'll notify you if anything comes up.</p>
                </div>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                <TrendingUp className="w-6 h-6 text-primary-600" />
                <span>Trending in Your Area</span>
              </h2>

              {trending_issues && trending_issues.length > 0 ? (
                <div className="space-y-3">
                  {trending_issues.map((issue, index) => (
                    <div key={index} className="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{issue.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {issue.count} reports • {issue.location}
                          </p>
                        </div>
                        {issue.verified_count > 0 && (
                          <div className="flex items-center space-x-1 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm font-medium">{issue.verified_count} verified</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-white rounded-xl p-8 text-center border-2 border-gray-200">
                  <p className="text-gray-600">No trending issues in your area</p>
                </div>
              )}
            </motion.div>
          </div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                <Award className="w-6 h-6 text-primary-600" />
                <span>Your Schemes</span>
              </h2>

              {enrolled_schemes && enrolled_schemes.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">Enrolled ({enrolled_schemes.length})</h3>
                  <div className="space-y-3">
                    {enrolled_schemes.map((us) => (
                      <div key={us.id} className="bg-green-50 border-2 border-green-300 rounded-xl p-4">
                        <h4 className="font-bold text-green-900 mb-1">{us.scheme.short_name}</h4>
                        <p className="text-sm text-green-700 mb-2">{us.scheme.benefits}</p>
                        {us.next_payment_date && (
                          <div className="flex items-center space-x-2 text-xs text-green-600">
                            <Clock className="w-3 h-3" />
                            <span>Next payment: {new Date(us.next_payment_date).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {eligible_schemes && eligible_schemes.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">You May Qualify ({eligible_schemes.length})</h3>
                  <div className="space-y-3">
                    {eligible_schemes.slice(0, 3).map((us) => (
                      <div key={us.id} className="bg-white border-2 border-primary-200 rounded-xl p-4 hover:border-primary-400 transition">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-bold text-gray-900 flex-1">{us.scheme.short_name}</h4>
                          <span className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-bold">
                            {Math.round(us.match_score)}%
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{us.scheme.benefits}</p>
                        <button 
                          onClick={() => navigate('/schemes')}
                          className="w-full py-2 gradient-saffron text-white rounded-lg font-semibold text-sm hover:shadow-lg transition"
                        >
                          Apply Now
                        </button>
                      </div>
                    ))}
                  </div>
                  {eligible_schemes.length > 3 && (
                    <button 
                      onClick={() => navigate('/schemes')}
                      className="w-full mt-3 py-2 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold text-sm hover:border-gray-400 transition"
                    >
                      View All Schemes
                    </button>
                  )}
                </div>
              )}

              {(!eligible_schemes || eligible_schemes.length === 0) && (!enrolled_schemes || enrolled_schemes.length === 0) && (
                <div className="bg-white rounded-xl p-8 text-center border-2 border-gray-200">
                  <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600 text-sm">Complete your profile to see matching schemes</p>
                </div>
              )}
            </motion.div>

            {local_prices && Object.keys(local_prices).length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="bg-white rounded-xl p-6 border-2 border-gray-200"
              >
                <h3 className="font-bold text-gray-900 mb-4">Local Prices</h3>
                <div className="space-y-3">
                  {Object.entries(local_prices).slice(0, 5).map(([item, data]) => (
                    <div key={item} className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700 capitalize">{data.item}</span>
                      <span className="text-sm font-bold text-gray-900">₹{data.average.toFixed(0)}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;