import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { AlertCircle, DollarSign, Droplet, Zap, MapPin, Camera, Send, CheckCircle, X, Upload, Image } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const ReportIssue = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    report_type: '',
    title: '',
    description: '',
    location: user?.location || '',
    city: user?.city || '',
    state: user?.state || '',
    data: {}
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [photoFile, setPhotoFile] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoError, setPhotoError] = useState(null);
  const [submitError, setSubmitError] = useState(null);
  const fileInputRef = useRef(null);

  const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp', 'image/heic'];
  const MAX_SIZE_MB = 5;

  const reportTypes = [
    {
      id: 'price',
      label: 'Price Report',
      icon: DollarSign,
      color: 'bg-green-50 border-green-300 hover:border-green-400',
      description: 'Report commodity prices in your area'
    },
    {
      id: 'water',
      label: 'Water Issue',
      icon: Droplet,
      color: 'bg-blue-50 border-blue-300 hover:border-blue-400',
      description: 'Water shortage, quality, or supply problems'
    },
    {
      id: 'electricity',
      label: 'Electricity Issue',
      icon: Zap,
      color: 'bg-yellow-50 border-yellow-300 hover:border-yellow-400',
      description: 'Power cuts, voltage issues, or billing problems'
    },
    {
      id: 'infrastructure',
      label: 'Infrastructure',
      icon: MapPin,
      color: 'bg-purple-50 border-purple-300 hover:border-purple-400',
      description: 'Roads, drainage, or public facility issues'
    },
    {
      id: 'health',
      label: 'Health Concern',
      icon: AlertCircle,
      color: 'bg-red-50 border-red-300 hover:border-red-400',
      description: 'Disease outbreak, sanitation, or health facility issues'
    },
    {
      id: 'other',
      label: 'Other Issue',
      icon: AlertCircle,
      color: 'bg-gray-50 border-gray-300 hover:border-gray-400',
      description: 'Any other concern or observation'
    }
  ];

  const commodities = [
    'Onion', 'Tomato', 'Potato', 'Rice', 'Wheat', 'Atta (Flour)', 
    'Sugar', 'Cooking Oil', 'Petrol', 'Diesel', 'LPG Cylinder', 
    'Milk', 'Egg', 'Chicken', 'Fish', 'Dal (Lentils)', 'Other'
  ];

  const handleTypeSelect = (typeId) => {
    setFormData({ ...formData, report_type: typeId });
    setStep(2);
  };

  const handlePhotoChange = (e) => {
    setPhotoError(null);
    const file = e.target.files[0];
    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setPhotoError('Invalid file type. Allowed: JPG, PNG, GIF, WebP, HEIC');
      e.target.value = '';
      return;
    }

    if (file.size > MAX_SIZE_MB * 1024 * 1024) {
      setPhotoError(`File too large. Maximum size is ${MAX_SIZE_MB} MB`);
      e.target.value = '';
      return;
    }

    setPhotoFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setPhotoPreview(reader.result);
    reader.readAsDataURL(file);
  };

  const handleRemovePhoto = () => {
    setPhotoFile(null);
    setPhotoPreview(null);
    setPhotoError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setSubmitError(null);

    try {
      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      if (photoFile) {
        // Send as multipart/form-data when a photo is attached
        const fd = new FormData();
        fd.append('report_type', formData.report_type);
        fd.append('title', formData.title);
        fd.append('description', formData.description);
        fd.append('location', formData.location);
        fd.append('city', formData.city);
        fd.append('state', formData.state);
        fd.append('data', JSON.stringify(formData.data));
        fd.append('photo', photoFile);

        await axios.post('http://localhost:5000/api/reports', fd, {
          headers: { ...headers },  // axios sets Content-Type automatically for FormData
        });
      } else {
        // JSON submission (no photo)
        const reportData = {
          ...formData,
          data: JSON.stringify(formData.data),
        };
        await axios.post('http://localhost:5000/api/reports', reportData, {
          headers: { ...headers, 'Content-Type': 'application/json' },
        });
      }

      setSuccess(true);
      setTimeout(() => {
        navigate('/my-reports');
      }, 2000);
    } catch (error) {
      console.error('Failed to submit report:', error);
      const msg =
        error?.response?.data?.error ||
        'Failed to submit report. Please try again.';
      setSubmitError(msg);
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gray-50 pt-20 pb-12 flex items-center justify-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="text-center"
        >
          <div className="w-24 h-24 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <CheckCircle className="w-16 h-16 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Report Submitted!</h2>
          <p className="text-gray-600 mb-4">Thank you for helping improve your community</p>
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
            <span>+5 Reputation Points</span>
            <span>•</span>
            <span>Your report will be verified</span>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pt-20 pb-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Report an Issue</h1>
          <p className="text-gray-600">Your reports help government respond faster and predict crises</p>
        </motion.div>

        {step === 1 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <h2 className="text-xl font-bold text-gray-900 mb-4">What would you like to report?</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reportTypes.map((type, index) => {
                const Icon = type.icon;
                return (
                  <motion.button
                    key={type.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => handleTypeSelect(type.id)}
                    className={`${type.color} border-2 rounded-xl p-6 text-left hover:shadow-lg transition`}
                  >
                    <Icon className="w-10 h-10 mb-3 text-gray-700" />
                    <h3 className="text-lg font-bold text-gray-900 mb-1">{type.label}</h3>
                    <p className="text-sm text-gray-600">{type.description}</p>
                  </motion.button>
                );
              })}
            </div>
          </motion.div>
        )}

        {step === 2 && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-white rounded-2xl shadow-lg border-2 border-gray-200 p-8"
          >
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                Report Details - {reportTypes.find(t => t.id === formData.report_type)?.label}
              </h2>
              <button
                onClick={() => setStep(1)}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                Change Type
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {formData.report_type === 'price' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Commodity
                    </label>
                    <select
                      value={formData.data.item || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        data: { ...formData.data, item: e.target.value },
                        title: `${e.target.value} price report`
                      })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      required
                    >
                      <option value="">Select commodity</option>
                      {commodities.map(item => (
                        <option key={item} value={item}>{item}</option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Price (₹)
                      </label>
                      <input
                        type="number"
                        value={formData.data.price || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          data: { ...formData.data, price: e.target.value }
                        })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                        placeholder="Enter price"
                        required
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Unit
                      </label>
                      <select
                        value={formData.data.unit || 'kg'}
                        onChange={(e) => setFormData({
                          ...formData,
                          data: { ...formData.data, unit: e.target.value }
                        })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="kg">per kg</option>
                        <option value="liter">per liter</option>
                        <option value="dozen">per dozen</option>
                        <option value="piece">per piece</option>
                        <option value="quintal">per quintal</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Market/Shop Name (Optional)
                    </label>
                    <input
                      type="text"
                      value={formData.data.location_name || ''}
                      onChange={(e) => setFormData({
                        ...formData,
                        data: { ...formData.data, location_name: e.target.value }
                      })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="E.g., Main Market, XYZ Store"
                    />
                  </div>
                </>
              )}

              {formData.report_type !== 'price' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Issue Title
                    </label>
                    <input
                      type="text"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Brief description of the issue"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Detailed Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                      rows={6}
                      placeholder="Provide detailed information about the issue..."
                      required
                    />
                  </div>

                  {formData.report_type === 'water' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Issue Type
                      </label>
                      <select
                        value={formData.data.issue_type || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          data: { ...formData.data, issue_type: e.target.value }
                        })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">Select issue type</option>
                        <option value="shortage">Water Shortage</option>
                        <option value="quality">Poor Water Quality</option>
                        <option value="supply">Irregular Supply</option>
                        <option value="contamination">Contamination</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  )}

                  {formData.report_type === 'electricity' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Issue Type
                      </label>
                      <select
                        value={formData.data.issue_type || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          data: { ...formData.data, issue_type: e.target.value }
                        })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">Select issue type</option>
                        <option value="powercut">Power Cut</option>
                        <option value="voltage">Voltage Fluctuation</option>
                        <option value="billing">Billing Issue</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  )}

                  {formData.report_type === 'health' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Health Concern Type
                      </label>
                      <select
                        value={formData.data.concern_type || ''}
                        onChange={(e) => setFormData({
                          ...formData,
                          data: { ...formData.data, concern_type: e.target.value }
                        })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <option value="">Select concern type</option>
                        <option value="disease">Disease Cases</option>
                        <option value="sanitation">Sanitation Issue</option>
                        <option value="facility">Health Facility Issue</option>
                        <option value="mosquito">Mosquito Breeding</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  )}
                </>
              )}

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Location Information</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      City
                    </label>
                    <input
                      type="text"
                      value={formData.city}
                      onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Your city"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      State
                    </label>
                    <input
                      type="text"
                      value={formData.state}
                      onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="Your state"
                      required
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Specific Location (Optional)
                  </label>
                  <input
                    type="text"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Area name, landmark, or address"
                  />
                </div>
              </div>

              {/* ── Photo Upload ── */}
              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-bold text-gray-900 mb-1">📸 Photo Evidence</h3>
                <p className="text-sm text-gray-500 mb-4">
                  Attach a photo to help verify your report faster (JPG, PNG, WebP · max {MAX_SIZE_MB} MB)
                </p>

                <AnimatePresence mode="wait">
                  {photoPreview ? (
                    <motion.div
                      key="preview"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.95 }}
                      className="relative rounded-xl overflow-hidden border-2 border-primary-300 shadow-md"
                    >
                      <img
                        src={photoPreview}
                        alt="Preview"
                        className="w-full max-h-72 object-cover"
                      />
                      <div className="absolute top-2 right-2 flex gap-2">
                        <button
                          type="button"
                          onClick={() => fileInputRef.current?.click()}
                          className="bg-white/90 hover:bg-white text-gray-700 rounded-full p-1.5 shadow transition"
                          title="Replace photo"
                        >
                          <Image className="w-4 h-4" />
                        </button>
                        <button
                          type="button"
                          onClick={handleRemovePhoto}
                          className="bg-red-500/90 hover:bg-red-600 text-white rounded-full p-1.5 shadow transition"
                          title="Remove photo"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      <p className="text-xs text-gray-500 px-3 py-2 bg-gray-50">
                        {photoFile?.name} &nbsp;·&nbsp; {(photoFile?.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="picker"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                    >
                      <button
                        type="button"
                        onClick={() => fileInputRef.current?.click()}
                        className="w-full border-2 border-dashed border-gray-300 hover:border-primary-400 rounded-xl p-8 flex flex-col items-center gap-3 text-gray-500 hover:text-primary-600 transition-colors cursor-pointer bg-gray-50 hover:bg-primary-50"
                      >
                        <Upload className="w-10 h-10" />
                        <span className="font-medium">Click to attach a photo</span>
                        <span className="text-xs">JPG, PNG, GIF, WebP, HEIC up to {MAX_SIZE_MB} MB</span>
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Hidden file input */}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/jpg,image/png,image/gif,image/webp,image/heic"
                  className="hidden"
                  onChange={handlePhotoChange}
                />

                {photoError && (
                  <motion.p
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-2 text-sm text-red-600 flex items-center gap-1"
                  >
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    {photoError}
                  </motion.p>
                )}
              </div>

              <div className="bg-green-50 border-2 border-green-200 rounded-xl p-4">
                <h4 className="font-bold text-green-900 mb-2">Why Your Report Matters</h4>
                <ul className="text-sm text-green-700 space-y-1">
                  <li>• Helps government identify and respond to issues faster</li>
                  <li>• Your data feeds AI predictions to prevent crises</li>
                  <li>• Multiple reports get verified automatically</li>
                  <li>• Earn reputation points for contributing</li>
                </ul>
              </div>

              {submitError && (
                <motion.div
                  initial={{ opacity: 0, y: -4 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 flex items-start gap-2 text-red-700 text-sm"
                >
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  {submitError}
                </motion.div>
              )}

              <div className="flex items-center space-x-4 pt-6">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:border-gray-400 transition"
                >
                  Back
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 py-3 gradient-saffron text-white rounded-lg font-semibold hover:shadow-lg transition disabled:opacity-50 flex items-center justify-center space-x-2"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                      </svg>
                      {photoFile ? 'Uploading & Submitting...' : 'Submitting...'}
                    </span>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      <span>Submit Report</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ReportIssue;