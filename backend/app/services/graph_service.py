from collections import Counter

import networkx as nx
from sqlalchemy.orm import Session

from app.db.models import Document, Entity, Relationship
from app.schemas.graph import EntityResponse, GraphResponse, GraphSummaryResponse, RelationshipResponse


class GraphServiceError(Exception):
    pass


class GraphNotFoundError(GraphServiceError):
    pass


class GraphBuildError(GraphServiceError):
    pass


class GraphService:
    GLOBAL_DOCUMENT_ID = 0

    def get_document_graph(self, db: Session, document_id: int) -> GraphResponse:
        document = db.query(Document).filter(Document.id == document_id).first()
        if document is None:
            raise GraphNotFoundError("Document graph not found.")

        entities = db.query(Entity).filter(Entity.document_id == document_id).all()
        relationships = db.query(Relationship).filter(Relationship.document_id == document_id).all()

        return GraphResponse(
            document_id=document_id,
            entities=[EntityResponse.model_validate(item) for item in entities],
            relationships=[RelationshipResponse.model_validate(item) for item in relationships],
        )

    def get_global_graph(self, db: Session) -> GraphResponse:
        entities = db.query(Entity).all()
        relationships = db.query(Relationship).all()

        return GraphResponse(
            document_id=self.GLOBAL_DOCUMENT_ID,
            entities=[EntityResponse.model_validate(item) for item in entities],
            relationships=[RelationshipResponse.model_validate(item) for item in relationships],
        )

    def build_networkx_graph(self, db: Session, document_id: int | None = None) -> nx.DiGraph:
        if document_id is not None:
            document = db.query(Document).filter(Document.id == document_id).first()
            if document is None:
                raise GraphNotFoundError("Document graph not found.")

        try:
            graph = nx.DiGraph()

            entity_query = db.query(Entity)
            relationship_query = db.query(Relationship)

            if document_id is not None:
                entity_query = entity_query.filter(Entity.document_id == document_id)
                relationship_query = relationship_query.filter(Relationship.document_id == document_id)

            entities = entity_query.all()
            relationships = relationship_query.all()
            entity_map = {entity.id: entity for entity in entities}

            for entity in entities:
                graph.add_node(
                    entity.id,
                    document_id=entity.document_id,
                    name=entity.name,
                    entity_type=entity.entity_type,
                )

            for relation in relationships:
                if relation.source_entity_id not in entity_map:
                    source_entity = db.query(Entity).filter(Entity.id == relation.source_entity_id).first()
                    if source_entity is not None:
                        entity_map[source_entity.id] = source_entity
                        graph.add_node(
                            source_entity.id,
                            document_id=source_entity.document_id,
                            name=source_entity.name,
                            entity_type=source_entity.entity_type,
                        )

                if relation.target_entity_id not in entity_map:
                    target_entity = db.query(Entity).filter(Entity.id == relation.target_entity_id).first()
                    if target_entity is not None:
                        entity_map[target_entity.id] = target_entity
                        graph.add_node(
                            target_entity.id,
                            document_id=target_entity.document_id,
                            name=target_entity.name,
                            entity_type=target_entity.entity_type,
                        )

                graph.add_edge(
                    relation.source_entity_id,
                    relation.target_entity_id,
                    relationship_id=relation.id,
                    document_id=relation.document_id,
                    relation_type=relation.relation_type,
                    evidence_text=relation.evidence_text,
                )

            return graph
        except GraphNotFoundError:
            raise
        except Exception as exc:
            raise GraphBuildError("Failed to build graph.") from exc

    def get_graph_summary(self, db: Session, document_id: int | None = None) -> GraphSummaryResponse:
        graph = self.build_networkx_graph(db=db, document_id=document_id)

        entity_query = db.query(Entity)
        if document_id is not None:
            entity_query = entity_query.filter(Entity.document_id == document_id)

        entities = entity_query.all()
        name_counts = Counter(item.name for item in entities)
        top_entity_names = [name for name, _ in name_counts.most_common(5)]

        summary_document_id = document_id if document_id is not None else self.GLOBAL_DOCUMENT_ID
        return GraphSummaryResponse(
            document_id=summary_document_id,
            entity_count=graph.number_of_nodes(),
            relationship_count=graph.number_of_edges(),
            top_entity_names=top_entity_names,
        )
