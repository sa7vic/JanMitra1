import unittest
from collections import defaultdict

from services.graph_reasoner import GraphEdge, GraphReasoningService


class TestGraphReasonerPipeline(unittest.TestCase):
    def setUp(self):
        self.service = GraphReasoningService()

        nodes = {
            'Policy A': {
                'id': 'Policy A',
                'entity_id': 1,
                'type': 'policy',
                'importance': 0.9,
            },
            'Event B': {
                'id': 'Event B',
                'entity_id': 2,
                'type': 'event',
                'importance': 0.8,
            },
            'District X': {
                'id': 'District X',
                'entity_id': 3,
                'type': 'location',
                'importance': 0.7,
            },
            'Farmer Group': {
                'id': 'Farmer Group',
                'entity_id': 4,
                'type': 'group',
                'importance': 0.85,
            },
            'Farm Collective': {
                'id': 'Farm Collective',
                'entity_id': 5,
                'type': 'group',
                'importance': 0.65,
            },
            'Orphan Node': {
                'id': 'Orphan Node',
                'entity_id': 6,
                'type': 'other',
                'importance': 0.2,
            },
        }

        edges = [
            GraphEdge('Policy A', 'Farmer Group', 'BENEFITS', 0.9, {}),
            GraphEdge('Event B', 'District X', 'OCCURRED_IN', 0.8, {}),
            GraphEdge('Policy A', 'Event B', 'RELATED_TO', 0.6, {}),
        ]

        out_adj = defaultdict(list)
        in_adj = defaultdict(list)
        for edge in edges:
            out_adj[edge.source].append(edge)
            in_adj[edge.target].append(edge)

        self.fake_graph = {
            'nodes': nodes,
            'edges': edges,
            'out_adj': out_adj,
            'in_adj': in_adj,
            'integrity_issues': [],
        }

        self.service._build_graph = lambda: self.fake_graph  # type: ignore[attr-defined]

    def test_simple_query(self):
        result = self.service.interpret_and_query('Who benefits "Farmer Group"?', max_depth=3)
        self.assertNotIn('error', result)
        self.assertIn('generated_query', result)
        self.assertTrue(result.get('post_validation', {}).get('ok'))
        self.assertGreaterEqual(len(result.get('edges', [])), 1)

    def test_multi_hop_query(self):
        result = self.service.interpret_and_query(
            'How is "Policy A" connected to "District X"?',
            max_depth=4,
        )
        self.assertNotIn('error', result)
        self.assertEqual(result.get('query_type'), 'path')
        self.assertTrue(result.get('paths'))
        self.assertEqual(result['paths'][0][0], 'Policy A')
        self.assertEqual(result['paths'][0][-1], 'District X')

    def test_ambiguous_query(self):
        result = self.service.interpret_and_query('What affects "Farm"?', max_depth=3)
        self.assertIn('error', result)
        self.assertEqual(result.get('query_type'), 'ambiguous')
        self.assertTrue(result.get('clarification'))

    def test_edge_case_no_results(self):
        result = self.service.interpret_and_query(
            'How is "Orphan Node" connected to "District X"?',
            max_depth=3,
        )
        self.assertNotIn('error', result)
        self.assertEqual(result.get('status'), 'no_data')
        self.assertEqual(result.get('paths'), [])


if __name__ == '__main__':
    unittest.main()
