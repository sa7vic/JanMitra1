import { motion } from 'framer-motion';
import { ArrowRight, Zap, Shield, Globe, MessageCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const Hero = () => {
  const whatsappNumber = '14155238886';
  const joinCode = 'join rod-choose';
  
  const features = [
    { icon: Zap, text: 'Real-time Intelligence' },
    { icon: Shield, text: 'Fact Verification' },
    { icon: Globe, text: 'National Coverage' },
  ];

  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-primary-50 via-white to-primary-50 pt-32 pb-20">
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center"
        >
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring' }}
            className="inline-block mb-6"
          >
            <div className="w-3 h-3 bg-saffron rounded-full inline-block"></div>
            <div className="w-3 h-3 bg-white border-2 border-gray-300 rounded-full inline-block mx-2"></div>
            <div className="w-3 h-3 bg-green rounded-full inline-block"></div>
          </motion.div>

          <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
            India's Intelligence
            <br />
            <span className="text-gradient">Operating System</span>
          </h1>

          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Real-time intelligence that predicts crises, verifies facts, and connects every Indian to governance data. Powered by AI.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              to="/dashboard"
              className="px-8 py-4 gradient-saffron text-white rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-1 transition-all flex items-center justify-center"
            >
              Explore Dashboard
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            
            <a
              href="#features"
              className="px-8 py-4 bg-white text-primary-600 border-2 border-primary-600 rounded-lg font-semibold hover:bg-primary-50 transition-all"
            >
              Learn More
            </a>

            <motion.button
              onClick={() => {
                const encodedMessage = encodeURIComponent(joinCode);
                window.open(`https://wa.me/${whatsappNumber}?text=${encodedMessage}`, '_blank');
              }}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              style={{
                backgroundColor: '#16a34a',
                color: '#ffffff',
                border: 'none'
              }}
              className="px-8 py-4 rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-1 transition-all flex items-center justify-center space-x-2 group cursor-pointer"
              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#15803d'}
              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#16a34a'}
            >
              <MessageCircle style={{ color: 'white' }} className="w-5 h-5 group-hover:scale-110 transition-transform" />
              <span style={{ color: 'white' }}>Chat on WhatsApp</span>
              <span style={{ backgroundColor: 'white', color: '#16a34a' }} className="text-xs px-2 py-1 rounded-full font-bold">NEW</span>
            </motion.button>
          </div>

          <div className="flex flex-wrap justify-center gap-8 mt-16">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 + index * 0.1 }}
                  className="flex items-center space-x-2 text-gray-700"
                >
                  <Icon className="w-5 h-5 text-primary-600" />
                  <span className="font-medium">{feature.text}</span>
                </motion.div>
              );
            })}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Hero;