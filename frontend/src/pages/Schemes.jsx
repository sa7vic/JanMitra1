import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { Award, ExternalLink, FileText, CheckCircle, Clock, TrendingUp, Loader2, ChevronRight, X } from 'lucide-react';

const Schemes = () => {
  const [schemes, setSchemes] = useState({ enrolled: [], eligible: [] });
  const [loading, setLoading] = useState(true);
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [activeTab, setActiveTab] = useState('eligible');

  useEffect(() => {
    fetchSchemes();
  }, []);

  const fetchSchemes = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/user/schemes');
      setSchemes(response.data);
    } catch (error) {
      console.error('Failed to fetch schemes:', error);
    } finally {
      setLoading(false);
    }
  };

  const SchemeCard = ({ userScheme, enrolled }) => {
    const scheme = userScheme.scheme;
    
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ y: -4 }}
        className={`bg-white rounded-xl p-6 border-2 ${
          enrolled ? 'border-green-300 bg-green-50' : 'border-primary-200'
        } hover:shadow-lg transition cursor-pointer`}
        onClick={() => setSelectedScheme(userScheme)}
      >
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-1">{scheme.short_name || scheme.name}</h3>
            <p className="text-sm text-gray-600 mb-2">{scheme.ministry}</p>
          </div>
          
          {!enrolled && userScheme.match_score && (
            <div className="flex items-center space-x-2">
              <div className="text-right">
                <div className="text-2xl font-bold text-primary-600">{Math.round(userScheme.match_score)}</div>
                <div className="text-xs text-gray-600">Match</div>
              </div>
              <TrendingUp className="w-5 h-5 text-primary-600" />
            </div>
          )}
          
          {enrolled && (
            <div className="flex items-center space-x-2 text-green-600">
              <CheckCircle className="w-6 h-6" />
              <span className="text-sm font-bold">Enrolled</span>
            </div>
          )}
        </div>

        <p className="text-gray-700 mb-4 line-clamp-2">{scheme.description}</p>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div>
            <div className="text-sm font-semibold text-gray-900 mb-1">Benefits</div>
            <div className="text-sm text-gray-600 line-clamp-1">{scheme.benefits}</div>
          </div>
          
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </div>

        {enrolled && userScheme.next_payment_date && (
          <div className="mt-4 flex items-center space-x-2 text-sm text-green-700 bg-green-100 px-3 py-2 rounded-lg">
            <Clock className="w-4 h-4" />
            <span>Next payment: {new Date(userScheme.next_payment_date).toLocaleDateString()}</span>
          </div>
        )}

        {enrolled && userScheme.total_benefit_received > 0 && (
          <div className="mt-2 text-sm text-gray-600">
            Total received: <span className="font-bold text-green-600">₹{userScheme.total_benefit_received.toLocaleString()}</span>
          </div>
        )}
      </motion.div>
    );
  };

  const SchemeDetailModal = ({ userScheme, onClose }) => {
    const scheme = userScheme.scheme;
    const criteria = scheme.eligibility_criteria || {};
    const documents = scheme.documents_required || [];
    const process = scheme.application_process || [];

    return (
      <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="sticky top-0 bg-gradient-to-r from-primary-600 to-orange-600 p-6 text-white rounded-t-2xl">
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-3xl font-bold mb-2">{scheme.name}</h2>
                <p className="text-white/90">{scheme.ministry}</p>
              </div>
              <button
                onClick={onClose}
                className="text-white hover:bg-white/20 rounded-lg p-2 transition"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>

          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">About This Scheme</h3>
              <p className="text-gray-700 leading-relaxed">{scheme.description}</p>
            </div>

            <div className="bg-primary-50 border-2 border-primary-200 rounded-xl p-6">
              <h3 className="text-xl font-bold text-primary-900 mb-3">Benefits</h3>
              <p className="text-primary-800 text-lg font-semibold">{scheme.benefits}</p>
            </div>

            {Object.keys(criteria).length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Eligibility Criteria</h3>
                <div className="bg-gray-50 rounded-xl p-4 space-y-2">
                  {Object.entries(criteria).map(([key, value]) => (
                    <div key={key} className="flex items-start space-x-3">
                      <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <span className="font-medium text-gray-900 capitalize">{key.replace(/_/g, ' ')}: </span>
                        <span className="text-gray-700">
                          {typeof value === 'object' ? JSON.stringify(value) : value.toString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {documents.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center space-x-2">
                  <FileText className="w-6 h-6 text-primary-600" />
                  <span>Documents Required</span>
                </h3>
                <ul className="space-y-2">
                  {documents.map((doc, index) => (
                    <li key={index} className="flex items-center space-x-3 text-gray-700">
                      <div className="w-2 h-2 bg-primary-600 rounded-full" />
                      <span>{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {process.length > 0 && (
              <div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">Application Process</h3>
                <div className="space-y-4">
                  {process.map((step, index) => (
                    <div key={index} className="flex items-start space-x-4">
                      <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                        {index + 1}
                      </div>
                      <p className="text-gray-700 pt-1">{step}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
              <h4 className="font-bold text-blue-900 mb-2">How to Apply</h4>
              <p className="text-blue-800 mb-3">{scheme.how_to_apply}</p>
              {scheme.url && (
                <a
                  href={scheme.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                >
                  <span>Visit Official Website</span>
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={onClose}
                className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:border-gray-400 transition"
              >
                Close
              </button>
              <button 
                onClick={() => {
                  if (scheme.url) {
                    window.open(scheme.url, '_blank');
                  } else {
                    alert('📋 Application Steps:\n\n1. Visit nearest government office or CSC center\n2. Carry all required documents listed above\n3. Fill the application form\n4. Submit and get acknowledgement\n\nFor more details, contact your local government office.');
                  }
                }}
                className="flex-1 py-3 gradient-saffron text-white rounded-lg font-semibold hover:shadow-lg transition"
              >
                Start Application
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center space-x-3">
            <Award className="w-10 h-10 text-primary-600" />
            <span>Government Schemes</span>
          </h1>
          <p className="text-gray-600">Discover schemes you qualify for and track your enrollments</p>
        </motion.div>

        <div className="mb-6 flex items-center space-x-2 bg-white rounded-lg p-1 border border-gray-200 inline-flex">
          <button
            onClick={() => setActiveTab('eligible')}
            className={`px-6 py-3 rounded-lg font-medium transition ${
              activeTab === 'eligible'
                ? 'bg-primary-600 text-white'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            You May Qualify ({schemes.eligible.length})
          </button>
          <button
            onClick={() => setActiveTab('enrolled')}
            className={`px-6 py-3 rounded-lg font-medium transition ${
              activeTab === 'enrolled'
                ? 'bg-primary-600 text-white'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Enrolled ({schemes.enrolled.length})
          </button>
        </div>

        {activeTab === 'eligible' && (
          <div>
            {schemes.eligible.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {schemes.eligible.map((userScheme) => (
                  <SchemeCard key={userScheme.id} userScheme={userScheme} enrolled={false} />
                ))}
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-white rounded-xl p-12 text-center border-2 border-gray-200"
              >
                <Award className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">No Matching Schemes</h3>
                <p className="text-gray-600">Complete your profile to discover schemes you qualify for</p>
              </motion.div>
            )}
          </div>
        )}

        {activeTab === 'enrolled' && (
          <div>
            {schemes.enrolled.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {schemes.enrolled.map((userScheme) => (
                  <SchemeCard key={userScheme.id} userScheme={userScheme} enrolled={true} />
                ))}
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-white rounded-xl p-12 text-center border-2 border-gray-200"
              >
                <CheckCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 mb-2">No Enrollments Yet</h3>
                <p className="text-gray-600">Apply to eligible schemes to see them here</p>
              </motion.div>
            )}
          </div>
        )}

        {selectedScheme && (
          <SchemeDetailModal
            userScheme={selectedScheme}
            onClose={() => setSelectedScheme(null)}
          />
        )}
      </div>
    </div>
  );
};

export default Schemes;