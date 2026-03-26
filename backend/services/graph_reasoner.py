from __future__ import annotations

import re
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Optional

from models.database import Entity, Relationship


@dataclass
class GraphEdge:
    source: str
    target: str
    label: str
    weight: float
    metadata: dict[str, Any]


@dataclass
class GraphIntent:
    query_type: str
    entity_tokens: list[str]
    relation_labels: set[str]
    direction: str
    max_depth: int
    filters: dict[str, Any]
    raw_query: str


class GraphReasoningService:
    """Deterministic graph reasoning with strict schema validation."""

    ENTITY_TYPE_ALIASES = {
        'person': 'person',
        'people': 'person',
        'location': 'location',
        'place': 'location',
        'event': 'event',
        'case': 'case',
        'policy': 'policy',
        'scheme': 'scheme',
        'group': 'group',
        'organization': 'organization',
        'org': 'organization',
        'commodity': 'commodity',
        'indicator': 'indicator',
        'other': 'other',
    }

    GRAPH_SCHEMA = {
        'entity_types': {
            'person': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'location': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'event': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'case': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'organization': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'policy': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'scheme': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'group': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'commodity': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'indicator': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
            'other': {
                'required_properties': ['id', 'entity_id', 'type'],
                'unique_property': 'id',
            },
        },
        'relationships': {
            'OCCURRED_IN': {
                'source_types': {'event', 'case'},
                'target_types': {'location'},
                'directional': True,
                'description': 'An event/case occurred in a location.',
            },
            'REPORTED_AT': {
                'source_types': {'case', 'event'},
                'target_types': {'location', 'organization'},
                'directional': True,
                'description': 'A case/event was reported at a location or org.',
            },
            'ASSIGNED_TO': {
                'source_types': {'case', 'event'},
                'target_types': {'person', 'organization'},
                'directional': True,
                'description': 'A case/event is assigned to owner.',
            },
            'AFFECTS': {
                'source_types': {'policy', 'event', 'indicator', 'commodity'},
                'target_types': {'group', 'location', 'commodity', 'indicator'},
                'directional': True,
                'description': 'Source affects target.',
            },
            'BENEFITS': {
                'source_types': {'policy', 'scheme'},
                'target_types': {'group', 'person', 'location'},
                'directional': True,
                'description': 'Policy/scheme benefits target.',
            },
            'RELATED_TO': {
                'source_types': {'person', 'location', 'event', 'case', 'organization', 'policy', 'scheme', 'group', 'commodity', 'indicator', 'other'},
                'target_types': {'person', 'location', 'event', 'case', 'organization', 'policy', 'scheme', 'group', 'commodity', 'indicator', 'other'},
                'directional': False,
                'description': 'Generic fallback relation when domain relation is unavailable.',
            },
        },
    }

    RELATION_KEYWORDS = {
        'AFFECTS': {'affect', 'affects', 'affected', 'impact', 'impacts', 'influence', 'influences'},
        'BENEFITS': {'benefit', 'benefits', 'help', 'helps', 'support', 'supports'},
        'ASSIGNED_TO': {'assigned to', 'owns', 'owner'},
        'OCCURRED_IN': {'occurred in', 'happened in', 'in'},
        'REPORTED_AT': {'reported at', 'reported in', 'logged at'},
        'RELATED_TO': {'related', 'connected', 'link', 'linked'},
    }

    def _json_safe(self, value: Any) -> Any:
        if isinstance(value, set):
            return sorted(value)
        if isinstance(value, dict):
            return {
                key: self._json_safe(item)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        return value

    def intent_to_dict(self, intent: GraphIntent) -> dict[str, Any]:
        return {
            'query_type': intent.query_type,
            'entity_tokens': intent.entity_tokens,
            'relation_labels': sorted(intent.relation_labels),
            'direction': intent.direction,
            'max_depth': intent.max_depth,
            'filters': intent.filters,
            'raw_query': intent.raw_query,
        }

    def _normalize_entity_type(self, raw_type: Optional[str]) -> str:
        normalized = (raw_type or 'other').strip().lower()
        return self.ENTITY_TYPE_ALIASES.get(normalized, 'other')

    def _normalize_relation_label(self, raw_label: Optional[str]) -> str:
        value = (raw_label or 'RELATED_TO').strip().upper()
        value = re.sub(r'[^A-Z0-9]+', '_', value).strip('_')
        return value or 'RELATED_TO'

    def _schema_relation_allowed(
        self,
        relation_label: str,
        source_type: str,
        target_type: str,
    ) -> bool:
        spec = self.GRAPH_SCHEMA['relationships'].get(relation_label)
        if not spec:
            return False
        return (
            source_type in spec['source_types']
            and target_type in spec['target_types']
        )

    def _build_graph(self) -> dict[str, Any]:
        entities = Entity.query.all()
        relationships = Relationship.query.all()

        nodes: dict[str, dict[str, Any]] = {}
        node_name_by_lc: dict[str, str] = {}
        integrity_issues: list[dict[str, Any]] = []

        for entity in entities:
            entity_name = (entity.name or '').strip()
            if not entity_name:
                continue

            key_lc = entity_name.lower()
            entity_type = self._normalize_entity_type(entity.type)
            node_payload = {
                'id': entity_name,
                'entity_id': entity.id,
                'type': entity_type,
                'description': entity.description,
                'importance': entity.importance_score,
                'created_at': entity.created_at.isoformat() if entity.created_at else None,
                'updated_at': entity.updated_at.isoformat() if entity.updated_at else None,
            }

            if key_lc in node_name_by_lc:
                # Deterministic duplicate resolution: keep higher importance.
                existing_name = node_name_by_lc[key_lc]
                existing = nodes[existing_name]
                existing_importance = existing.get('importance') or 0.0
                incoming_importance = node_payload.get('importance') or 0.0
                if incoming_importance > existing_importance:
                    nodes.pop(existing_name, None)
                    nodes[entity_name] = node_payload
                    node_name_by_lc[key_lc] = entity_name
                integrity_issues.append({
                    'kind': 'duplicate_entity_name',
                    'name': entity_name,
                    'resolved_to': node_name_by_lc[key_lc],
                })
                continue

            nodes[entity_name] = node_payload
            node_name_by_lc[key_lc] = entity_name

        out_adj: dict[str, list[GraphEdge]] = defaultdict(list)
        in_adj: dict[str, list[GraphEdge]] = defaultdict(list)
        edges: list[GraphEdge] = []

        for rel in relationships:
            source_name = rel.source.name if rel.source else None
            target_name = rel.target.name if rel.target else None
            if not source_name or not target_name:
                integrity_issues.append({
                    'kind': 'invalid_relationship_missing_nodes',
                    'relationship_id': rel.id,
                })
                continue

            source = nodes.get(source_name)
            target = nodes.get(target_name)
            if not source or not target:
                integrity_issues.append({
                    'kind': 'invalid_relationship_unknown_nodes',
                    'relationship_id': rel.id,
                    'source': source_name,
                    'target': target_name,
                })
                continue

            label = self._normalize_relation_label(rel.relationship_type)
            if label not in self.GRAPH_SCHEMA['relationships']:
                label = 'RELATED_TO'

            if not self._schema_relation_allowed(label, source['type'], target['type']):
                integrity_issues.append({
                    'kind': 'invalid_relationship_pair',
                    'relationship_id': rel.id,
                    'label': label,
                    'source_type': source['type'],
                    'target_type': target['type'],
                })
                continue

            edge = GraphEdge(
                source=source_name,
                target=target_name,
                label=label,
                weight=rel.strength or 0.5,
                metadata={
                    'relationship_id': rel.id,
                    'context': rel.context,
                    'bidirectional_input': bool(rel.bidirectional),
                    'created_at': rel.created_at.isoformat() if rel.created_at else None,
                },
            )
            edges.append(edge)
            out_adj[source_name].append(edge)
            in_adj[target_name].append(edge)

            schema_bidirectional = not self.GRAPH_SCHEMA['relationships'][label]['directional']
            if schema_bidirectional or rel.bidirectional:
                reverse = GraphEdge(
                    source=target_name,
                    target=source_name,
                    label=label,
                    weight=edge.weight,
                    metadata=edge.metadata,
                )
                edges.append(reverse)
                out_adj[target_name].append(reverse)
                in_adj[source_name].append(reverse)

        return {
            'nodes': nodes,
            'edges': edges,
            'out_adj': out_adj,
            'in_adj': in_adj,
            'integrity_issues': integrity_issues,
        }

    def get_schema(self) -> dict[str, Any]:
        cypher_constraints = [
            'CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE;',
            'CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE;',
            'CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type);',
        ]

        cypher_rel_examples = []
        for label, spec in self.GRAPH_SCHEMA['relationships'].items():
            src = '|'.join(sorted(spec['source_types']))
            tgt = '|'.join(sorted(spec['target_types']))
            cypher_rel_examples.append(
                f'// {label}: ({src}) -> ({tgt})'
            )

        return {
            'schema': self._json_safe(self.GRAPH_SCHEMA),
            'cypher': {
                'constraints': cypher_constraints,
                'relationship_rules': cypher_rel_examples,
            },
        }

    def _extract_quoted_entities(self, query: str) -> list[str]:
        return [item.strip() for item in re.findall(r'"([^"]+)"', query)]

    def _extract_candidate_entities(
        self,
        graph: dict[str, Any],
        query: str,
    ) -> list[str]:
        lowered = query.lower()
        matches = []
        for name in sorted(graph['nodes'].keys(), key=len, reverse=True):
            if name.lower() in lowered:
                matches.append(name)

        unique = []
        seen = set()
        for item in matches:
            if item not in seen:
                seen.add(item)
                unique.append(item)
        return unique

    def _infer_relations_from_query(self, query: str) -> set[str]:
        lowered = query.lower()
        inferred = set()
        for label, keywords in self.RELATION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in lowered:
                    inferred.add(label)
                    break
        return inferred or {'RELATED_TO'}

    def _parse_filters(self, query: str) -> dict[str, Any]:
        filters: dict[str, Any] = {}

        time_match = re.search(
            r'last\s+(\d+)\s*(hour|hours|day|days|week|weeks)',
            query.lower(),
        )
        if time_match:
            value = int(time_match.group(1))
            unit = time_match.group(2)
            if 'day' in unit:
                value *= 24
            elif 'week' in unit:
                value *= 24 * 7
            filters['time_range_hours'] = value

        region_match = re.search(r'\bin\s+([A-Za-z][A-Za-z\s\-]{2,40})$', query.strip())
        if region_match:
            filters['region'] = region_match.group(1).strip()

        return filters

    def _resolve_entity_candidates(
        self,
        graph: dict[str, Any],
        token: str,
    ) -> dict[str, Any]:
        token_clean = (token or '').strip()
        if not token_clean:
            return {'ok': False, 'error': 'empty_entity_token', 'candidates': []}

        exact = [
            name for name in graph['nodes']
            if name.lower() == token_clean.lower()
        ]
        if len(exact) == 1:
            return {'ok': True, 'entity': exact[0], 'candidates': exact}

        starts = [
            name for name in graph['nodes']
            if name.lower().startswith(token_clean.lower())
        ]
        if len(starts) == 1:
            return {'ok': True, 'entity': starts[0], 'candidates': starts}

        contains = [
            name for name in graph['nodes']
            if token_clean.lower() in name.lower()
        ]
        if len(contains) == 1:
            return {'ok': True, 'entity': contains[0], 'candidates': contains}

        if len(exact) > 1 or len(starts) > 1 or len(contains) > 1:
            pool = exact or starts or contains
            pool = sorted(pool)[:5]
            return {
                'ok': False,
                'error': 'ambiguous_entity',
                'token': token_clean,
                'candidates': pool,
            }

        return {
            'ok': False,
            'error': 'entity_not_found',
            'token': token_clean,
            'candidates': [],
        }

    def parse_intent(self, nl_query: str, max_depth: int = 4) -> GraphIntent:
        query = (nl_query or '').strip()
        lowered = query.lower()

        quoted = self._extract_quoted_entities(query)
        inferred_relations = self._infer_relations_from_query(query)
        filters = self._parse_filters(query)

        if 'connected' in lowered or 'path' in lowered or 'between' in lowered:
            query_type = 'path'
            direction = 'out'
        elif 'affected by' in lowered or 'impacted by' in lowered:
            query_type = 'reverse_neighbors'
            direction = 'out'
        elif lowered.startswith('what') or lowered.startswith('who'):
            query_type = 'neighbors'
            direction = 'in'
        else:
            query_type = 'unresolved'
            direction = 'both'

        return GraphIntent(
            query_type=query_type,
            entity_tokens=quoted,
            relation_labels=inferred_relations,
            direction=direction,
            max_depth=max(1, min(max_depth, 6)),
            filters=filters,
            raw_query=query,
        )

    def _validate_filters(self, filters: dict[str, Any]) -> list[str]:
        errors = []
        time_hours = filters.get('time_range_hours')
        if time_hours is not None and (time_hours <= 0 or time_hours > 24 * 365):
            errors.append('Invalid time range filter. Allowed range: 1 to 8760 hours.')
        return errors

    def validate_intent(self, graph: dict[str, Any], intent: GraphIntent) -> dict[str, Any]:
        errors: list[str] = []
        warnings: list[str] = []
        resolved_entities: list[str] = []
        clarifications: list[dict[str, Any]] = []

        if not intent.raw_query:
            errors.append('Query text is required.')

        if intent.query_type == 'unresolved':
            errors.append('Ambiguous query intent. Please specify relation or entities clearly.')

        errors.extend(self._validate_filters(intent.filters))

        tokens = intent.entity_tokens[:]
        if not tokens:
            tokens = self._extract_candidate_entities(graph, intent.raw_query)[:2]

        if intent.query_type == 'path' and len(tokens) < 2:
            errors.append('Path intent requires two entities.')
        if intent.query_type in {'neighbors', 'reverse_neighbors'} and len(tokens) < 1:
            errors.append('Neighbor intent requires at least one entity.')

        for token in tokens:
            resolution = self._resolve_entity_candidates(graph, token)
            if resolution.get('ok'):
                resolved_entities.append(resolution['entity'])
                continue

            if resolution.get('error') == 'ambiguous_entity':
                clarifications.append({
                    'token': resolution.get('token'),
                    'candidates': resolution.get('candidates', []),
                })
            else:
                errors.append(f"Entity '{token}' was not found.")

        # Normalize relation labels and validate against schema.
        valid_relations = set()
        for label in intent.relation_labels:
            normalized = self._normalize_relation_label(label)
            if normalized in self.GRAPH_SCHEMA['relationships']:
                valid_relations.add(normalized)
            else:
                warnings.append(f"Unknown relation '{label}' ignored.")

        if not valid_relations:
            valid_relations = {'RELATED_TO'}

        payload = {
            'ok': len(errors) == 0 and len(clarifications) == 0,
            'errors': errors,
            'warnings': warnings,
            'clarifications': clarifications,
            'resolved_entities': resolved_entities,
            'valid_relations': valid_relations,
        }
        return self._json_safe(payload)

    def _edge_payload(self, edge: GraphEdge) -> dict[str, Any]:
        return {
            'source': edge.source,
            'target': edge.target,
            'label': edge.label,
            'weight': edge.weight,
            'metadata': edge.metadata,
        }

    def _subgraph_from_paths(
        self,
        graph: dict[str, Any],
        paths: list[list[str]],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        node_names = set()
        edge_keys = set()
        output_edges: list[dict[str, Any]] = []

        for path in paths:
            node_names.update(path)
            for idx in range(len(path) - 1):
                source = path[idx]
                target = path[idx + 1]
                for edge in graph['out_adj'].get(source, []):
                    if edge.target != target:
                        continue
                    key = (edge.source, edge.target, edge.label)
                    if key in edge_keys:
                        continue
                    edge_keys.add(key)
                    output_edges.append(self._edge_payload(edge))

        output_nodes = [
            graph['nodes'][name]
            for name in node_names
            if name in graph['nodes']
        ]
        return output_nodes, output_edges

    def _bfs_shortest_path(
        self,
        graph: dict[str, Any],
        source: str,
        target: str,
        max_depth: int,
        allowed_relations: set[str],
    ) -> list[str] | None:
        if source == target:
            return [source]

        queue: deque[tuple[str, list[str], int]] = deque([(source, [source], 0)])
        visited = {source}

        while queue:
            node, path, depth = queue.popleft()
            if depth >= max_depth:
                continue

            for edge in graph['out_adj'].get(node, []):
                if edge.label not in allowed_relations and 'RELATED_TO' not in allowed_relations:
                    continue
                nxt = edge.target
                if nxt in visited:
                    continue
                new_path = path + [nxt]
                if nxt == target:
                    return new_path
                visited.add(nxt)
                queue.append((nxt, new_path, depth + 1))

        return None

    def _generate_cypher(self, plan: dict[str, Any]) -> str:
        query_type = plan['query_type']
        if query_type == 'path':
            relation_expr = '|'.join(sorted(plan['allowed_relations']))
            return (
                f"MATCH p=(a:Entity {{name: '{plan['source']}'}})-[:{relation_expr}*1..{plan['max_depth']}]->"
                f"(b:Entity {{name: '{plan['target']}'}}) RETURN p LIMIT 1"
            )

        relation_expr = '|'.join(sorted(plan['allowed_relations']))
        direction = '-->' if plan['direction'] == 'out' else '<--'
        return (
            f"MATCH (n:Entity {{name: '{plan['pivot']}'}}){direction}"
            f"(m:Entity) WHERE ANY(r IN relationships((n){direction}(m)) WHERE type(r) IN [{relation_expr}]) "
            f"RETURN n,m LIMIT {plan['limit_nodes']}"
        )

    def _post_validate_result(self, plan: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        errors = []
        query_type = plan['query_type']

        if query_type == 'path' and result.get('paths'):
            path = result['paths'][0]
            if not path or path[0] != plan['source'] or path[-1] != plan['target']:
                errors.append('Returned path does not match requested source/target.')

        allowed = plan['allowed_relations']
        for edge in result.get('edges', []):
            if edge.get('label') not in allowed and 'RELATED_TO' not in allowed:
                errors.append('Result includes relation outside validated intent.')
                break

        return {
            'ok': len(errors) == 0,
            'errors': errors,
        }

    def _execute_path_plan(self, graph: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
        path = self._bfs_shortest_path(
            graph,
            source=plan['source'],
            target=plan['target'],
            max_depth=plan['max_depth'],
            allowed_relations=plan['allowed_relations'],
        )
        if not path:
            return {
                'nodes': [graph['nodes'][plan['source']], graph['nodes'][plan['target']]],
                'edges': [],
                'paths': [],
                'status': 'no_data',
                'message': 'No data found for the validated path intent.',
            }

        nodes, edges = self._subgraph_from_paths(graph, [path])
        return {
            'nodes': nodes,
            'edges': edges,
            'paths': [path],
            'status': 'ok',
        }

    def _execute_neighbor_plan(self, graph: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
        pivot = plan['pivot']
        direction = plan['direction']
        depth = plan['max_depth']
        limit_nodes = plan['limit_nodes']
        allowed = plan['allowed_relations']

        queue = deque([(pivot, 0)])
        visited_nodes = {pivot}
        visited_edges = set()
        output_edges = []

        while queue and len(visited_nodes) < limit_nodes:
            node, level = queue.popleft()
            if level >= depth:
                continue

            if direction in {'out', 'both'}:
                candidates = graph['out_adj'].get(node, [])
            else:
                candidates = graph['in_adj'].get(node, [])

            for edge in candidates:
                if edge.label not in allowed and 'RELATED_TO' not in allowed:
                    continue
                key = (edge.source, edge.target, edge.label)
                if key in visited_edges:
                    continue
                visited_edges.add(key)
                output_edges.append(self._edge_payload(edge))

                next_node = edge.target if direction in {'out', 'both'} else edge.source
                if next_node not in visited_nodes and len(visited_nodes) < limit_nodes:
                    visited_nodes.add(next_node)
                    queue.append((next_node, level + 1))

        nodes = [graph['nodes'][name] for name in visited_nodes if name in graph['nodes']]
        if len(nodes) <= 1:
            return {
                'nodes': nodes,
                'edges': [],
                'paths': [[pivot]],
                'status': 'no_data',
                'message': 'No data found for the validated neighborhood intent.',
            }

        return {
            'nodes': nodes,
            'edges': output_edges,
            'paths': [[pivot]],
            'status': 'ok',
        }

    def _build_explanation(self, plan: dict[str, Any], result: dict[str, Any]) -> str:
        if result.get('status') == 'no_data':
            return result.get('message', 'No data found.')

        if plan['query_type'] == 'path':
            relation_desc = ', '.join(sorted(plan['allowed_relations']))
            hop_count = (len(result.get('paths', [[]])[0]) - 1) if result.get('paths') else 0
            return (
                f"This query finds a path from {plan['source']} to {plan['target']} "
                f"using validated relations ({relation_desc}) up to {plan['max_depth']} hops. "
                f"Returned path length: {hop_count} hops."
            )

        relation_desc = ', '.join(sorted(plan['allowed_relations']))
        direction_text = 'outgoing' if plan['direction'] == 'out' else 'incoming'
        return (
            f"This query finds {direction_text} neighbors of {plan['pivot']} by traversing "
            f"validated relations ({relation_desc}) up to depth {plan['max_depth']}."
        )

    def _error_response(self, message: str, **extra: Any) -> dict[str, Any]:
        payload = {
            'error': message,
            'nodes': [],
            'edges': [],
            'paths': [],
        }
        payload.update(extra)
        return payload

    def interpret_and_query(self, nl_query: str, max_depth: int = 4) -> dict[str, Any]:
        graph = self._build_graph()
        intent = self.parse_intent(nl_query, max_depth=max_depth)
        validation = self.validate_intent(graph, intent)

        if validation.get('clarifications'):
            return self._error_response(
                'Ambiguous query. Clarification required.',
                query_type='ambiguous',
                clarification=validation['clarifications'],
                intent=self.intent_to_dict(intent),
                schema=self.get_schema()['schema'],
            )

        if not validation.get('ok'):
            return self._error_response(
                'Invalid query intent for current schema.',
                query_type='invalid',
                validation=validation,
                intent=self.intent_to_dict(intent),
                schema=self.get_schema()['schema'],
            )

        resolved = validation['resolved_entities']
        allowed_relations = validation['valid_relations']

        if intent.query_type == 'path':
            plan = {
                'query_type': 'path',
                'source': resolved[0],
                'target': resolved[1],
                'max_depth': intent.max_depth,
                'allowed_relations': allowed_relations,
            }
            generated_query = self._generate_cypher(plan)
            result = self._execute_path_plan(graph, plan)
        else:
            pivot = resolved[0]
            plan = {
                'query_type': 'neighbors',
                'pivot': pivot,
                'direction': intent.direction,
                'max_depth': intent.max_depth,
                'allowed_relations': allowed_relations,
                'limit_nodes': 250,
            }
            generated_query = self._generate_cypher(plan)
            result = self._execute_neighbor_plan(graph, plan)

        post_validation = self._post_validate_result(plan, result)
        if not post_validation['ok']:
            return self._error_response(
                'Result failed post-execution validation.',
                query_type='validation_error',
                generated_query=generated_query,
                intent=self.intent_to_dict(intent),
                validation=validation,
                post_validation=post_validation,
                corrected_query=generated_query,
                explanation='Execution result did not match validated intent, so response is safely rejected.',
            )

        result.update({
            'query_type': plan['query_type'],
            'generated_query': generated_query,
            'corrected_query': generated_query,
            'intent': self.intent_to_dict(intent),
            'validation': validation,
            'post_validation': post_validation,
            'integrity_issues': graph.get('integrity_issues', [])[:25],
            'explanation': self._build_explanation(plan, result),
        })
        return self._json_safe(result)

    def search_entities(self, q: str, limit: int = 10) -> list[dict[str, Any]]:
        graph = self._build_graph()
        needle = (q or '').strip().lower()
        if not needle:
            return []

        matches = [
            node for node in graph['nodes'].values()
            if needle in node['id'].lower()
        ]
        matches.sort(
            key=lambda row: (
                len(row['id']),
                -(row.get('importance') or 0),
                row['id'].lower(),
            )
        )
        return matches[:limit]

    def get_seed_subgraph(self, limit_nodes: int = 120, limit_edges: int = 240) -> dict[str, Any]:
        graph = self._build_graph()
        sorted_nodes = sorted(
            graph['nodes'].values(),
            key=lambda node: ((node.get('importance') or 0), node['id']),
            reverse=True,
        )[:limit_nodes]
        node_names = {node['id'] for node in sorted_nodes}

        edges = []
        seen = set()
        for edge in graph['edges']:
            if edge.source not in node_names or edge.target not in node_names:
                continue
            key = (edge.source, edge.target, edge.label)
            if key in seen:
                continue
            seen.add(key)
            edges.append(self._edge_payload(edge))
            if len(edges) >= limit_edges:
                break

        return {
            'nodes': sorted_nodes,
            'edges': edges,
            'paths': [],
            'explanation': 'Seed graph loaded from schema-valid entities and relationships.',
            'schema': self.get_schema()['schema'],
            'integrity_issues': graph.get('integrity_issues', [])[:25],
        }

    def shortest_path(
        self,
        source_name: str,
        target_name: str,
        max_depth: int = 5,
    ) -> dict[str, Any]:
        query = f'path from "{source_name}" to "{target_name}"'
        return self.interpret_and_query(query, max_depth=max_depth)

    def neighbors(
        self,
        entity_name: str,
        depth: int = 1,
        direction: str = 'both',
        limit_nodes: int = 250,
    ) -> dict[str, Any]:
        direction_hint = 'who affects' if direction == 'in' else 'what is related to'
        query = f'{direction_hint} "{entity_name}"'
        result = self.interpret_and_query(query, max_depth=depth)

        # Enforce caller limit post-safe execution.
        if result.get('nodes') and len(result['nodes']) > limit_nodes:
            keep = {node['id'] for node in result['nodes'][:limit_nodes]}
            result['nodes'] = result['nodes'][:limit_nodes]
            result['edges'] = [
                edge for edge in result.get('edges', [])
                if edge['source'] in keep and edge['target'] in keep
            ]
        return result

    def dfs_explore(
        self,
        source_name: str,
        max_depth: int = 3,
        limit_paths: int = 20,
    ) -> dict[str, Any]:
        graph = self._build_graph()
        entity_resolution = self._resolve_entity_candidates(graph, source_name)
        if not entity_resolution.get('ok'):
            return self._error_response(
                f"Entity '{source_name}' not found for DFS exploration.",
                query_type='dfs',
                clarification=[entity_resolution],
            )

        source = entity_resolution['entity']
        visited_paths = []

        def dfs(node: str, path: list[str], depth: int) -> None:
            if len(visited_paths) >= limit_paths or depth > max_depth:
                return
            if len(path) > 1:
                visited_paths.append(path[:])
            if depth == max_depth:
                return

            for edge in graph['out_adj'].get(node, []):
                nxt = edge.target
                if nxt in path:
                    continue
                path.append(nxt)
                dfs(nxt, path, depth + 1)
                path.pop()

        dfs(source, [source], 0)
        nodes, edges = self._subgraph_from_paths(graph, visited_paths)
        return {
            'query_type': 'dfs',
            'nodes': nodes,
            'edges': edges,
            'paths': visited_paths,
            'generated_query': (
                f"MATCH p=(s:Entity {{name:'{source}'}})-[:RELATED_TO*1..{max_depth}]->(t:Entity) RETURN p LIMIT {limit_paths}"
            ),
            'explanation': (
                f"DFS explores outgoing schema-valid relationships from {source} up to depth {max_depth}."
            ),
            'post_validation': {'ok': True, 'errors': []},
            'integrity_issues': graph.get('integrity_issues', [])[:25],
        }
