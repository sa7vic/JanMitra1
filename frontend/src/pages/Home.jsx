import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { ArrowRight, Shield, Users, AlertTriangle, FileText, Network } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../lib/api';
import Hero from '../components/Hero';
import StatsCounter from '../components/StatsCounter';
import NewsCard from '../components/NewsCard';
import PredictionCard from '../components/PredictionCard';
import KnowledgeGraph from '../components/KnowledgeGraph';

const Home = () => {
  const [stats, setStats] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [articles, setArticles] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    fetchHomeData();
  }, []);

  const fetchHomeData = async () => {
    try {
      const [statsRes, predictionsRes, articlesRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/api/stats`),
        axios.get(`${API_BASE_URL}/api/predictions?status=active`),
        axios.get(`${API_BASE_URL}/api/news?limit=6`)
      ]);

      setStats(statsRes.data);
      setPredictions(predictionsRes.data.predictions);
      setArticles(articlesRes.data.articles);
    } catch (error) {
      console.error('Failed to fetch home data:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Hero />

      {stats && (
        <section className="py-20 bg-gradient-to-br from-primary-50 via-white to-orange-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                Real-Time Intelligence at Scale
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Processing millions of data points to keep India safe and informed
              </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <StatsCounter
                end={stats.articles}
                label="Articles Analyzed"
                icon={FileText}
                delay={0}
              />
              <StatsCounter
                end={stats.predictions}
                label="Active Predictions"
                icon={AlertTriangle}
                delay={0.2}
              />
              <StatsCounter
                end={stats.entities}
                label="Entities Tracked"
                icon={Network}
                delay={0.4}
              />
              <StatsCounter
                end={stats.reports}
                label="Citizen Reports"
                icon={Users}
                delay={0.6}
              />
            </div>
          </div>
        </section>
      )}

      {predictions.length > 0 && (
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-12"
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-4">Active Crisis Predictions</h2>
              <p className="text-xl text-gray-600">AI-powered early warnings to prevent disasters</p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {predictions.slice(0, 3).map((prediction, index) => (
                <PredictionCard 
                  key={prediction.id} 
                  prediction={prediction} 
                  index={index}
                />
              ))}
            </div>

            <div className="text-center">
              <button
                onClick={() => navigate('/login')}
                className="inline-flex items-center space-x-2 px-8 py-4 gradient-saffron text-white rounded-lg font-bold text-lg hover:shadow-2xl transition"
              >
                <span>View All Predictions</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </section>
      )}

      {articles.length > 0 && (
        <section className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-12"
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-4">Latest Intelligence</h2>
              <p className="text-xl text-gray-600">Real-time news from 20+ trusted sources</p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles.map((article, index) => (
                <NewsCard key={article.id} article={article} index={index} />
              ))}
            </div>
          </div>
        </section>
      )}

      <section className="py-20 bg-gradient-to-br from-primary-600 to-orange-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Experience JanMitra?
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
              Join thousands of citizens and government officials using AI-powered intelligence
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
              <button
                onClick={() => navigate('/register')}
                className="px-8 py-4 bg-white text-primary-600 rounded-lg font-bold text-lg hover:shadow-2xl transition"
              >
                Get Started Free
              </button>
              <button
                onClick={() => navigate('/fact-check')}
                className="px-8 py-4 bg-white/10 backdrop-blur text-white rounded-lg font-bold text-lg hover:bg-white/20 transition"
              >
                Try Fact Checker
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="py-20 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <Shield className="w-8 h-8 text-primary-400" />
                <span className="text-2xl font-bold text-white">JanMitra</span>
              </div>
              <p className="text-gray-400">
                AI-powered crisis prediction and intelligence system for India
              </p>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white mb-4">For Citizens</h3>
              <ul className="space-y-2 text-gray-400">
                <li>• Personalized Alerts</li>
                <li>• Government Schemes</li>
                <li>• Fact Checker</li>
                <li>• Report Issues</li>
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-bold text-white mb-4">For Government</h3>
              <ul className="space-y-2 text-gray-400">
                <li>• Crisis Predictions</li>
                <li>• Citizen Intelligence</li>
                <li>• Analytics Dashboard</li>
                <li>• Response Tracking</li>
              </ul>
            </div>
          </div>

          <div className="mt-12 pt-8 border-t border-gray-800 text-center text-gray-400">
            <p>&copy; 2024 JanMitra. Built with ❤️ for India.</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;