import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Send, Loader2, Bot, User, Home, Sparkles } from 'lucide-react';
import { askQuestion } from '../lib/api';

const ChatInterface = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: 'bot',
      text: '👋 **Welcome to JanMitra Intelligence**\n\nSelect a capability to get started:',
      options: [
        { 
          icon: '🎯', 
          label: 'Crisis Predictions', 
          desc: 'AI-powered early warnings',
          action: 'predictions',
          gradient: 'from-red-50 to-red-100 border-red-300 hover:border-red-400 text-red-900'
        },
        { 
          icon: '✓', 
          label: 'Fact Check', 
          desc: 'Verify claims instantly',
          action: 'fact_check',
          gradient: 'from-green-50 to-green-100 border-green-300 hover:border-green-400 text-green-900'
        },
        { 
          icon: '📊', 
          label: 'Economic Analysis', 
          desc: 'Track indicators & trends',
          action: 'economy',
          gradient: 'from-blue-50 to-blue-100 border-blue-300 hover:border-blue-400 text-blue-900'
        },
        { 
          icon: '🗺️', 
          label: 'Regional Intel', 
          desc: 'Geographic hotspots',
          action: 'geo',
          gradient: 'from-purple-50 to-purple-100 border-purple-300 hover:border-purple-400 text-purple-900'
        },
        { 
          icon: '💬', 
          label: 'Ask Anything', 
          desc: 'Open conversation mode',
          action: 'open',
          gradient: 'from-indigo-50 to-indigo-100 border-indigo-300 hover:border-indigo-400 text-indigo-900'
        },
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (type, text, options = null) => {
    setMessages(prev => [...prev, { type, text, options, timestamp: new Date() }]);
  };

  const resetToMenu = () => {
    setMode(null);
    addMessage('bot', '🏠 **Main Menu**\n\nSelect a capability:', [
      { icon: '🎯', label: 'Crisis Predictions', desc: 'AI-powered early warnings', action: 'predictions', gradient: 'from-red-50 to-red-100 border-red-300 hover:border-red-400 text-red-900' },
      { icon: '✓', label: 'Fact Check', desc: 'Verify claims instantly', action: 'fact_check', gradient: 'from-green-50 to-green-100 border-green-300 hover:border-green-400 text-green-900' },
      { icon: '📊', label: 'Economic Analysis', desc: 'Track indicators & trends', action: 'economy', gradient: 'from-blue-50 to-blue-100 border-blue-300 hover:border-blue-400 text-blue-900' },
      { icon: '🗺️', label: 'Regional Intel', desc: 'Geographic hotspots', action: 'geo', gradient: 'from-purple-50 to-purple-100 border-purple-300 hover:border-purple-400 text-purple-900' },
      { icon: '💬', label: 'Ask Anything', desc: 'Open conversation', action: 'open', gradient: 'from-indigo-50 to-indigo-100 border-indigo-300 hover:border-indigo-400 text-indigo-900' },
    ]);
  };

  const handleOptionClick = async (action) => {
    if (action === 'predictions') {
      setMode('predictions');
      addMessage('user', '🎯 Show crisis predictions');
      setLoading(true);
      try {
        const response = await askQuestion('What are the current active crisis predictions for India with confidence scores and key evidence?');
        addMessage('bot', response.answer);
      } catch (error) {
        addMessage('bot', '❌ Failed to fetch predictions. Please try again.');
      } finally {
        setLoading(false);
      }
    } else if (action === 'fact_check') {
      setMode('fact_check');
      addMessage('bot', '✓ **Fact Check Mode Active**\n\nSend me any claim and I\'ll verify it against verified sources.\n\n**Example:** "Petrol prices increased by 50% in 2024"');
    } else if (action === 'economy') {
      setMode('economy');
      addMessage('user', '📊 Economic analysis');
      setLoading(true);
      try {
        const response = await askQuestion('Analyze current economic situation in India: inflation trends, commodity prices, and key indicators');
        addMessage('bot', response.answer);
      } catch (error) {
        addMessage('bot', '❌ Economic analysis unavailable.');
      } finally {
        setLoading(false);
      }
    } else if (action === 'geo') {
      setMode('geo');
      addMessage('user', '🗺️ Regional intelligence');
      setLoading(true);
      try {
        const response = await askQuestion('What are the major regional trends and hotspots across Indian states?');
        addMessage('bot', response.answer);
      } catch (error) {
        addMessage('bot', '❌ Regional data unavailable.');
      } finally {
        setLoading(false);
      }
    } else if (action === 'open') {
      setMode('open');
      addMessage('bot', '💬 **Open Conversation**\n\nAsk me anything about India - I can help with questions about economy, politics, health, agriculture, technology, and more!');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    addMessage('user', userMessage);
    setInput('');
    setLoading(true);

    try {
      let prefix = '';
      if (mode === 'fact_check') {
        prefix = 'Fact check this claim with sources: ';
      }

      const response = await askQuestion(prefix + userMessage);
      addMessage('bot', response.answer);
    } catch (error) {
      addMessage('bot', '❌ Failed to get response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const modeConfig = {
    predictions: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-900', icon: '🎯', label: 'Crisis Predictions' },
    fact_check: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-900', icon: '✓', label: 'Fact Check' },
    economy: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-900', icon: '📊', label: 'Economic Analysis' },
    geo: { bg: 'bg-purple-50', border: 'border-purple-200', text: 'text-purple-900', icon: '🗺️', label: 'Regional Intel' },
    open: { bg: 'bg-indigo-50', border: 'border-indigo-200', text: 'text-indigo-900', icon: '💬', label: 'Open Conversation' },
  };

  const currentMode = mode ? modeConfig[mode] : null;

  return (
    <>
      {/* Floating Button */}
      <motion.button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 w-16 h-16 gradient-saffron rounded-full shadow-2xl flex items-center justify-center z-50 ${isOpen ? 'hidden' : ''}`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
      >
        <MessageCircle className="w-8 h-8 text-white" />
        <span className="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full text-white text-xs flex items-center justify-center font-bold animate-pulse">
          AI
        </span>
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            className="fixed bottom-6 right-6 w-[450px] h-[650px] bg-white rounded-2xl shadow-2xl z-50 flex flex-col overflow-hidden border-2 border-gray-200"
          >
            {/* Header */}
            <div className="gradient-saffron p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur">
                    <Sparkles className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">JanMitra AI</h3>
                    <p className="text-xs text-white/90">Intelligence Assistant</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:bg-white/20 rounded-lg p-2 transition"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Mode Indicator with Home Button */}
              {currentMode && (
                <div className={`${currentMode.bg} ${currentMode.border} border-2 rounded-lg px-3 py-2 flex items-center justify-between`}>
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{currentMode.icon}</span>
                    <span className={`${currentMode.text} font-semibold text-sm`}>
                      {currentMode.label}
                    </span>
                  </div>
                  <button
                    onClick={resetToMenu}
                    className={`${currentMode.text} hover:opacity-70 transition flex items-center space-x-1 text-xs font-semibold`}
                  >
                    <Home className="w-4 h-4" />
                    <span>Menu</span>
                  </button>
                </div>
              )}
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[85%] ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    {/* Avatar */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user' ? 'bg-primary-600' : 'bg-white border-2 border-gray-200'
                    }`}>
                      {message.type === 'user' ? (
                        <User className="w-5 h-5 text-white" />
                      ) : (
                        <Bot className="w-5 h-5 text-primary-600" />
                      )}
                    </div>

                    {/* Message Bubble */}
                    <div className="flex-1">
                      <div
                        className={`rounded-2xl px-4 py-3 ${
                          message.type === 'user'
                            ? 'bg-primary-600 text-white'
                            : 'bg-white border border-gray-200 text-gray-800 shadow-sm'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.text}</p>
                      </div>
                      
                      {/* Options Grid */}
                      {message.options && (
                        <div className="mt-3 space-y-2">
                          {message.options.map((option, idx) => (
                            <motion.button
                              key={idx}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ delay: idx * 0.08 }}
                              onClick={() => handleOptionClick(option.action)}
                              className={`w-full text-left px-4 py-3 rounded-xl border-2 transition-all shadow-sm hover:shadow-md ${option.gradient}`}
                            >
                              <div className="flex items-center space-x-3">
                                <span className="text-2xl">{option.icon}</span>
                                <div className="flex-1">
                                  <div className="font-bold text-sm">{option.label}</div>
                                  <div className="text-xs opacity-75 mt-0.5">{option.desc}</div>
                                </div>
                              </div>
                            </motion.button>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="w-8 h-8 rounded-full bg-white border-2 border-gray-200 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-primary-600" />
                    </div>
                    <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3 shadow-sm flex items-center space-x-3">
                      <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                      <span className="text-sm text-gray-600">Analyzing...</span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={mode === 'fact_check' ? 'Enter claim to verify...' : mode ? 'Type your question...' : 'Select an option above...'}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm bg-gray-50"
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="px-4 py-3 gradient-saffron text-white rounded-xl hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Powered by Groq AI • {messages.length - 1} queries
              </p>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatInterface;