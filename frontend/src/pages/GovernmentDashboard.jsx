import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  Calendar,
  Loader2,
  MapPin,
  Shield,
  ChevronLeft,
  ChevronRight,
  Users,
  FileText,
  Activity,
  TrendingUp,
  Flame,
  Filter,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  getGovernmentReports,
  getGovernmentReportGeoAnalytics,
  getGovernmentReportMapData,
  getNews,
  getPredictions,
  getStats,
} from '../lib/api';
import GeoIntelMap from '../components/GeoIntelMap';

const LEVEL_LABELS = {
  national: 'National',
  state: 'State',
  district: 'District',
  local: 'Local',
};

const GovernmentDashboard = () => {
  const navigate = useNavigate();

  const [reports, setReports] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [fallbackArticles, setFallbackArticles] = useState([]);
  const [stats, setStats] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 12,
    total: 0,
    pages: 0,
    has_next: false,
    has_prev: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mapLoading, setMapLoading] = useState(false);
  const [mapPoints, setMapPoints] = useState([]);
  const [mapInsights, setMapInsights] = useState(null);
  const [mapClusters, setMapClusters] = useState([]);
  const [regionGeoJson, setRegionGeoJson] = useState(null);
  const [regionAnalytics, setRegionAnalytics] = useState([]);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [mapFilters, setMapFilters] = useState({
    state: '',
    district: '',
    city: '',
    type: '',
    status: '',
    verified: 'all',
    time_range: '168',
  });
  const [bbox, setBbox] = useState('');

  const severityConfig = {
    high: {
      color: 'text-red-600',
      bg: 'bg-red-50',
      border: 'border-red-300',
      badge: 'bg-red-600',
    },
    medium: {
      color: 'text-yellow-700',
      bg: 'bg-yellow-50',
      border: 'border-yellow-300',
      badge: 'bg-yellow-600',
    },
    low: {
      color: 'text-blue-600',
      bg: 'bg-blue-50',
      border: 'border-blue-300',
      badge: 'bg-blue-600',
    },
  };

  const fetchReports = async (page = 1) => {
    try {
      const data = await getGovernmentReports({ page, per_page: pagination.per_page });
      setReports(data.reports || []);
      setViewing(data.viewing || null);
      setPagination((prev) => ({
        ...prev,
        ...(data.pagination || {}),
      }));
    } catch (err) {
      throw err;
    }
  };

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');
    try {
      const [statsData, predictionsData, reportsData, recentData, newsData] = await Promise.all([
        getStats(),
        getPredictions('active'),
        getGovernmentReports({ page: 1, per_page: pagination.per_page }),
        getGovernmentReports({ page: 1, per_page: 8, verified: true }),
        getNews(5),
      ]);

      setStats(statsData);
      setPredictions(predictionsData.predictions || []);

      setReports(reportsData.reports || []);
      setViewing(reportsData.viewing || null);
      setPagination((prev) => ({
        ...prev,
        ...(reportsData.pagination || {}),
      }));

      setRecentReports(recentData.reports || []);
      setFallbackArticles((predictionsData.predictions || []).length > 0 ? [] : (newsData.articles || []));
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to load government dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const buildMapParams = (activeBbox = bbox) => {
    const params = {
      limit: 2500,
      ...(activeBbox ? { bbox: activeBbox } : {}),
    };

    if (mapFilters.state) params.state = mapFilters.state;
    if (mapFilters.district) params.district = mapFilters.district;
    if (mapFilters.city) params.city = mapFilters.city;
    if (mapFilters.type) params.type = mapFilters.type;
    if (mapFilters.status) params.status = mapFilters.status;
    if (mapFilters.verified !== 'all') params.verified = String(mapFilters.verified === 'true');
    if (mapFilters.time_range) params.time_range = Number(mapFilters.time_range);

    return params;
  };

  const fetchMapData = async (activeBbox = bbox) => {
    setMapLoading(true);
    try {
      const params = buildMapParams(activeBbox);
      const [mapData, analyticsData] = await Promise.all([
        getGovernmentReportMapData(params),
        getGovernmentReportGeoAnalytics({
          group_by: 'region',
          state: params.state,
          district: params.district,
          city: params.city,
          type: params.type,
          status: params.status,
          verified: params.verified,
        }),
      ]);

      setMapPoints(mapData.points || []);
      setMapClusters(mapData.clusters || []);
      setRegionGeoJson(mapData.region_geojson || null);
      setMapInsights(mapData.insights || null);
      setRegionAnalytics((analyticsData.groups || []).slice(0, 8));
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to load geospatial intelligence');
    } finally {
      setMapLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchMapData(bbox);
    }, 300);

    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [bbox, mapFilters.state, mapFilters.district, mapFilters.city, mapFilters.type, mapFilters.status, mapFilters.verified, mapFilters.time_range]);

  const viewingLabel = () => {
    if (!viewing?.gov_level) return 'Viewing: Government Dashboard';

    const levelName = LEVEL_LABELS[viewing.gov_level] || viewing.gov_level;
    if (viewing.gov_level === 'national') {
      return 'Viewing: National Dashboard';
    }
    if (viewing.gov_level === 'state' && viewing.state) {
      return `Viewing: State Level (${viewing.state})`;
    }
    if (viewing.gov_level === 'district' && viewing.district) {
      return `Viewing: District Level (${viewing.district})`;
    }
    if (viewing.gov_level === 'local' && viewing.city) {
      return `Viewing: Local Level (${viewing.city})`;
    }
    return `Viewing: ${levelName} Level`;
  };

  const scopeDescription = () => {
    if (!viewing?.gov_level) return 'Operational view based on your assigned role.';
    if (viewing.gov_level === 'national') return 'Nationwide operational visibility.';
    if (viewing.gov_level === 'state' && viewing.state) return `Operational scope: ${viewing.state}.`;
    if (viewing.gov_level === 'district' && viewing.district) {
      return `Operational scope: ${viewing.district}, ${viewing.state}.`;
    }
    if (viewing.gov_level === 'local' && viewing.city) {
      return `Operational scope: ${viewing.city}, ${viewing.district}.`;
    }
    return 'Operational view based on your assigned jurisdiction.';
  };

  const categoryOptions = Object.keys(mapInsights?.category_breakdown || {}).sort();
  const statusOptions = ['pending', 'working', 'completed'];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-primary-600" />
      </div>
    );
  }

  const statCards = [
    {
      icon: AlertTriangle,
      label: 'Active Predictions',
      value: predictions.length,
      change: 'Updated in real time',
      color: 'text-red-600',
      bg: 'bg-red-50',
    },
    {
      icon: Users,
      label: 'In-Scope Reports',
      value: pagination.total,
      change: 'Jurisdiction-filtered',
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      icon: FileText,
      label: 'Total Articles',
      value: stats?.articles || 0,
      change: 'System-wide feed',
      color: 'text-green-600',
      bg: 'bg-green-50',
    },
    {
      icon: Activity,
      label: 'System Health',
      value: '98%',
      change: 'Stable',
      color: 'text-indigo-600',
      bg: 'bg-indigo-50',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="bg-gradient-to-r from-blue-700 to-indigo-600 rounded-2xl p-8 text-white shadow-2xl">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-9 h-9" />
              <h1 className="text-3xl sm:text-4xl font-bold">Government Operations Dashboard</h1>
            </div>
            <p className="text-white/90 text-lg">{viewingLabel()}</p>
            <p className="text-white/80 text-sm mt-1">{scopeDescription()}</p>
          </div>
        </motion.div>

        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-50 text-red-700 border border-red-200">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, idx) => {
            const Icon = stat.icon;
            return (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
                className="bg-white rounded-xl p-6 shadow-lg border border-gray-200"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 ${stat.bg} rounded-lg flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                </div>
                <div className="text-sm font-medium text-gray-900">{stat.label}</div>
                <div className="text-xs text-gray-600 mt-1">{stat.change}</div>
              </motion.div>
            );
          })}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-green-700 to-teal-600 p-6">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <MapPin className="w-6 h-6" />
                <span>Live Prediction Map</span>
              </h2>
              <p className="text-white/90 text-sm mt-1">Active predictions across the operational theater</p>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 mb-6">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-600 mb-1">State</label>
                  <input
                    value={mapFilters.state}
                    onChange={(e) => setMapFilters((prev) => ({ ...prev, state: e.target.value }))}
                    placeholder="e.g. Maharashtra"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-600 mb-1">District</label>
                  <input
                    value={mapFilters.district}
                    onChange={(e) => setMapFilters((prev) => ({ ...prev, district: e.target.value }))}
                    placeholder="e.g. Pune"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-600 mb-1">City</label>
                  <input
                    value={mapFilters.city}
                    onChange={(e) => setMapFilters((prev) => ({ ...prev, city: e.target.value }))}
                    placeholder="e.g. Pimpri"
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    onClick={() => setMapFilters({ state: '', district: '', city: '', type: '', status: '', verified: 'all', time_range: '168' })}
                    className="w-full py-2.5 border border-slate-300 rounded-lg text-sm font-semibold hover:bg-slate-50 transition"
                  >
                    Reset Filters
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-4 gap-4 mb-6">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-600 mb-1">Category</label>
                  <select
                    value={mapFilters.type}
                    onChange={(e) => setMapFilters((prev) => ({ ...prev, type: e.target.value }))}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">All categories</option>
                    {categoryOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-600 mb-1">Status</label>
                  <select
                    value={mapFilters.status}
                    onChange={(e) => setMapFilters((prev) => ({ ...prev, status: e.target.value }))}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="">All statuses</option>
                    {statusOptions.map((option) => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-600 mb-1">Verification</label>
                  <select
                    value={mapFilters.verified}
                    onChange={(e) => setMapFilters((prev) => ({ ...prev, verified: e.target.value }))}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="all">All</option>
                    <option value="true">Verified only</option>
                    <option value="false">Unverified only</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wide text-slate-600 mb-1">Time Range</label>
                  <select
                    value={mapFilters.time_range}
                    onChange={(e) => setMapFilters((prev) => ({ ...prev, time_range: e.target.value }))}
                    className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="24">Last 24h</option>
                    <option value="72">Last 3 days</option>
                    <option value="168">Last 7 days</option>
                    <option value="720">Last 30 days</option>
                  </select>
                </div>
                <div className="flex items-end gap-2">
                  <button
                    onClick={() => setShowHeatmap((prev) => !prev)}
                    className={`w-full py-2.5 rounded-lg text-sm font-semibold border transition flex items-center justify-center gap-2 ${
                      showHeatmap
                        ? 'bg-orange-600 text-white border-orange-600'
                        : 'bg-white text-slate-700 border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <Flame className="w-4 h-4" />
                    {showHeatmap ? 'Heatmap On' : 'Heatmap Off'}
                  </button>
                </div>
              </div>

              <GeoIntelMap
                points={mapPoints}
                clusters={mapClusters}
                regionGeoJson={regionGeoJson}
                loading={mapLoading}
                showHeatmap={showHeatmap}
                onBoundsChange={setBbox}
                onReportClick={(point) => navigate(`/reports/${point.id}`)}
              />

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-6">
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
                  <div className="flex items-center gap-2 text-slate-700 mb-2">
                    <Filter className="w-4 h-4" />
                    <span className="font-semibold text-sm">Map Scope</span>
                  </div>
                  <div className="text-2xl font-bold text-slate-900">{mapInsights?.total_points || 0}</div>
                  <p className="text-xs text-slate-600 mt-1">points in current viewport + filters</p>
                </div>

                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 lg:col-span-2">
                  <div className="font-semibold text-sm text-slate-700 mb-2">Top Region Hotspots</div>
                  {(regionAnalytics || []).length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {regionAnalytics.map((row) => (
                        <div key={row.group} className="flex items-center justify-between text-sm bg-white border border-slate-200 rounded-lg px-3 py-2">
                          <span className="text-slate-700 truncate pr-2">{row.group}</span>
                          <span className="font-bold text-slate-900">{row.count}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-600">No region insights available for current filter selection.</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
                <div className="bg-red-50 border border-red-200 rounded-xl p-4">
                  <div className="font-semibold text-sm text-red-800 mb-2">Top 3 Hotspots</div>
                  {(mapInsights?.top_hotspots || []).length > 0 ? (
                    <div className="space-y-2">
                      {(mapInsights.top_hotspots || []).slice(0, 3).map((hotspot, idx) => (
                        <div key={`${hotspot.cluster_id || hotspot.region || idx}`} className="text-sm bg-white border border-red-100 rounded-lg px-3 py-2">
                          <div className="font-semibold text-slate-800">#{idx + 1} {hotspot.type === 'cluster' ? `Cluster ${hotspot.cluster_id}` : hotspot.region}</div>
                          <div className="text-slate-600">{hotspot.insight || `${hotspot.count} incidents`}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-600">No hotspot patterns found for current filters.</p>
                  )}
                  <p className="text-xs text-red-700 mt-2">Insight: these are highest concentration zones for immediate intervention.</p>
                </div>

                <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
                  <div className="font-semibold text-sm text-emerald-800 mb-2">Least Active Regions</div>
                  {(mapInsights?.least_active_regions || []).length > 0 ? (
                    <div className="space-y-2">
                      {(mapInsights.least_active_regions || []).slice(0, 3).map((row) => (
                        <div key={row.region} className="flex items-center justify-between text-sm bg-white border border-emerald-100 rounded-lg px-3 py-2">
                          <span className="text-slate-700">{row.region}</span>
                          <span className="font-semibold text-slate-900">{row.count}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-600">No low-activity regions available.</p>
                  )}
                  <p className="text-xs text-emerald-700 mt-2">Insight: low-activity zones can indicate stable conditions or underreporting.</p>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                  <div className="font-semibold text-sm text-amber-800 mb-2">Sudden Spikes</div>
                  {(mapInsights?.anomalies || []).length > 0 ? (
                    <div className="space-y-2">
                      {(mapInsights.anomalies || []).slice(0, 3).map((row) => (
                        <div key={row.region} className="text-sm bg-white border border-amber-100 rounded-lg px-3 py-2">
                          <div className="font-semibold text-slate-800">{row.region}</div>
                          <div className="text-slate-600">24h: {row.recent_24h} vs prev: {row.previous_24h} ({row.growth_ratio}x)</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-slate-600">No statistically notable spikes in selected window.</p>
                  )}
                  <p className="text-xs text-amber-700 mt-2">Insight: rapid increases may indicate emerging local crises.</p>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.28 }}
              className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
            >
              <div className="bg-gradient-to-r from-red-700 to-orange-600 p-6">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                  <AlertTriangle className="w-6 h-6" />
                  <span>Active Crisis Predictions</span>
                </h2>
              </div>
              <div className="p-6">
                {predictions.length > 0 ? (
                  <div className="space-y-4">
                    {predictions.slice(0, 5).map((prediction, idx) => {
                      const config = severityConfig[prediction.severity] || severityConfig.low;
                      return (
                        <motion.button
                          key={prediction.id}
                          initial={{ opacity: 0, x: -12 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.06 }}
                          className={`w-full text-left ${config.bg} border ${config.border} rounded-xl p-5 hover:shadow-lg transition`}
                          onClick={() => navigate(`/government/prediction/${prediction.id}`)}
                        >
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <div className="flex items-center gap-3 mb-2">
                                <span className={`px-3 py-1 ${config.badge} text-white rounded-full text-xs font-bold uppercase`}>
                                  {prediction.severity}
                                </span>
                                <span className="text-sm text-gray-600">
                                  {Math.round((prediction.confidence || 0) * 100)}% confidence
                                </span>
                              </div>
                              <h3 className={`text-lg font-bold ${config.color} mb-1`}>{prediction.title}</h3>
                              <p className="text-sm text-gray-700 line-clamp-2 mb-2">{prediction.description}</p>
                              <div className="text-xs text-gray-600 flex items-center gap-3">
                                <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" />{prediction.location}</span>
                                {prediction.predicted_date && (
                                  <span>Expected: {new Date(prediction.predicted_date).toLocaleDateString()}</span>
                                )}
                              </div>
                            </div>
                            <TrendingUp className={`w-5 h-5 ${config.color} mt-1`} />
                          </div>
                        </motion.button>
                      );
                    })}
                  </div>
                ) : fallbackArticles.length > 0 ? (
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600">
                      No active prediction event yet. Showing latest fetched articles.
                    </p>
                    {fallbackArticles.map((article) => (
                      <a
                        key={article.id}
                        href={article.url}
                        target="_blank"
                        rel="noreferrer"
                        className="block p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition"
                      >
                        <h3 className="text-sm font-semibold text-gray-900 line-clamp-2">{article.title}</h3>
                        <div className="text-xs text-gray-600 mt-2 flex items-center justify-between gap-2">
                          <span>{article.source || 'Unknown source'}</span>
                          <span>{article.published_at ? new Date(article.published_at).toLocaleDateString() : '-'}</span>
                        </div>
                      </a>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-10 text-gray-600">No active predictions at this time.</div>
                )}
              </div>
            </motion.div>
          </div>

          <div className="space-y-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.36 }}
              className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
            >
              <div className="bg-gradient-to-r from-blue-700 to-indigo-700 p-6">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  <span>Citizen Intel (Verified)</span>
                </h2>
              </div>
              <div className="p-6">
                {recentReports.length > 0 ? (
                  <div className="space-y-3">
                    {recentReports.map((report) => (
                      <div key={report.id} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="font-semibold text-gray-900 text-sm mb-1">{report.title || report.report_type}</div>
                        <div className="text-xs text-gray-600 flex items-center gap-2">
                          <MapPin className="w-3 h-3" />
                          <span>{[report.city, report.district, report.state].filter(Boolean).join(', ')}</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">{new Date(report.created_at).toLocaleString()}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-sm text-gray-600">No recent in-scope reports.</div>
                )}

                <button
                  onClick={() => navigate('/government/reports')}
                  className="w-full mt-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:border-gray-400 transition text-sm"
                >
                  View All Reports
                </button>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.44 }}
              className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-6 text-white shadow-lg"
            >
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={() => navigate('/government/predictions')}
                  className="w-full py-3 bg-white/15 hover:bg-white/25 rounded-lg font-semibold transition text-left px-4"
                >
                  View All Predictions
                </button>
                <button
                  onClick={() => navigate('/government/reports')}
                  className="w-full py-3 bg-white/15 hover:bg-white/25 rounded-lg font-semibold transition text-left px-4"
                >
                  Reports Dashboard
                </button>
                <button
                  onClick={() => navigate('/government/analytics')}
                  className="w-full py-3 bg-white/15 hover:bg-white/25 rounded-lg font-semibold transition text-left px-4"
                >
                  Analytics and Insights
                </button>
              </div>
            </motion.div>
          </div>
        </div>

        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-white text-lg font-semibold">Jurisdiction Reports</h2>
          <div className="text-sm text-gray-200">
            Showing {reports.length} of {pagination.total} reports
          </div>
        </div>

        {reports.length === 0 ? (
          <div className="bg-white rounded-xl p-10 text-center border border-gray-200">
            <AlertTriangle className="w-12 h-12 mx-auto text-gray-400 mb-3" />
            <h2 className="text-xl font-bold text-gray-900 mb-1">No Reports In Scope</h2>
            <p className="text-gray-600">No citizen reports match your current jurisdiction.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {reports.map((report, idx) => (
              <motion.button
                key={report.id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.04 }}
                onClick={() => navigate(`/reports/${report.id}`)}
                className="w-full text-left bg-white rounded-xl p-5 border border-gray-200 shadow-sm hover:shadow-lg transition"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-700 capitalize">
                    {report.report_type || 'issue'}
                  </span>
                  <span
                    className={`px-2.5 py-1 text-xs font-semibold rounded-full ${
                      report.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : report.status === 'working'
                        ? 'bg-blue-100 text-blue-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {report.status === 'completed' ? '🟢 Completed' : report.status === 'working' ? '🔵 Working' : '🟡 Pending'}
                  </span>
                </div>

                <h3 className="font-bold text-gray-900 mb-2 line-clamp-2">
                  {report.title || 'Citizen Report'}
                </h3>
                {report.description && (
                  <p className="text-sm text-gray-600 mb-3 line-clamp-3">{report.description}</p>
                )}

                <div className="flex flex-wrap gap-2 mb-3">
                  {report.state && (
                    <span className="text-xs px-2 py-1 rounded bg-slate-100 text-slate-700">{report.state}</span>
                  )}
                  {report.district && (
                    <span className="text-xs px-2 py-1 rounded bg-slate-100 text-slate-700">{report.district}</span>
                  )}
                  {report.city && (
                    <span className="text-xs px-2 py-1 rounded bg-slate-100 text-slate-700">{report.city}</span>
                  )}
                </div>

                <div className="text-xs text-gray-500 space-y-1 border-t border-gray-100 pt-3">
                  <div className="flex items-center gap-2">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{report.location || 'Location not specified'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="w-3.5 h-3.5" />
                    <span>
                      Assigned to: {report.assigned_to_name ? `${report.assigned_to_name}${report.district ? ` - ${report.district}` : ''}` : 'Unassigned'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-3.5 h-3.5" />
                    <span>{new Date(report.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </motion.button>
            ))}
          </div>
        )}

        <div className="mt-8 flex items-center justify-end gap-2">
          <button
            onClick={async () => {
              setLoading(true);
              setError('');
              try {
                await fetchReports(pagination.page - 1);
              } catch (err) {
                setError(err.response?.data?.error || 'Unable to load government reports');
              } finally {
                setLoading(false);
              }
            }}
            disabled={!pagination.has_prev}
            className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium bg-white border border-gray-200 disabled:opacity-50"
          >
            <ChevronLeft className="w-4 h-4" />
            Prev
          </button>
          <span className="px-3 py-2 text-sm text-gray-100">
            Page {pagination.page} of {Math.max(pagination.pages, 1)}
          </span>
          <button
            onClick={async () => {
              setLoading(true);
              setError('');
              try {
                await fetchReports(pagination.page + 1);
              } catch (err) {
                setError(err.response?.data?.error || 'Unable to load government reports');
              } finally {
                setLoading(false);
              }
            }}
            disabled={!pagination.has_next}
            className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium bg-white border border-gray-200 disabled:opacity-50"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default GovernmentDashboard;
