import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  Users, MapPin, Calendar, CheckCircle, 
  Clock, Filter, Loader2, TrendingUp 
} from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

const CitizenReports = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ 
    verified: 'all', 
    type: 'all',
    time_range: 168
  });

  useEffect(() => {
    fetchReports();
  }, [filter]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filter.verified === 'verified') params.append('verified', 'true');
      if (filter.type !== 'all') params.append('type', filter.type);
      params.append('time_range', filter.time_range);

      const response = await axios.get(`${API_BASE_URL}/api/reports?${params.toString()}`);
      setReports(response.data.reports);
    } catch (error) {
      console.error('Failed to fetch reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const reportTypes = ['price', 'water', 'electricity', 'health', 'infrastructure', 'other'];

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
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white shadow-2xl">
            <h1 className="text-4xl font-bold mb-2 flex items-center space-x-3">
              <Users className="w-10 h-10" />
              <span>Citizen Intelligence Reports</span>
            </h1>
            <p className="text-white/90 text-lg">Ground-level data from citizens across India</p>
          </div>
        </motion.div>

        <div className="mb-6 bg-white rounded-xl p-4 shadow-lg border-2 border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <Filter className="w-5 h-5 text-gray-600" />
            <span className="font-semibold text-gray-900">Filters</span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Verification Status</label>
              <select
                value={filter.verified}
                onChange={(e) => setFilter({...filter, verified: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Reports</option>
                <option value="verified">Verified Only</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Report Type</label>
              <select
                value={filter.type}
                onChange={(e) => setFilter({...filter, type: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="all">All Types</option>
                {reportTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
              <select
                value={filter.time_range}
                onChange={(e) => setFilter({...filter, time_range: parseInt(e.target.value)})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="24">Last 24 hours</option>
                <option value="72">Last 3 days</option>
                <option value="168">Last week</option>
                <option value="720">Last month</option>
              </select>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-600">Showing {reports.length} reports</span>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-gray-600">
                  {reports.filter(r => r.verified).length} verified
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span className="text-gray-600">
                  {reports.filter(r => r.upvotes > 0).length} with upvotes
                </span>
              </div>
            </div>
          </div>
        </div>

        {reports.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {reports.map((report, index) => (
              <motion.div
                key={report.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                className="bg-white rounded-xl p-5 border-2 border-gray-200 hover:shadow-lg transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-bold capitalize">
                    {report.report_type}
                  </span>
                  {report.verified && (
                    <div className="flex items-center space-x-1 text-green-600">
                      <CheckCircle className="w-4 h-4" />
                      <span className="text-xs font-medium">Verified</span>
                    </div>
                  )}
                </div>

                <h3 className="font-bold text-gray-900 mb-2">
                  {report.title || `${report.report_type} report`}
                </h3>

                {report.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {report.description}
                  </p>
                )}

                {report.data && (() => {
                  try {
                    const data = typeof report.data === 'string' ? JSON.parse(report.data) : report.data;
                    if (data.item && data.price) {
                      return (
                        <div className="mb-3 p-2 bg-green-50 rounded-lg border border-green-200">
                          <span className="text-sm font-semibold text-green-900">
                            {data.item}: ₹{data.price}/{data.unit || 'unit'}
                          </span>
                        </div>
                      );
                    }
                  } catch (e) {
                    return null;
                  }
                })()}

                <div className="space-y-2 pt-3 border-t border-gray-200">
                  <div className="flex items-center space-x-2 text-xs text-gray-600">
                    <MapPin className="w-3 h-3" />
                    <span>{report.city}, {report.state}</span>
                  </div>

                  <div className="flex items-center space-x-2 text-xs text-gray-600">
                    <Calendar className="w-3 h-3" />
                    <span>{new Date(report.created_at).toLocaleString()}</span>
                  </div>

                  {report.upvotes > 0 && (
                    <div className="flex items-center space-x-2 text-xs text-gray-600">
                      <TrendingUp className="w-3 h-3" />
                      <span>{report.upvotes} upvotes</span>
                    </div>
                  )}

                  {report.verification_confidence > 0 && (
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Confidence:</span>
                      <span className="text-xs font-bold text-primary-600">
                        {Math.round(report.verification_confidence * 100)}%
                      </span>
                    </div>
                  )}
                </div>

                <div className="mt-4 flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    report.status === 'resolved' ? 'bg-green-100 text-green-700' :
                    report.status === 'in_progress' ? 'bg-blue-100 text-blue-700' :
                    report.status === 'acknowledged' ? 'bg-purple-100 text-purple-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {report.status || 'pending'}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-xl p-12 text-center border-2 border-gray-200">
            <Users className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Reports Found</h3>
            <p className="text-gray-600">Try adjusting your filters</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CitizenReports;