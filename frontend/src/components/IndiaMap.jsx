import { motion } from 'framer-motion';
import { MapPin } from 'lucide-react';

const IndiaMap = () => {
  const states = [
    { name: 'Delhi', x: 45, y: 30, status: 'high' },
    { name: 'Mumbai', x: 35, y: 50, status: 'medium' },
    { name: 'Bangalore', x: 40, y: 75, status: 'low' },
    { name: 'Chennai', x: 50, y: 80, status: 'medium' },
    { name: 'Kolkata', x: 70, y: 45, status: 'high' },
  ];

  const statusColors = {
    high: 'bg-red-500',
    medium: 'bg-yellow-500',
    low: 'bg-green-500',
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <h3 className="text-xl font-bold text-gray-900 mb-4">Live India Map</h3>
      
      <div className="relative w-full h-[500px] bg-gradient-to-br from-blue-50 to-green-50 rounded-lg overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative w-[80%] h-[80%]">
            {states.map((state, index) => (
              <motion.div
                key={state.name}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: index * 0.1 }}
                className="absolute"
                style={{ left: `${state.x}%`, top: `${state.y}%` }}
              >
                <div className="relative group">
                  <div className={`w-4 h-4 ${statusColors[state.status]} rounded-full animate-pulse cursor-pointer`}></div>
                  <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    {state.name}
                    <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg p-3 space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-xs text-gray-700">High Alert</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <span className="text-xs text-gray-700">Medium</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-xs text-gray-700">Normal</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndiaMap;