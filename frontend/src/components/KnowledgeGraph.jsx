import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Network, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../lib/api';

const KnowledgeGraph = () => {
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchGraphData();
  }, []);

  const fetchGraphData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/knowledge-graph`);
      setGraphData(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load knowledge graph');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error || !graphData) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
        <div className="flex items-center space-x-3 text-red-600">
          <AlertCircle className="w-6 h-6" />
          <span>{error || 'No graph data available'}</span>
        </div>
      </div>
    );
  }

  const { nodes = [], edges = [] } = graphData;

  // Group nodes by type
  const nodesByType = nodes.reduce((acc, node) => {
    const type = node.type || 'other';
    if (!acc[type]) acc[type] = [];
    acc[type].push(node);
    return acc;
  }, {});

  const types = Object.keys(nodesByType);

  const typeColors = {
    place: 'bg-blue-100 text-blue-800 border-blue-300',
    commodity: 'bg-green-100 text-green-800 border-green-300',
    indicator: 'bg-purple-100 text-purple-800 border-purple-300',
    policy: 'bg-orange-100 text-orange-800 border-orange-300',
    event: 'bg-red-100 text-red-800 border-red-300',
    technology: 'bg-indigo-100 text-indigo-800 border-indigo-300',
    other: 'bg-gray-100 text-gray-800 border-gray-300',
  };

  const filteredNodes = filter === 'all' ? nodes : nodes.filter(n => n.type === filter);
  const filteredEdges = edges.filter(e => 
    filteredNodes.find(n => n.id === e.source) && 
    filteredNodes.find(n => n.id === e.target)
  );

  // Find most connected nodes
  const connectionCounts = {};
  edges.forEach(edge => {
    connectionCounts[edge.source] = (connectionCounts[edge.source] || 0) + 1;
    connectionCounts[edge.target] = (connectionCounts[edge.target] || 0) + 1;
  });

  const topNodes = nodes
    .map(node => ({ ...node, connections: connectionCounts[node.id] || 0 }))
    .sort((a, b) => b.connections - a.connections)
    .slice(0, 10);

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Network className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Knowledge Graph</h3>
              <p className="text-sm text-gray-600">
                {nodes.length} entities • {edges.length} relationships
              </p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
              filter === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            All ({nodes.length})
          </button>
          {types.map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-3 py-1 rounded-lg text-sm font-medium transition capitalize ${
                filter === type
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {type} ({nodesByType[type].length})
            </button>
          ))}
        </div>
      </div>

      {/* Graph Visualization - Network View */}
      <div className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Connected Entities */}
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-4">Most Connected Entities</h4>
            <div className="space-y-2">
              {topNodes.map((node, idx) => (
                <motion.div
                  key={node.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className={`p-3 rounded-lg border-2 ${typeColors[node.type] || typeColors.other} flex items-center justify-between`}
                >
                  <div className="flex-1">
                    <div className="font-semibold">{node.label}</div>
                    <div className="text-xs opacity-75">{node.description?.substring(0, 60)}...</div>
                  </div>
                  <div className="ml-3 text-right">
                    <div className="text-2xl font-bold">{node.connections}</div>
                    <div className="text-xs opacity-75">links</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Key Relationships */}
          <div>
            <h4 className="text-sm font-bold text-gray-900 mb-4">Key Relationships</h4>
            <div className="space-y-3">
              {filteredEdges.slice(0, 10).map((edge, idx) => {
                const source = nodes.find(n => n.id === edge.source);
                const target = nodes.find(n => n.id === edge.target);
                
                if (!source || !target) return null;

                const relationshipIcons = {
                  causes: '→',
                  affects: '↔',
                  relates_to: '•',
                };

                return (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="p-3 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <div className="flex items-center space-x-2 text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${typeColors[source.type]}`}>
                        {source.label}
                      </span>
                      <span className="text-gray-400 font-bold">
                        {relationshipIcons[edge.type] || '•'}
                      </span>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${typeColors[target.type]}`}>
                        {target.label}
                      </span>
                    </div>
                    {edge.strength && (
                      <div className="mt-2 flex items-center space-x-2">
                        <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary-500 rounded-full"
                            style={{ width: `${edge.strength * 100}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600 font-medium">
                          {(edge.strength * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Stats Summary */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          {types.map(type => (
            <div key={type} className={`p-4 rounded-lg border-2 ${typeColors[type]}`}>
              <div className="text-2xl font-bold">{nodesByType[type].length}</div>
              <div className="text-sm opacity-75 capitalize">{type}s</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraph;