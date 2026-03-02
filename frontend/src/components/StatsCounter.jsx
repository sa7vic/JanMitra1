import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

const StatsCounter = ({ end, duration = 2, label, icon: Icon, delay = 0 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let startTime;
    let animationFrame;

    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      
      setCount(Math.floor(progress * end));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    const timer = setTimeout(() => {
      animationFrame = requestAnimationFrame(animate);
    }, delay * 1000);

    return () => {
      clearTimeout(timer);
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [end, duration, delay]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay }}
      className="text-center"
    >
      {Icon && (
        <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon className="w-8 h-8 text-primary-600" />
        </div>
      )}
      <motion.div
        className="text-5xl md:text-6xl font-bold text-gradient mb-2"
        initial={{ scale: 0.5 }}
        animate={{ scale: 1 }}
        transition={{ delay: delay + 0.2, type: "spring", stiffness: 200 }}
      >
        {count.toLocaleString()}
        {end >= 1000000 ? 'M+' : end >= 1000 ? 'K+' : '+'}
      </motion.div>
      <div className="text-gray-600 text-lg font-medium">{label}</div>
    </motion.div>
  );
};

export default StatsCounter;