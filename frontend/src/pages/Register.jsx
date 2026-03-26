import { useEffect, useMemo, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import {
  UserPlus,
  User,
  Mail,
  Lock,
  Shield,
  Building2,
  MapPin,
  Phone,
  Briefcase,
  BadgeCheck,
  Loader2,
} from 'lucide-react';
import { getCities, getDistricts, getStates } from '../lib/api';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    official_email: '',
    password: '',
    phone: '',
    role: 'citizen',
    department: '',
    designation: '',
    gov_level: '',
    state: '',
    district: '',
    city: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [locationLoading, setLocationLoading] = useState({
    states: false,
    districts: false,
    cities: false,
  });
  const [locationData, setLocationData] = useState({
    states: [],
    districts: [],
    cities: [],
  });
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const isGovernment = formData.role === 'government';

  const requiresState = useMemo(() => {
    if (!isGovernment) return true;
    return ['state', 'district', 'local'].includes(formData.gov_level);
  }, [isGovernment, formData.gov_level]);

  const requiresDistrict = useMemo(() => {
    if (!isGovernment) return true;
    return ['district', 'local'].includes(formData.gov_level);
  }, [isGovernment, formData.gov_level]);

  const requiresCity = useMemo(() => {
    if (!isGovernment) return true;
    return formData.gov_level === 'local';
  }, [isGovernment, formData.gov_level]);

  useEffect(() => {
    const loadStates = async () => {
      setLocationLoading((prev) => ({ ...prev, states: true }));
      try {
        const states = await getStates();
        setLocationData((prev) => ({ ...prev, states }));
      } finally {
        setLocationLoading((prev) => ({ ...prev, states: false }));
      }
    };

    loadStates();
  }, []);

  useEffect(() => {
    const loadDistricts = async () => {
      if (!formData.state || !requiresDistrict) {
        setLocationData((prev) => ({ ...prev, districts: [], cities: [] }));
        return;
      }

      setLocationLoading((prev) => ({ ...prev, districts: true }));
      try {
        const districts = await getDistricts(formData.state);
        setLocationData((prev) => ({ ...prev, districts }));
      } finally {
        setLocationLoading((prev) => ({ ...prev, districts: false }));
      }
    };

    loadDistricts();
  }, [formData.state, requiresDistrict]);

  useEffect(() => {
    const loadCities = async () => {
      if (!formData.state || !formData.district || !requiresCity) {
        setLocationData((prev) => ({ ...prev, cities: [] }));
        return;
      }

      setLocationLoading((prev) => ({ ...prev, cities: true }));
      try {
        const cities = await getCities(formData.state, formData.district);
        setLocationData((prev) => ({ ...prev, cities }));
      } finally {
        setLocationLoading((prev) => ({ ...prev, cities: false }));
      }
    };

    loadCities();
  }, [formData.state, formData.district, requiresCity]);

  const updateField = (field, value) => {
    setFormData((prev) => {
      const next = { ...prev, [field]: value };

      if (field === 'role' && value !== 'government') {
        next.gov_level = '';
        next.department = '';
        next.designation = '';
        next.official_email = '';
        next.state = '';
        next.district = '';
        next.city = '';
      }

      if (field === 'gov_level') {
        if (value === 'national') {
          next.state = '';
          next.district = '';
          next.city = '';
        } else if (value === 'state') {
          next.district = '';
          next.city = '';
        } else if (value === 'district') {
          next.city = '';
        }
      }

      if (field === 'state') {
        next.district = '';
        next.city = '';
      }

      if (field === 'district') {
        next.city = '';
      }

      return next;
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (isGovernment) {
      if (!formData.official_email.trim()) {
        setError('Official email is required for government users.');
        setLoading(false);
        return;
      }
      if (!formData.department.trim() || !formData.designation.trim()) {
        setError('Department and designation are required for government users.');
        setLoading(false);
        return;
      }
      if (!formData.gov_level) {
        setError('Please select a government level.');
        setLoading(false);
        return;
      }
      if (requiresState && !formData.state.trim()) {
        setError('State is required for this government level.');
        setLoading(false);
        return;
      }
      if (requiresDistrict && !formData.district.trim()) {
        setError('District is required for this government level.');
        setLoading(false);
        return;
      }
      if (requiresCity && !formData.city.trim()) {
        setError('City/local area is required for local government level.');
        setLoading(false);
        return;
      }
    } else if (!formData.state || !formData.district || !formData.city) {
      setError('State, district, and city are required for citizen registration.');
      setLoading(false);
      return;
    }

    try {
      const extra = isGovernment
        ? {
            official_email: formData.official_email,
            department: formData.department,
            designation: formData.designation,
            gov_level: formData.gov_level,
            state: formData.state,
            district: formData.district,
            city: formData.city,
          }
        : {
            state: formData.state,
            district: formData.district,
            city: formData.city,
          };

      const authEmail = isGovernment ? formData.official_email : formData.email;

      const userData = await register(
        authEmail,
        formData.password,
        formData.name,
        formData.role,
        extra
      );
      
      if (userData.role === 'government' || userData.role === 'gov') {
        navigate('/government/dashboard');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-50 py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full"
      >
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold text-gradient mb-2">Join JanMitra</h2>
          <p className="text-gray-600">Structured onboarding for citizens and government officials</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => updateField('name', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Your name"
                  required
                />
              </div>
            </div>

            {!isGovernment && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => updateField('email', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="citizen@example.com"
                    required={!isGovernment}
                  />
                </div>
              </div>
            )}

            {isGovernment && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Official Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    type="email"
                    value={formData.official_email}
                    onChange={(e) => updateField('official_email', e.target.value)}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="officer@maharashtra.gov.in"
                    required={isGovernment}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Use a department/organization domain for official access.</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => updateField('phone', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="+91xxxxxxxxxx"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => updateField('password', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="••••••••"
                  required
                  minLength={6}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Account Type
              </label>
              <div className="relative">
                <Shield className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <select
                  value={formData.role}
                  onChange={(e) => updateField('role', e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                >
                  <option value="citizen">Citizen</option>
                  <option value="government">Government</option>
                </select>
              </div>
            </div>

            {isGovernment && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      value={formData.department}
                      onChange={(e) => updateField('department', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="e.g. Water, Roads, Sanitation"
                      required={isGovernment}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Designation</label>
                  <div className="relative">
                    <BadgeCheck className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      value={formData.designation}
                      onChange={(e) => updateField('designation', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="e.g. District Collector"
                      required={isGovernment}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Government Level
                  </label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select
                      value={formData.gov_level}
                      onChange={(e) => updateField('gov_level', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                      required
                    >
                      <option value="">Select level</option>
                      <option value="national">National</option>
                      <option value="state">State</option>
                      <option value="district">District</option>
                      <option value="local">Local</option>
                    </select>
                  </div>
                </div>

                {requiresState && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <select
                        value={formData.state}
                        onChange={(e) => updateField('state', e.target.value)}
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                        disabled={locationLoading.states}
                        required={requiresState}
                      >
                        <option value="">Select State</option>
                        {locationData.states.map((state) => (
                          <option key={state} value={state}>{state}</option>
                        ))}
                      </select>
                      {locationLoading.states && <Loader2 className="absolute right-3 top-3.5 w-5 h-5 animate-spin text-gray-400" />}
                    </div>
                  </div>
                )}

                {requiresDistrict && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">District</label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <select
                        value={formData.district}
                        onChange={(e) => updateField('district', e.target.value)}
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                        disabled={!formData.state || locationLoading.districts}
                        required={requiresDistrict}
                      >
                        <option value="">Select District</option>
                        {locationData.districts.map((district) => (
                          <option key={district} value={district}>{district}</option>
                        ))}
                      </select>
                      {locationLoading.districts && <Loader2 className="absolute right-3 top-3.5 w-5 h-5 animate-spin text-gray-400" />}
                    </div>
                  </div>
                )}

                {requiresCity && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">City / Local Area</label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                      <select
                        value={formData.city}
                        onChange={(e) => updateField('city', e.target.value)}
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                        disabled={!formData.district || locationLoading.cities}
                        required={requiresCity}
                      >
                        <option value="">Select City</option>
                        {locationData.cities.map((city) => (
                          <option key={city} value={city}>{city}</option>
                        ))}
                      </select>
                      {locationLoading.cities && <Loader2 className="absolute right-3 top-3.5 w-5 h-5 animate-spin text-gray-400" />}
                    </div>
                  </div>
                )}
              </>
            )}

            {!isGovernment && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">State</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select
                      value={formData.state}
                      onChange={(e) => updateField('state', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                      disabled={locationLoading.states}
                      required
                    >
                      <option value="">Select State</option>
                      {locationData.states.map((state) => (
                        <option key={state} value={state}>{state}</option>
                      ))}
                    </select>
                    {locationLoading.states && <Loader2 className="absolute right-3 top-3.5 w-5 h-5 animate-spin text-gray-400" />}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">District</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select
                      value={formData.district}
                      onChange={(e) => updateField('district', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                      disabled={!formData.state || locationLoading.districts}
                      required
                    >
                      <option value="">Select District</option>
                      {locationData.districts.map((district) => (
                        <option key={district} value={district}>{district}</option>
                      ))}
                    </select>
                    {locationLoading.districts && <Loader2 className="absolute right-3 top-3.5 w-5 h-5 animate-spin text-gray-400" />}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">City</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select
                      value={formData.city}
                      onChange={(e) => updateField('city', e.target.value)}
                      className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white"
                      disabled={!formData.district || locationLoading.cities}
                      required
                    >
                      <option value="">Select City</option>
                      {locationData.cities.map((city) => (
                        <option key={city} value={city}>{city}</option>
                      ))}
                    </select>
                    {locationLoading.cities && <Loader2 className="absolute right-3 top-3.5 w-5 h-5 animate-spin text-gray-400" />}
                  </div>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 gradient-saffron text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? 'Creating account...' : (
                <>
                  <UserPlus className="w-5 h-5 mr-2" />
                  Create Account
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 font-semibold hover:text-primary-700">
                Sign In
              </Link>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;