import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  FileText, Plus, CheckCircle, Clock, XCircle, 
  TrendingUp, MapPin, Calendar, Loader2 
} from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

const MyReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchMyReports();
  }, []);

  const fetchMyReports = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/user/dashboard`);
      setReports(response.data.my_reports || []);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const statusConfig = {
    pending: {
      icon: Clock,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-300',
      label: 'Pending Review'
    },
    acknowledged: {
      icon: CheckCircle,
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-300',
      label: 'Acknowledged'
    },
    in_progress: {
      icon: TrendingUp,
      color: 'text-purple-600',
      bg: 'bg-purple-50',
      border: 'border-purple-300',
      label: 'In Progress'
    },
    resolved: {
      icon: CheckCircle,
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-300',
      label: 'Resolved'
    },
    rejected: {
      icon: XCircle,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-300',
      label: 'Not Valid'
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center space-x-3">
              <FileText className="w-10 h-10 text-primary-600" />
              <span>My Reports</span>
            </h1>
            <p className="text-gray-600">Track your contributions to community intelligence</p>
          </div>

          <button
            onClick={() => navigate('/report')}
            className="flex items-center space-x-2 px-6 py-3 gradient-saffron text-white rounded-lg font-semibold hover:shadow-lg transition"
          >
            <Plus className="w-5 h-5" />
            <span>New Report</span>
          </button>
        </motion.div>

        {reports.length > 0 ? (
          <div className="space-y-4">
            {reports.map((report, index) => {
              const config = statusConfig[report.status] || statusConfig.pending;
              const Icon = config.icon;

              return (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`${config.bg} border-2 ${config.border} rounded-xl p-6 hover:shadow-lg transition`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-bold capitalize">
                          {report.report_type}
                        </span>
                        {report.verified && (
                          <div className="flex items-center space-x-1 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm font-medium">Verified</span>
                          </div>
                        )}
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">
                        {report.title || `${report.report_type} report`}
                      </h3>
                      {report.description && (
                        <p className="text-gray-700 line-clamp-2">{report.description}</p>
                      )}
                    </div>

                    <div className={`flex items-center space-x-2 px-3 py-2 ${config.bg} border-2 ${config.border} rounded-lg`}>
                      <Icon className={`w-5 h-5 ${config.color}`} />
                      <span className={`text-sm font-bold ${config.color}`}>{config.label}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <MapPin className="w-4 h-4" />
                      <span>{report.city}, {report.state}</span>
                    </div>
                    
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(report.created_at).toLocaleDateString()}</span>
                    </div>

                    {report.upvotes > 0 && (
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <TrendingUp className="w-4 h-4" />
                        <span>{report.upvotes} upvotes</span>
                      </div>
                    )}

                    {report.verification_confidence > 0 && (
                      <div className="text-sm text-gray-600">
                        <span className="font-bold">{Math.round(report.verification_confidence * 100)}%</span> confidence
                      </div>
                    )}
                  </div>

                  {report.status === 'resolved' && (
                    <div className="mt-4 p-3 bg-green-100 border border-green-300 rounded-lg">
                      <p className="text-sm text-green-800 font-medium">
                        ✅ This issue has been resolved! Thank you for reporting. You earned +15 reputation points.
                      </p>
                    </div>
                  )}
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
            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Reports Yet</h3>
            <p className="text-gray-600 mb-6">Start contributing to your community by reporting issues</p>
            <button
              onClick={() => navigate('/report')}
              className="inline-flex items-center space-x-2 px-6 py-3 gradient-saffron text-white rounded-lg font-semibold hover:shadow-lg transition"
            >
              <Plus className="w-5 h-5" />
              <span>Submit First Report</span>
            </button>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 bg-gradient-to-r from-primary-50 to-orange-50 rounded-xl p-6 border-2 border-primary-200"
        >
          <h3 className="text-lg font-bold text-gray-900 mb-3">💡 How Your Reports Help</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-start space-x-2">
              <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center flex-shrink-0 font-bold">1</div>
              <div>
                <div className="font-semibold text-gray-900">Early Warning</div>
                <div className="text-gray-600">Your reports help AI predict crises before they escalate</div>
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center flex-shrink-0 font-bold">2</div>
              <div>
                <div className="font-semibold text-gray-900">Government Action</div>
                <div className="text-gray-600">Officials see verified reports and can respond faster</div>
              </div>
            </div>
            <div className="flex items-start space-x-2">
              <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center flex-shrink-0 font-bold">3</div>
              <div>
                <div className="font-semibold text-gray-900">Community Trust</div>
                <div className="text-gray-600">Build reputation and help your neighbors stay informed</div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default MyReports;