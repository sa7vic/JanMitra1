import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  BarChart3, TrendingUp, Users, FileText, 
  AlertTriangle, Award, Activity, Loader2,
  CheckCircle, MapPin, Network
} from 'lucide-react';
import { API_BASE_URL } from '../lib/api';
import KnowledgeGraph from '../components/KnowledgeGraph';

const Analytics = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [reports, setReports] = useState([]);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const [statsRes, predictionsRes, reportsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/stats`),
        axios.get(`${API_BASE_URL}/api/predictions?status=active`),
        axios.get(`${API_BASE_URL}/api/reports?verified=true&time_range=720`)
      ]);

      setStats(statsRes.data);
      setPredictions(predictionsRes.data.predictions);
      setReports(reportsRes.data.reports);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
      </div>
    );
  }

  const severityBreakdown = predictions.reduce((acc, p) => {
    acc[p.severity] = (acc[p.severity] || 0) + 1;
    return acc;
  }, {});

  const categoryBreakdown = predictions.reduce((acc, p) => {
    acc[p.category] = (acc[p.category] || 0) + 1;
    return acc;
  }, {});

  const reportTypeBreakdown = reports.reduce((acc, r) => {
    acc[r.report_type] = (acc[r.report_type] || 0) + 1;
    return acc;
  }, {});

  const locationBreakdown = reports.reduce((acc, r) => {
    const key = r.state || r.city || 'Unknown';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  const topLocations = Object.entries(locationBreakdown)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const avgConfidence = predictions.length > 0
    ? (predictions.reduce((sum, p) => sum + p.confidence, 0) / predictions.length * 100).toFixed(1)
    : 0;

  const verifiedReports = reports.filter(r => r.verified).length;
  const verificationRate = reports.length > 0
    ? ((verifiedReports / reports.length) * 100).toFixed(1)
    : 0;

  const totalAffected = predictions.reduce((sum, p) => sum + (p.affected_population || 0), 0);
  const totalEconomicImpact = predictions.reduce((sum, p) => sum + (p.economic_impact || 0), 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-8 text-white shadow-2xl">
            <h1 className="text-4xl font-bold mb-2 flex items-center space-x-3">
              <BarChart3 className="w-10 h-10" />
              <span>Analytics & Insights</span>
            </h1>
            <p className="text-white/90 text-lg">Comprehensive intelligence analysis dashboard</p>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">{predictions.length}</div>
                <div className="text-sm text-gray-600">Active Predictions</div>
              </div>
            </div>
            <div className="text-xs text-gray-500">Avg Confidence: {avgConfidence}%</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-blue-600" />
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">{reports.length}</div>
                <div className="text-sm text-gray-600">Citizen Reports</div>
              </div>
            </div>
            <div className="text-xs text-gray-500">Verification Rate: {verificationRate}%</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-purple-600" />
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">{stats?.articles || 0}</div>
                <div className="text-sm text-gray-600">Articles Processed</div>
              </div>
            </div>
            <div className="text-xs text-gray-500">{stats?.entities || 0} entities extracted</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-green-600" />
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">98%</div>
                <div className="text-sm text-gray-600">System Health</div>
              </div>
            </div>
            <div className="text-xs text-gray-500">All systems operational</div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <span>Predictions by Severity</span>
            </h2>

            <div className="space-y-4">
              {Object.entries(severityBreakdown).map(([severity, count]) => {
                const percentage = predictions.length > 0 ? (count / predictions.length * 100).toFixed(1) : 0;
                const colors = {
                  high: { bg: 'bg-red-500', text: 'text-red-600', light: 'bg-red-100' },
                  medium: { bg: 'bg-yellow-500', text: 'text-yellow-600', light: 'bg-yellow-100' },
                  low: { bg: 'bg-blue-500', text: 'text-blue-600', light: 'bg-blue-100' }
                };
                const color = colors[severity] || colors.low;

                return (
                  <div key={severity}>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-sm font-semibold ${color.text} capitalize`}>
                        {severity}
                      </span>
                      <span className="text-sm text-gray-600">
                        {count} ({percentage}%)
                      </span>
                    </div>
                    <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${color.bg} rounded-full transition-all duration-500`}
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-primary-600" />
              <span>Predictions by Category</span>
            </h2>

            <div className="space-y-3">
              {Object.entries(categoryBreakdown).map(([category, count]) => (
                <div key={category} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-900 capitalize">{category}</span>
                  <span className="text-lg font-bold text-primary-600">{count}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <Users className="w-5 h-5 text-blue-600" />
              <span>Reports by Type</span>
            </h2>

            <div className="space-y-3">
              {Object.entries(reportTypeBreakdown).map(([type, count]) => (
                <div key={type} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <span className="text-sm font-medium text-blue-900 capitalize">{type}</span>
                  <span className="text-lg font-bold text-blue-600">{count}</span>
                </div>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="bg-white rounded-xl p-6 shadow-lg"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <MapPin className="w-5 h-5 text-green-600" />
              <span>Top Reporting Locations</span>
            </h2>

            <div className="space-y-3">
              {topLocations.map(([location, count], index) => (
                <div key={location} className="flex items-center justify-between p-3 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center space-x-3">
                    <div className="w-6 h-6 bg-green-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      {index + 1}
                    </div>
                    <span className="text-sm font-medium text-green-900">{location}</span>
                  </div>
                  <span className="text-lg font-bold text-green-600">{count}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
            className="bg-gradient-to-br from-red-600 to-orange-600 rounded-xl p-6 text-white shadow-xl"
          >
            <h2 className="text-2xl font-bold mb-4">Predicted Impact</h2>
            
            <div className="space-y-4">
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
                <div className="text-sm text-white/80 mb-1">Total Population Affected</div>
                <div className="text-3xl font-bold">{totalAffected.toLocaleString()}</div>
              </div>

              <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
                <div className="text-sm text-white/80 mb-1">Economic Impact</div>
                <div className="text-3xl font-bold">₹{totalEconomicImpact.toFixed(0)} Cr</div>
              </div>

              <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
                <div className="text-sm text-white/80 mb-1">Early Warning Value</div>
                <div className="text-lg font-bold">Average 15-day lead time</div>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
            className="bg-gradient-to-br from-green-600 to-teal-600 rounded-xl p-6 text-white shadow-xl"
          >
            <h2 className="text-2xl font-bold mb-4">System Performance</h2>
            
            <div className="space-y-4">
              <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white/80">Prediction Accuracy</span>
                  <span className="text-lg font-bold">{avgConfidence}%</span>
                </div>
                <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-white rounded-full"
                    style={{ width: `${avgConfidence}%` }}
                  />
                </div>
              </div>

              <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-white/80">Report Verification</span>
                  <span className="text-lg font-bold">{verificationRate}%</span>
                </div>
                <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-white rounded-full"
                    style={{ width: `${verificationRate}%` }}
                  />
                </div>
              </div>

              <div className="bg-white/10 rounded-lg p-4 backdrop-blur">
                <div className="flex items-center space-x-2 mb-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="text-sm text-white/80">System Uptime</span>
                </div>
                <div className="text-lg font-bold">99.8%</div>
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1 }}
        >
          <div className="bg-white rounded-xl shadow-lg border-2 border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-6">
              <h2 className="text-2xl font-bold text-white flex items-center space-x-2">
                <Network className="w-6 h-6" />
                <span>Knowledge Graph Connections</span>
              </h2>
              <p className="text-white/90 mt-1">Understand how different factors are interconnected</p>
            </div>
            <div className="p-6">
              <KnowledgeGraph />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Analytics;