import re

import networkx as nx
from sqlalchemy.orm import Session

from app.db.models import Entity, Relationship
from app.schemas.query import GraphQueryResponse, PathStep
from app.services.graph_service import GraphBuildError, GraphNotFoundError, GraphService


class QueryServiceError(Exception):
    pass


class InvalidQuestionError(QueryServiceError):
    pass


class QueryService:
    FALLBACK_ANSWER = "The answer could not be determined from the extracted graph."

    RELATION_KEYWORDS = {
        "collaborates with": "COLLABORATES_WITH",
        "partners with": "COLLABORATES_WITH",
        "works with": "COLLABORATES_WITH",
        "build": "BUILDS",
        "builds": "BUILDS",
        "creates": "BUILDS",
        "develops": "BUILDS",
        "produces": "BUILDS",
        "use": "USES",
        "uses": "USES",
        "relies on": "USES",
        "depends on": "USES",
        "supports": "SUPPORTS",
        "enables": "SUPPORTS",
        "powers": "SUPPORTS",
        "part of": "PART_OF",
        "belongs to": "PART_OF",
        "member of": "PART_OF",
        "founded": "LEADS",
        "leads": "LEADS",
        "manages": "LEADS",
        "owns": "OWNS",
        "friends with": "FRIEND_OF",
        "best friend": "FRIEND_OF",
        "related to": "FRIEND_OF",
        "located in": "LOCATED_IN",
        "based in": "LOCATED_IN",
        "operates in": "LOCATED_IN",
    }

    BOTH_DIRECTION_RELATIONS = {"COLLABORATES_WITH", "FRIEND_OF"}

    def __init__(self) -> None:
        self.graph_service = GraphService()

    def answer_question(self, db: Session, question: str, document_id: int | None = None) -> GraphQueryResponse:
        cleaned_question = question.strip()
        if not cleaned_question:
            raise InvalidQuestionError("Question must not be empty.")

        question_lower = cleaned_question.lower()
        graph = self.graph_service.build_networkx_graph(db=db, document_id=document_id)
        scoped_entities = self._get_scoped_entities(db=db, document_id=document_id)
        matched_entities = self._match_entities(cleaned_question, scoped_entities)

        if self._is_path_question(question_lower) and len(matched_entities) >= 2:
            return self._answer_path_question(graph=graph, matched_entities=matched_entities, question=cleaned_question)

        relation_type = self._detect_relation_type(question_lower)
        if relation_type and matched_entities:
            response = self._answer_direct_relationship_question(
                db=db,
                graph=graph,
                question=cleaned_question,
                matched_entities=matched_entities,
                relation_type=relation_type,
                document_id=document_id,
            )
            if response is not None:
                return response

        if self._is_neighborhood_question(question_lower) and matched_entities:
            response = self._answer_neighborhood_question(
                db=db,
                graph=graph,
                question=cleaned_question,
                matched_entities=matched_entities,
                document_id=document_id,
            )
            if response is not None:
                return response

        if not matched_entities:
            return GraphQueryResponse(
                question=cleaned_question,
                answer="No matching entities were found in the graph for this question.",
                matched_entities=[],
                paths=[],
            )

        return GraphQueryResponse(
            question=cleaned_question,
            answer=self.FALLBACK_ANSWER,
            matched_entities=matched_entities,
            paths=[],
        )

    def _get_scoped_entities(self, db: Session, document_id: int | None) -> list[Entity]:
        query = db.query(Entity)
        if document_id is not None:
            query = query.filter(Entity.document_id == document_id)
        return query.all()

    def _match_entities(self, question: str, entities: list[Entity]) -> list[str]:
        lowered_question = question.lower().replace("'s", "")

        candidates = []
        for entity in entities:
            name = entity.name.strip()
            if not name:
                continue

            probe_names = {name.lower(), name.lower().replace("'s", "")}
            for probe in probe_names:
                index = lowered_question.find(probe)
                if index >= 0:
                    candidates.append((index, -len(name), name))
                    break

        candidates.sort()
        ordered_unique = []
        seen = set()
        for _, _, name in candidates:
            key = name.lower()
            if key not in seen:
                seen.add(key)
                ordered_unique.append(name)

        reduced = []
        for name in ordered_unique:
            lower_name = name.lower()
            if any(lower_name in kept.lower() for kept in reduced):
                continue
            reduced.append(name)

        return reduced

    @staticmethod
    def _is_path_question(question_lower: str) -> bool:
        return "how is" in question_lower and ("connected to" in question_lower or "related to" in question_lower)

    @staticmethod
    def _is_neighborhood_question(question_lower: str) -> bool:
        return (
            "connected to" in question_lower
            or "related to" in question_lower
            or "which entities are related to" in question_lower
            or "what is connected to" in question_lower
            or "what is related to" in question_lower
        )

    def _detect_relation_type(self, question_lower: str) -> str | None:
        for keyword, relation_type in self.RELATION_KEYWORDS.items():
            if keyword in question_lower:
                return relation_type
        return None

    def _answer_path_question(self, graph: nx.DiGraph, matched_entities: list[str], question: str) -> GraphQueryResponse:
        source_name = matched_entities[0]
        target_name = matched_entities[1]

        source_ids = self._find_node_ids_by_name(graph, source_name)
        target_ids = self._find_node_ids_by_name(graph, target_name)

        if not source_ids or not target_ids:
            return GraphQueryResponse(
                question=question,
                answer="No matching entities were found in the graph for this question.",
                matched_entities=matched_entities,
                paths=[],
            )

        path_nodes: list[int] | None = None
        try:
            for source_id in source_ids:
                for target_id in target_ids:
                    candidate = nx.shortest_path(graph.to_undirected(), source=source_id, target=target_id)
                    if path_nodes is None or len(candidate) < len(path_nodes):
                        path_nodes = candidate
        except nx.NetworkXNoPath:
            path_nodes = None

        if path_nodes is None:
            return GraphQueryResponse(
                question=question,
                answer="No connection path was found between the requested entities.",
                matched_entities=matched_entities,
                paths=[],
            )

        path_steps: list[PathStep] = []
        for i in range(len(path_nodes) - 1):
            a = path_nodes[i]
            b = path_nodes[i + 1]

            if graph.has_edge(a, b):
                edge_data = graph.get_edge_data(a, b)
                source_node = graph.nodes[a]
                target_node = graph.nodes[b]
            else:
                edge_data = graph.get_edge_data(b, a)
                source_node = graph.nodes[b]
                target_node = graph.nodes[a]

            path_steps.append(
                PathStep(
                    source_entity=source_node.get("name", ""),
                    relation_type=edge_data.get("relation_type", "RELATED_TO"),
                    target_entity=target_node.get("name", ""),
                    evidence_text=edge_data.get("evidence_text"),
                )
            )

        answer = f"{source_name} is connected to {target_name} through {len(path_steps)} relationship step(s)."
        return GraphQueryResponse(question=question, answer=answer, matched_entities=matched_entities, paths=path_steps)

    def _answer_direct_relationship_question(
        self,
        db: Session,
        graph: nx.DiGraph,
        question: str,
        matched_entities: list[str],
        relation_type: str,
        document_id: int | None,
    ) -> GraphQueryResponse | None:
        focus_name = matched_entities[-1]
        focus_ids = set(self._find_node_ids_by_name(graph, focus_name))
        if not focus_ids:
            return None

        question_lower = question.lower()
        relation_query = db.query(Relationship).filter(Relationship.relation_type == relation_type)
        if document_id is not None:
            relation_query = relation_query.filter(Relationship.document_id == document_id)
        relation_rows = relation_query.all()

        candidates: list[PathStep] = []
        seen_steps: set[tuple[str, str, str, str]] = set()
        want_incoming = self._is_incoming_query(question_lower, relation_type)
        want_outgoing = self._is_outgoing_query(question_lower, relation_type)

        for row in relation_rows:
            include = False

            if relation_type in self.BOTH_DIRECTION_RELATIONS:
                include = row.source_entity_id in focus_ids or row.target_entity_id in focus_ids
            elif want_incoming:
                include = row.target_entity_id in focus_ids
            elif want_outgoing:
                include = row.source_entity_id in focus_ids
            else:
                include = row.source_entity_id in focus_ids or row.target_entity_id in focus_ids

            if not include:
                continue

            source_name = graph.nodes[row.source_entity_id]["name"] if row.source_entity_id in graph else ""
            target_name = graph.nodes[row.target_entity_id]["name"] if row.target_entity_id in graph else ""
            if not source_name or not target_name:
                continue

            dedupe_key = (source_name.lower(), row.relation_type.upper(), target_name.lower(), (row.evidence_text or "").strip())
            if dedupe_key in seen_steps:
                continue
            seen_steps.add(dedupe_key)

            candidates.append(
                PathStep(
                    source_entity=source_name,
                    relation_type=row.relation_type,
                    target_entity=target_name,
                    evidence_text=row.evidence_text,
                )
            )

        if not candidates:
            return GraphQueryResponse(
                question=question,
                answer=self.FALLBACK_ANSWER,
                matched_entities=matched_entities,
                paths=[],
            )

        related_names = sorted(
            {
                step.target_entity if step.source_entity.lower() == focus_name.lower() else step.source_entity
                for step in candidates
            }
        )
        answer = f"{focus_name} has {len(candidates)} matching {relation_type} relationship(s): {', '.join(related_names)}."

        return GraphQueryResponse(question=question, answer=answer, matched_entities=matched_entities, paths=candidates)

    def _answer_neighborhood_question(
        self,
        db: Session,
        graph: nx.DiGraph,
        question: str,
        matched_entities: list[str],
        document_id: int | None,
    ) -> GraphQueryResponse | None:
        focus_name = matched_entities[-1]
        focus_ids = set(self._find_node_ids_by_name(graph, focus_name))
        if not focus_ids:
            return None

        relation_query = db.query(Relationship).filter(
            Relationship.source_entity_id.in_(focus_ids) | Relationship.target_entity_id.in_(focus_ids)
        )
        if document_id is not None:
            relation_query = relation_query.filter(Relationship.document_id == document_id)
        relation_rows = relation_query.all()

        steps: list[PathStep] = []
        for row in relation_rows:
            source_name = graph.nodes[row.source_entity_id]["name"] if row.source_entity_id in graph else ""
            target_name = graph.nodes[row.target_entity_id]["name"] if row.target_entity_id in graph else ""
            if not source_name or not target_name:
                continue
            steps.append(
                PathStep(
                    source_entity=source_name,
                    relation_type=row.relation_type,
                    target_entity=target_name,
                    evidence_text=row.evidence_text,
                )
            )

        if not steps:
            return GraphQueryResponse(
                question=question,
                answer=self.FALLBACK_ANSWER,
                matched_entities=matched_entities,
                paths=[],
            )

        neighbor_names = sorted(
            {
                step.target_entity if step.source_entity.lower() == focus_name.lower() else step.source_entity
                for step in steps
            }
        )
        answer = f"{focus_name} is connected to {len(neighbor_names)} entity(ies): {', '.join(neighbor_names)}."

        return GraphQueryResponse(question=question, answer=answer, matched_entities=matched_entities, paths=steps)

    @staticmethod
    def _is_incoming_query(question_lower: str, relation_type: str) -> bool:
        incoming_markers = {
            "SUPPORTS": ["what supports", "who supports"],
            "PART_OF": ["what is part of", "who is part of", "what belongs to"],
            "LEADS": ["who founded", "who leads", "who manages"],
            "FRIEND_OF": ["best friend", "friends with"],
            "LOCATED_IN": ["what is located in", "who is located in", "what is based in"],
            "OWNS": ["who owns"],
        }
        markers = incoming_markers.get(relation_type, [])
        return any(marker in question_lower for marker in markers)

    @staticmethod
    def _is_outgoing_query(question_lower: str, relation_type: str) -> bool:
        if relation_type in {"BUILDS", "USES", "OWNS", "LEADS", "LOCATED_IN"} and "does" in question_lower:
            return True
        if relation_type == "PART_OF" and ("is part of" in question_lower or "belongs to" in question_lower):
            return True
        return False

    @staticmethod
    def _find_node_ids_by_name(graph: nx.DiGraph, entity_name: str) -> list[int]:
        probe = entity_name.strip().lower().replace("'s", "")
        matched: list[int] = []
        for node_id, attrs in graph.nodes(data=True):
            name = str(attrs.get("name", "")).strip().lower()
            if name == probe or name.replace("'s", "") == probe:
                matched.append(int(node_id))
        return matched


__all__ = [
    "QueryService",
    "QueryServiceError",
    "InvalidQuestionError",
    "GraphBuildError",
    "GraphNotFoundError",
]
