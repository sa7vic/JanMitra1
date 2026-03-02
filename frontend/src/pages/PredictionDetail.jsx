import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  AlertTriangle, MapPin, Calendar, TrendingUp, 
  Users, FileText, DollarSign, ChevronLeft, 
  CheckCircle, Loader2, Download 
} from 'lucide-react';

const PredictionDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [prediction, setPrediction] = useState(null);
  const [relatedReports, setRelatedReports] = useState([]);

  useEffect(() => {
    fetchPredictionDetail();
  }, [id]);

  const fetchPredictionDetail = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/predictions/${id}`);
      setPrediction(response.data.prediction);
      setRelatedReports(response.data.related_reports || []);
    } catch (error) {
      console.error('Failed to fetch prediction:', error);
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

  if (!prediction) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">Prediction not found</p>
        </div>
      </div>
    );
  }

  const severityConfig = {
    high: { 
      color: 'text-red-600', 
      bg: 'bg-red-50', 
      border: 'border-red-300',
      badge: 'bg-red-600',
      gradient: 'from-red-600 to-orange-600'
    },
    medium: { 
      color: 'text-yellow-600', 
      bg: 'bg-yellow-50', 
      border: 'border-yellow-300',
      badge: 'bg-yellow-600',
      gradient: 'from-yellow-600 to-orange-600'
    },
    low: { 
      color: 'text-blue-600', 
      bg: 'bg-blue-50', 
      border: 'border-blue-300',
      badge: 'bg-blue-600',
      gradient: 'from-blue-600 to-purple-600'
    }
  };

  const config = severityConfig[prediction.severity] || severityConfig.low;
  const evidence = prediction.evidence || {};
  const impact = prediction.impact_estimate || {};
  const actions = prediction.recommended_actions || [];

  const daysUntil = prediction.predicted_date 
    ? Math.ceil((new Date(prediction.predicted_date) - new Date()) / (1000 * 60 * 60 * 24))
    : 0;

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <button
          onClick={() => navigate('/government')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 mb-6 transition"
        >
          <ChevronLeft className="w-5 h-5" />
          <span className="font-medium">Back to Dashboard</span>
        </button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`bg-gradient-to-r ${config.gradient} rounded-2xl p-8 text-white shadow-2xl mb-8`}
        >
          <div className="flex items-start justify-between mb-6">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-3">
                <span className={`px-4 py-2 bg-white/20 rounded-full text-sm font-bold uppercase`}>
                  {prediction.severity} SEVERITY
                </span>
                <span className="px-4 py-2 bg-white/20 rounded-full text-sm font-bold">
                  {Math.round(prediction.confidence * 100)}% Confidence
                </span>
              </div>
              <h1 className="text-4xl font-bold mb-3">{prediction.title}</h1>
              <p className="text-white/90 text-lg leading-relaxed">{prediction.description}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <MapPin className="w-6 h-6 mb-2" />
              <div className="text-sm opacity-80">Location</div>
              <div className="text-xl font-bold">{prediction.location}</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur rounded-lg p-4">
              <Calendar className="w-6 h-6 mb-2" />
              <div className="text-sm opacity-80">Timeline</div>
              <div className="text-xl font-bold">{daysUntil > 0 ? `${daysUntil} days` : 'Imminent'}</div>
            </div>
            
            {prediction.affected_population && (
              <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                <Users className="w-6 h-6 mb-2" />
                <div className="text-sm opacity-80">Affected</div>
                <div className="text-xl font-bold">{prediction.affected_population.toLocaleString()}</div>
              </div>
            )}
            
            {prediction.economic_impact && (
              <div className="bg-white/10 backdrop-blur rounded-lg p-4">
                <DollarSign className="w-6 h-6 mb-2" />
                <div className="text-sm opacity-80">Economic Impact</div>
                <div className="text-xl font-bold">₹{prediction.economic_impact.toFixed(0)}Cr</div>
              </div>
            )}
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            {Object.keys(evidence).length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-xl p-6 shadow-lg border-2 border-gray-200"
              >
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                  <TrendingUp className="w-6 h-6 text-primary-600" />
                  <span>Evidence & Analysis</span>
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(evidence).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                      <div className="text-sm text-gray-600 mb-1 capitalize">
                        {key.replace(/_/g, ' ')}
                      </div>
                      <div className="text-lg font-bold text-gray-900">
                        {typeof value === 'object' ? JSON.stringify(value) : value}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {actions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-xl p-6 shadow-lg border-2 border-gray-200"
              >
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                  <CheckCircle className="w-6 h-6 text-primary-600" />
                  <span>Recommended Actions</span>
                </h2>
                
                <div className="space-y-6">
                  {actions.map((phase, index) => (
                    <div key={index} className="border-l-4 border-primary-600 pl-4">
                      <h3 className="text-lg font-bold text-gray-900 mb-3">
                        Phase {index + 1}: {phase.phase || 'Action Phase'}
                      </h3>
                      {phase.actions && (
                        <ul className="space-y-2">
                          {phase.actions.map((action, idx) => (
                            <li key={idx} className="flex items-start space-x-3">
                              <div className="w-6 h-6 bg-primary-600 text-white rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 text-sm font-bold">
                                {idx + 1}
                              </div>
                              <span className="text-gray-700">{action}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-white rounded-xl p-6 shadow-lg border-2 border-gray-200"
            >
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                <Users className="w-5 h-5 text-primary-600" />
                <span>Citizen Intel</span>
              </h3>

              {relatedReports.length > 0 ? (
                <div className="space-y-3">
                  <div className="text-center py-4 bg-primary-50 rounded-lg border-2 border-primary-200">
                    <div className="text-4xl font-bold text-primary-600">{relatedReports.length}</div>
                    <div className="text-sm text-primary-700 font-medium">Verified Reports</div>
                  </div>

                  <div className="space-y-2">
                    {relatedReports.slice(0, 5).map((report, index) => (
                      <div key={report.id} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="font-semibold text-gray-900 text-sm mb-1">
                          {report.title || report.report_type}
                        </div>
                        <div className="text-xs text-gray-600 flex items-center space-x-2">
                          <MapPin className="w-3 h-3" />
                          <span>{report.city}</span>
                          <span>•</span>
                          <span>{new Date(report.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="text-xs text-gray-600 mt-3 p-3 bg-green-50 rounded-lg border border-green-200">
                    <strong className="text-green-800">Validation:</strong> Multiple citizen reports confirm this prediction
                  </div>
                </div>
              ) : (
                <div className="text-center py-6">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-2" />
                  <p className="text-sm text-gray-600">No citizen reports yet</p>
                </div>
              )}
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-gradient-to-br from-primary-600 to-orange-600 rounded-xl p-6 text-white"
            >
              <h3 className="text-xl font-bold mb-4">Actions</h3>
              <div className="space-y-3">
                <button className="w-full py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-white/90 transition flex items-center justify-center space-x-2">
                  <Download className="w-5 h-5" />
                  <span>Download Report</span>
                </button>
                <button className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg font-semibold transition">
                  Assign to Department
                </button>
                <button className="w-full py-3 bg-white/20 hover:bg-white/30 rounded-lg font-semibold transition">
                  Mark as Active Response
                </button>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PredictionDetail;