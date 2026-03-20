import re
from collections import OrderedDict


class ExtractionService:
    ENTITY_REL_PATTERN = r"[A-Z][A-Za-z0-9'&.-]*(?:\s+[A-Za-z][A-Za-z0-9'&.-]*){0,5}"

    RELATION_PATTERN_DEFS = [
        ("COLLABORATES_WITH", ["collaborates with", "partners with", "works with"]),
        ("BUILDS", ["builds", "creates", "develops", "produces"]),
        ("USES", ["uses", "relies on", "depends on"]),
        ("SUPPORTS", ["supports", "enables", "powers"]),
        ("PART_OF", ["is part of", "belongs to", "member of"]),
        ("OWNS", ["owns"]),
        ("LEADS", ["leads", "manages", "founded"]),
        ("FRIEND_OF", ["is friends with", "are best friends with", "is related to"]),
        ("LOCATED_IN", ["is located in", "based in", "operates in"]),
    ]

    ENTITY_MULTIWORD_PATTERN = re.compile(r"\b[A-Z][a-zA-Z0-9'&.-]+(?:\s+[A-Za-z][a-zA-Z0-9'&.-]+)+\b")
    ENTITY_SINGLE_PATTERN = re.compile(r"\b[A-Z][a-zA-Z0-9'&.-]{2,}\b")
    ORGANIZATION_MARKERS = {
        "inc",
        "corp",
        "llc",
        "ltd",
        "company",
        "university",
        "institute",
        "labs",
        "systems",
        "group",
        "organization",
        "foundation",
    }
    NON_ENTITY_WORDS = {"The", "This", "That", "These", "Those", "And", "But", "For", "With", "From", "Into"}

    def __init__(self) -> None:
        self.relation_patterns = self._build_relation_patterns()

    def extract(self, document_id: int, text: str) -> dict[str, list[dict[str, str | int | None]]]:
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]

        entities = OrderedDict()
        relationships: list[dict[str, str | int | None]] = []
        seen_relations: set[tuple[str, str, str, str]] = set()

        for sentence in sentences:
            for name in self._extract_entities_from_sentence(sentence):
                key = name.lower()
                if key not in entities:
                    entities[key] = {
                        "document_id": document_id,
                        "name": name,
                        "entity_type": self.infer_entity_type(name),
                    }

            for pattern, relation_type in self.relation_patterns:
                for match in pattern.finditer(sentence):
                    source_name = self._normalize_entity_name(match.group("source"))
                    target_name = self._normalize_entity_name(match.group("target"))

                    if not source_name or not target_name:
                        continue
                    if source_name.lower() == target_name.lower():
                        continue

                    source_key = source_name.lower()
                    target_key = target_name.lower()

                    if source_key not in entities:
                        entities[source_key] = {
                            "document_id": document_id,
                            "name": source_name,
                            "entity_type": self.infer_entity_type(source_name),
                        }
                    if target_key not in entities:
                        entities[target_key] = {
                            "document_id": document_id,
                            "name": target_name,
                            "entity_type": self.infer_entity_type(target_name),
                        }

                    relation_key = (source_key, target_key, relation_type, sentence)
                    if relation_key in seen_relations:
                        continue
                    seen_relations.add(relation_key)

                    relationships.append(
                        {
                            "document_id": document_id,
                            "source_name": source_name,
                            "target_name": target_name,
                            "relation_type": relation_type,
                            "evidence_text": sentence,
                        }
                    )

        return {"entities": list(entities.values()), "relationships": relationships}

    def infer_entity_type(self, name: str) -> str:
        tokens = name.split()
        token_set = {token.strip(".,").lower() for token in tokens}

        if token_set.intersection(self.ORGANIZATION_MARKERS):
            return "ORGANIZATION"

        if len(tokens) in {2, 3} and all(token[:1].isupper() for token in tokens):
            return "PERSON"

        return "CONCEPT"

    def _extract_entities_from_sentence(self, sentence: str) -> list[str]:
        candidates = []

        for match in self.ENTITY_MULTIWORD_PATTERN.finditer(sentence):
            candidates.append(match.group(0))

        for match in self.ENTITY_SINGLE_PATTERN.finditer(sentence):
            token = match.group(0)
            if token in self.NON_ENTITY_WORDS:
                continue
            candidates.append(token)

        normalized = OrderedDict()
        for candidate in candidates:
            name = self._normalize_entity_name(candidate)
            if not name:
                continue
            key = name.lower()
            if key not in normalized:
                normalized[key] = name

        return list(normalized.values())

    def _build_relation_patterns(self) -> list[tuple[re.Pattern[str], str]]:
        compiled: list[tuple[re.Pattern[str], str]] = []
        for canonical, phrases in self.RELATION_PATTERN_DEFS:
            for phrase in phrases:
                pattern = re.compile(
                    rf"(?P<source>{self.ENTITY_REL_PATTERN})\s+{re.escape(phrase)}\s+(?P<target>{self.ENTITY_REL_PATTERN})",
                    re.IGNORECASE,
                )
                compiled.append((pattern, canonical))
        return compiled

    @staticmethod
    def _normalize_entity_name(value: str) -> str:
        cleaned = re.sub(r"\s+", " ", value).strip(" ,.;:\n\t")
        return cleaned
