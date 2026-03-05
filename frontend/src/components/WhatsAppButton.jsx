import { motion } from 'framer-motion';
import { MessageCircle, X } from 'lucide-react';
import { useState } from 'react';

const WhatsAppButton = () => {
  const [showTooltip, setShowTooltip] = useState(false);
  const [showModal, setShowModal] = useState(false);
  
  // Twilio WhatsApp Sandbox number (update this with your actual number)
  const whatsappNumber = '14155238886'; // Twilio sandbox default
  const joinCode = 'join rod-choose'; // Update with your actual join code from Twilio console
  
  const openWhatsApp = () => {
    // For Twilio sandbox, users need to join first
    // Show modal with instructions
    setShowModal(true);
  };

  const directWhatsApp = () => {
    // Direct link to WhatsApp
    const encodedMessage = encodeURIComponent(joinCode);
    window.open(`https://wa.me/${whatsappNumber}?text=${encodedMessage}`, '_blank');
    setShowModal(false);
  };

  return (
    <>
      {/* Floating WhatsApp Button */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 1, type: 'spring' }}
        className="fixed bottom-6 left-6 z-[60]"
      >
        <div className="relative">
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={openWhatsApp}
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            style={{ backgroundColor: '#22c55e', color: 'white' }}
            className="w-16 h-16 hover:!bg-green-600 text-white rounded-full shadow-2xl flex items-center justify-center transition-all border-2 border-green-400"
            aria-label="Chat on WhatsApp"
          >
            <MessageCircle className="w-8 h-8 text-white" strokeWidth={2} />
          </motion.button>

          {/* Tooltip */}
          {showTooltip && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="absolute left-full ml-3 top-1/2 -translate-y-1/2 bg-gray-900 text-white px-4 py-2 rounded-lg whitespace-nowrap text-sm font-medium shadow-lg"
            >
              Chat with JanMitra AI on WhatsApp
              <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-2 w-0 h-0 border-t-8 border-b-8 border-r-8 border-transparent border-r-gray-900"></div>
            </motion.div>
          )}
        </div>
      </motion.div>

      {/* Instructions Modal */}
      {showModal && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/50 z-[70] flex items-center justify-center p-4"
          onClick={() => setShowModal(false)}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="bg-white rounded-2xl max-w-md w-full p-6 relative"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MessageCircle className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                Chat with JanMitra AI
              </h3>
              <p className="text-gray-600">
                Get instant answers via WhatsApp
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <h4 className="font-semibold text-blue-900 mb-2">
                📱 Quick Start
              </h4>
              <p className="text-sm text-blue-800 mb-3">
                Click the button below to open WhatsApp with a pre-filled join message. Just send it to start chatting!
              </p>
              <div className="bg-white rounded p-3 text-xs text-gray-600">
                <strong>First time?</strong> Send the pre-filled message to join, then you can ask anything!
              </div>
            </div>

            <div className="space-y-3">
              <button
                onClick={directWhatsApp}
                className="w-full px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Open WhatsApp</span>
              </button>

              <button
                onClick={() => {
                  navigator.clipboard.writeText(`+${whatsappNumber}`);
                  alert('Number copied to clipboard!');
                }}
                className="w-full px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
              >
                Copy Number
              </button>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-2">💬 What you can ask:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Government schemes & eligibility</li>
                <li>• Latest news & policies</li>
                <li>• Fact checking</li>
                <li>• Price information</li>
                <li>• Report civic issues</li>
              </ul>
            </div>
          </motion.div>
        </motion.div>
      )}
    </>
  );
};

export default WhatsAppButton;
