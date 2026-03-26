import { useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertCircle,
  Loader2,
  Network,
  Search,
  Waypoints,
} from 'lucide-react';
import cytoscape from 'cytoscape';

import {
  getGraphNeighbors,
  getGraphPath,
  getGraphSubgraph,
  queryGraphNaturalLanguage,
  searchGraphEntities,
} from '../lib/api';

const TYPE_COLORS = {
  person: '#1d4ed8',
  place: '#0f766e',
  event: '#dc2626',
  policy: '#c2410c',
  scheme: '#9333ea',
  group: '#ca8a04',
  commodity: '#16a34a',
  indicator: '#be185d',
  other: '#334155',
};

const toElements = (graphData) => {
  const nodes = (graphData.nodes || []).map((node) => ({
    data: {
      id: node.id,
      label: node.id,
      type: node.type || 'other',
      description: node.description || '',
    },
  }));

  const edges = (graphData.edges || []).map((edge, index) => ({
    data: {
      id: `${edge.source}-${edge.target}-${edge.label}-${index}`,
      source: edge.source,
      target: edge.target,
      label: edge.label || 'related_to',
      weight: edge.weight || 0.5,
      context: edge.metadata?.context || '',
    },
  }));

  return [...nodes, ...edges];
};

const KnowledgeGraph = () => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);

  const [graphData, setGraphData] = useState({ nodes: [], edges: [], paths: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [explanation, setExplanation] = useState('');
  const [generatedQuery, setGeneratedQuery] = useState('');
  const [validationSummary, setValidationSummary] = useState('');
  const [queryInput, setQueryInput] = useState('How is Modi connected to agriculture?');
  const [searchInput, setSearchInput] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [busy, setBusy] = useState(false);

  const stats = useMemo(() => {
    const byType = {};
    graphData.nodes.forEach((node) => {
      const t = node.type || 'other';
      byType[t] = (byType[t] || 0) + 1;
    });
    return byType;
  }, [graphData.nodes]);

  const createCytoscape = (data) => {
    if (!containerRef.current) {
      return;
    }

    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const elements = toElements(data);
    cyRef.current = cytoscape({
      container: containerRef.current,
      elements,
      wheelSensitivity: 0.15,
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'font-size': 11,
            'text-valign': 'center',
            'text-halign': 'center',
            color: '#ffffff',
            'text-outline-width': 2,
            'text-outline-color': '#0f172a',
            width: 30,
            height: 30,
            'background-color': (ele) => TYPE_COLORS[ele.data('type')] || TYPE_COLORS.other,
          },
        },
        {
          selector: 'edge',
          style: {
            label: 'data(label)',
            width: 2,
            'curve-style': 'bezier',
            'target-arrow-shape': 'triangle',
            'line-color': '#94a3b8',
            'target-arrow-color': '#94a3b8',
            'font-size': 9,
            color: '#334155',
            'text-background-color': '#ffffff',
            'text-background-opacity': 0.9,
            'text-background-padding': 2,
          },
        },
        {
          selector: '.faded',
          style: {
            opacity: 0.12,
          },
        },
        {
          selector: '.highlighted',
          style: {
            'border-width': 3,
            'border-color': '#f97316',
            opacity: 1,
            width: 38,
            height: 38,
          },
        },
        {
          selector: '.path-edge',
          style: {
            'line-color': '#f97316',
            'target-arrow-color': '#f97316',
            width: 4,
            opacity: 1,
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: true,
        fit: true,
        padding: 28,
        nodeRepulsion: 120000,
        idealEdgeLength: 120,
      },
    });

    cyRef.current.on('tap', 'node', (event) => {
      const node = event.target;
      setSelectedNode(node.data());
      setSelectedEdge(null);

      cyRef.current.elements().addClass('faded').removeClass('highlighted');
      const neighborhood = node.closedNeighborhood();
      neighborhood.removeClass('faded');
      node.addClass('highlighted');
    });

    cyRef.current.on('tap', 'edge', (event) => {
      setSelectedEdge(event.target.data());
      setSelectedNode(null);
    });

    cyRef.current.on('tap', (event) => {
      if (event.target === cyRef.current) {
        cyRef.current.elements().removeClass('faded highlighted path-edge');
        setSelectedNode(null);
        setSelectedEdge(null);
      }
    });
  };

  const renderGraph = (data, explanationText = '') => {
    setGraphData(data);
    setExplanation(explanationText || data.explanation || '');
    setGeneratedQuery(data.generated_query || data.corrected_query || '');

    const validation = data.validation || {};
    const errors = validation.errors || [];
    const clarifications = data.clarification || validation.clarifications || [];
    if (errors.length > 0) {
      setValidationSummary(`Validation failed: ${errors.join(' | ')}`);
    } else if (clarifications.length > 0) {
      setValidationSummary('Ambiguous query: clarification required.');
    } else {
      setValidationSummary('Validated against graph schema.');
    }

    createCytoscape(data);
  };

  const loadSeedGraph = async () => {
    try {
      setLoading(true);
      const data = await getGraphSubgraph(120, 240);
      renderGraph(data, data.explanation);
      setError('');
    } catch (err) {
      setError('Failed to load graph data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSeedGraph();
  }, []);

  useEffect(() => {
    const handle = setTimeout(async () => {
      const needle = searchInput.trim();
      if (!needle) {
        setSearchResults([]);
        return;
      }
      try {
        const data = await searchGraphEntities(needle, 8);
        setSearchResults(data.matches || []);
      } catch (_err) {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(handle);
  }, [searchInput]);

  const runNaturalLanguageQuery = async () => {
    const query = queryInput.trim();
    if (!query) {
      return;
    }

    try {
      setBusy(true);
      const data = await queryGraphNaturalLanguage(query, 4);
      if (data.error) {
        const clarification = (data.clarification || [])
          .map((item) => `${item.token}: ${item.candidates?.join(', ') || 'no suggestions'}`)
          .join(' | ');
        setError(clarification ? `${data.error} ${clarification}` : data.error);
      } else {
        setError('');
      }
      renderGraph(data, data.explanation || `Query executed: ${query}`);

      if (cyRef.current && data.paths?.length) {
        highlightPaths(data.paths);
      }
    } catch (_err) {
      setError('Failed to execute graph query');
    } finally {
      setBusy(false);
    }
  };

  const highlightPaths = (paths) => {
    if (!cyRef.current || !paths?.length) {
      return;
    }

    const cy = cyRef.current;
    cy.elements().addClass('faded').removeClass('path-edge highlighted');

    const nodeIds = new Set();
    const edgeKeys = new Set();
    paths.forEach((path) => {
      path.forEach((nodeId) => nodeIds.add(nodeId));
      for (let i = 0; i < path.length - 1; i += 1) {
        edgeKeys.add(`${path[i]}:::${path[i + 1]}`);
      }
    });

    nodeIds.forEach((nodeId) => {
      const node = cy.getElementById(nodeId);
      node.removeClass('faded').addClass('highlighted');
    });

    cy.edges().forEach((edge) => {
      const key = `${edge.data('source')}:::${edge.data('target')}`;
      if (edgeKeys.has(key)) {
        edge.removeClass('faded').addClass('path-edge');
      }
    });
  };

  const loadNeighborhood = async (entityName) => {
    try {
      setBusy(true);
      const data = await getGraphNeighbors(entityName, 2, 'both', 220);
      renderGraph(data, data.explanation || `Loaded neighborhood for ${entityName}`);
    } catch (_err) {
      setError('Failed to load neighborhood');
    } finally {
      setBusy(false);
    }
  };

  const runPathQuery = async () => {
    const parts = queryInput
      .split('->')
      .map((item) => item.trim())
      .filter(Boolean);

    if (parts.length !== 2) {
      return;
    }

    try {
      setBusy(true);
      const data = await getGraphPath(parts[0], parts[1], 5);
      renderGraph(data, data.explanation || `Path query ${parts[0]} -> ${parts[1]}`);
      highlightPaths(data.paths || []);
    } catch (_err) {
      setError('Failed to find path between entities');
    } finally {
      setBusy(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
        <div className="flex items-center space-x-3 text-red-600">
          <AlertCircle className="w-6 h-6" />
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-5 border-b border-gray-200 bg-gray-50">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Network className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">Graph Reasoning</h3>
              <p className="text-xs text-gray-600">
                {graphData.nodes.length} nodes and {graphData.edges.length} edges loaded
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={loadSeedGraph}
            className="px-3 py-2 rounded-md bg-slate-900 text-white text-sm font-semibold hover:bg-slate-700 transition"
          >
            Reset Graph
          </button>
        </div>

        <div className="mt-4 grid grid-cols-1 lg:grid-cols-2 gap-3">
          <div>
            <label className="text-xs font-semibold text-gray-700">Natural Language Query</label>
            <div className="mt-1 flex items-center gap-2">
              <input
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                placeholder="What policies affect farmers?"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
              />
              <button
                type="button"
                onClick={runNaturalLanguageQuery}
                disabled={busy}
                className="px-3 py-2 rounded-md bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 disabled:opacity-50"
              >
                {busy ? 'Running' : 'Run'}
              </button>
              <button
                type="button"
                onClick={runPathQuery}
                disabled={busy}
                className="px-3 py-2 rounded-md bg-orange-600 text-white text-sm font-semibold hover:bg-orange-700 disabled:opacity-50"
              >
                Path A-&gt;B
              </button>
            </div>
          </div>

          <div className="relative">
            <label className="text-xs font-semibold text-gray-700">Entity Search (debounced)</label>
            <div className="mt-1 flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-2 top-2.5 w-4 h-4 text-gray-400" />
                <input
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                  placeholder="Search entities"
                  className="w-full pl-8 pr-2 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
            </div>
            {searchResults.length > 0 && (
              <div className="absolute z-20 mt-1 w-full bg-white border border-gray-200 rounded-md shadow">
                {searchResults.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => loadNeighborhood(item.id)}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 flex items-center justify-between"
                  >
                    <span>{item.id}</span>
                    <span className="text-xs text-gray-500">{item.type}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-0">
        <div className="xl:col-span-3 border-r border-gray-200">
          <div ref={containerRef} className="w-full h-[560px]" />
        </div>

        <div className="p-4 bg-gray-50">
          <h4 className="text-sm font-bold text-gray-900 flex items-center gap-2">
            <Waypoints className="w-4 h-4" />
            Result Panel
          </h4>

          <div className="mt-3 space-y-3 text-sm">
            <div>
              <div className="font-semibold text-gray-700">Explanation</div>
              <p className="text-gray-600">{explanation || 'No explanation yet.'}</p>
            </div>

            <div>
              <div className="font-semibold text-gray-700">Generated Query</div>
              <p className="text-gray-600 break-words">{generatedQuery || 'Query not generated yet.'}</p>
            </div>

            <div>
              <div className="font-semibold text-gray-700">Validation</div>
              <p className="text-gray-600">{validationSummary || 'No validation summary yet.'}</p>
            </div>

            <div>
              <div className="font-semibold text-gray-700">Selected Node</div>
              <p className="text-gray-600">
                {selectedNode
                  ? `${selectedNode.id} (${selectedNode.type})`
                  : 'Click a node to inspect neighborhood'}
              </p>
            </div>

            <div>
              <div className="font-semibold text-gray-700">Selected Edge</div>
              <p className="text-gray-600">
                {selectedEdge
                  ? `${selectedEdge.source} -[${selectedEdge.label}]-> ${selectedEdge.target}`
                  : 'Hover/click edge to inspect relation'}
              </p>
              {selectedEdge?.context && (
                <p className="text-xs text-gray-500 mt-1">{selectedEdge.context}</p>
              )}
            </div>

            <div>
              <div className="font-semibold text-gray-700">Type Distribution</div>
              <div className="mt-2 grid grid-cols-2 gap-2">
                {Object.entries(stats).slice(0, 8).map(([type, count]) => (
                  <motion.div
                    key={type}
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="px-2 py-1 rounded bg-white border border-gray-200"
                  >
                    <div className="text-xs font-semibold text-gray-700 capitalize">{type}</div>
                    <div className="text-base font-bold text-gray-900">{count}</div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeGraph;