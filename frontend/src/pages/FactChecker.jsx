import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { CheckCircle, XCircle, AlertCircle, HelpCircle, Search, Clock, Loader2, Share2, ThumbsUp } from 'lucide-react';
import { API_BASE_URL } from '../lib/api';

const FactChecker = () => {
  const [claim, setClaim] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [recentChecks, setRecentChecks] = useState([]);

  useEffect(() => {
    fetchRecentChecks();
  }, []);

  const fetchRecentChecks = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/fact-checks?limit=10`);
      setRecentChecks(response.data.fact_checks);
    } catch (error) {
      console.error('Failed to fetch recent checks:', error);
    }
  };

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!claim.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/fact-check`, {
        claim: claim.trim()
      });
      setResult(response.data);
      setClaim('');
      fetchRecentChecks();
    } catch (error) {
      console.error('Fact check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const verdictConfig = {
    TRUE: {
      icon: CheckCircle,
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-300',
      label: 'TRUE',
      description: 'This claim is accurate based on verified sources'
    },
    FALSE: {
      icon: XCircle,
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-300',
      label: 'FALSE',
      description: 'This claim is not supported by evidence'
    },
    PARTIALLY_TRUE: {
      icon: AlertCircle,
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-300',
      label: 'PARTIALLY TRUE',
      description: 'This claim contains some truth but is misleading'
    },
    UNVERIFIED: {
      icon: HelpCircle,
      color: 'text-gray-600',
      bg: 'bg-gray-50',
      border: 'border-gray-300',
      label: 'UNVERIFIED',
      description: 'Not enough evidence to verify this claim'
    }
  };

  const exampleClaims = [
    'Government is giving free ₹5000 to everyone',
    'Petrol prices increased by 50% in 2024',
    'India became the 5th largest economy',
    'PM-KISAN gives ₹6000 per year to farmers'
  ];

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 text-center"
        >
          <div className="w-20 h-20 bg-gradient-to-r from-primary-600 to-orange-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Fact Checker</h1>
          <p className="text-gray-600">Verify claims and combat misinformation instantly</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 p-8 mb-8"
        >
          <form onSubmit={handleCheck} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Enter claim to verify
              </label>
              <textarea
                value={claim}
                onChange={(e) => setClaim(e.target.value)}
                placeholder="Paste any claim from social media, WhatsApp, or news..."
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                rows={4}
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading || !claim.trim()}
              className="w-full py-4 gradient-saffron text-white rounded-xl font-bold text-lg hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span>Verifying...</span>
                </>
              ) : (
                <>
                  <Search className="w-6 h-6" />
                  <span>Verify Claim</span>
                </>
              )}
            </button>
          </form>

          <div className="mt-6">
            <p className="text-sm text-gray-600 mb-3">Try these examples:</p>
            <div className="flex flex-wrap gap-2">
              {exampleClaims.map((example, index) => (
                <button
                  key={index}
                  onClick={() => setClaim(example)}
                  className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition"
                >
                  {example}
                </button>
              ))}
            </div>
          </div>
        </motion.div>

        {result && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-8"
          >
            {(() => {
              const config = verdictConfig[result.verdict] || verdictConfig.UNVERIFIED;
              const Icon = config.icon;

              return (
                <div className={`${config.bg} border-2 ${config.border} rounded-2xl p-8`}>
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center space-x-4">
                      <Icon className={`w-12 h-12 ${config.color}`} />
                      <div>
                        <h2 className={`text-3xl font-bold ${config.color}`}>{config.label}</h2>
                        <p className="text-sm text-gray-600 mt-1">{config.description}</p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-3xl font-bold text-gray-900">{Math.round(result.confidence * 100)}%</div>
                      <div className="text-sm text-gray-600">Confidence</div>
                    </div>
                  </div>

                  <div className="bg-white/50 rounded-xl p-4 mb-6">
                    <h3 className="font-bold text-gray-900 mb-2">Claim Checked:</h3>
                    <p className="text-gray-700 italic">"{result.claim}"</p>
                  </div>

                  <div className="bg-white/50 rounded-xl p-4 mb-6">
                    <h3 className="font-bold text-gray-900 mb-2">Explanation:</h3>
                    <p className="text-gray-700 leading-relaxed">{result.explanation}</p>
                  </div>

                  {result.sources && result.sources.length > 0 && (
                    <div className="bg-white/50 rounded-xl p-4 mb-6">
                      <h3 className="font-bold text-gray-900 mb-3">Sources:</h3>
                      <ul className="space-y-2">
                        {result.sources.map((source, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-gray-600 rounded-full mt-2 flex-shrink-0" />
                            <span className="text-gray-700 text-sm">{source}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex items-center space-x-4">
                    <button className="flex items-center space-x-2 px-4 py-2 bg-white border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:border-gray-400 transition">
                      <Share2 className="w-4 h-4" />
                      <span>Share Result</span>
                    </button>
                    <button className="flex items-center space-x-2 px-4 py-2 bg-white border-2 border-gray-300 rounded-lg font-semibold text-gray-700 hover:border-gray-400 transition">
                      <ThumbsUp className="w-4 h-4" />
                      <span>Helpful</span>
                    </button>
                  </div>
                </div>
              );
            })()}
          </motion.div>
        )}

        {recentChecks.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
              <Clock className="w-6 h-6 text-primary-600" />
              <span>Recent Fact Checks</span>
            </h2>

            <div className="space-y-3">
              {recentChecks.map((check, index) => {
                const config = verdictConfig[check.verdict] || verdictConfig.UNVERIFIED;
                const Icon = config.icon;

                return (
                  <motion.div
                    key={check.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition cursor-pointer"
                    onClick={() => setResult(check)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 mr-4">
                        <p className="text-gray-900 font-medium mb-2 line-clamp-2">"{check.claim}"</p>
                        <div className="flex items-center space-x-3 text-sm text-gray-600">
                          <span>{new Date(check.created_at).toLocaleDateString()}</span>
                          <span>•</span>
                          <span>{Math.round(check.confidence * 100)}% confidence</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2 flex-shrink-0">
                        <Icon className={`w-6 h-6 ${config.color}`} />
                        <span className={`text-sm font-bold ${config.color}`}>{config.label}</span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default FactChecker;