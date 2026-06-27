"""
phase0/classifier.py
Classifier Agent — detects document type and confidence score for each uploaded file.

Strategy:
- Extracts text from PDF / DOCX
- Sends first ~3 pages to LLM with a typed classification prompt
- Returns ClassifiedDocument with doc_type + confidence
- Flags low-confidence docs for human review
"""

from __future__ import annotations
import json
import logging
import re
from pathlib import Path
from typing import Tuple

import anthropic

from .schema import ClassifiedDocument, DocType
from .utils import extract_text_from_file, count_pages

logger = logging.getLogger(__name__)

# Confidence below this threshold → needs_review = True
CONFIDENCE_THRESHOLD = 0.70

# How many characters from the start of the document to send for classification
CLASSIFICATION_PREVIEW_CHARS = 4000


CLASSIFICATION_PROMPT = """You are a document classifier for RFP (Request for Proposal) packs.

Classify the following document excerpt into exactly ONE of these types:
- technical_spec        : Technical requirements, system specifications, functional/non-functional requirements
- compliance            : Regulatory, legal, security compliance requirements
- pricing_template      : Pricing sheets, cost tables, commercial schedules
- cover_letter          : Executive summary, introduction letter, procurement notice
- reference_architecture: Architecture diagrams, reference designs, technology standards
- statement_of_work     : SOW, scope of work, deliverables definition
- terms_and_conditions  : Legal terms, contract conditions, SLAs
- unknown               : Cannot be determined from the excerpt

Respond ONLY with a JSON object in this exact format (no markdown, no explanation):
{{
  "doc_type": "<one of the types above>",
  "confidence": <float between 0.0 and 1.0>,
  "reasoning": "<one sentence explaining your classification>"
}}

Document excerpt:
---
{text}
---"""


class ClassifierAgent:
    """
    Classifies each uploaded document into a DocType.
    Uses Anthropic Claude via the standard client or OpenAI-compatible API.
    """

    def __init__(self, client = None):
        """
        Initialize ClassifierAgent with an LLM client.
        
        Args:
            client: Anthropic client or OpenAI-compatible wrapper. If None, uses get_anthropic_client().
        """
        if client is None:
            from .llm_client import get_anthropic_client
            client = get_anthropic_client()
        self.client = client

    def classify(self, filepath: str | Path) -> ClassifiedDocument:
        """
        Main entry point. Extracts text from file and classifies it.

        Args:
            filepath: Path to the uploaded file (.pdf, .docx, .txt)

        Returns:
            ClassifiedDocument with doc_type, confidence, and raw_text
        """
        filepath = Path(filepath)
        logger.info(f"Classifying: {filepath.name}")

        raw_text = extract_text_from_file(filepath)
        pages = count_pages(filepath)

        if not raw_text.strip():
            logger.warning(f"Empty text extracted from {filepath.name}")
            return ClassifiedDocument(
                filename=filepath.name,
                doc_type=DocType.UNKNOWN,
                confidence=0.0,
                raw_text="",
                pages=pages,
                needs_review=True,
            )

        doc_type, confidence, reasoning = self._call_llm(raw_text)
        needs_review = confidence < CONFIDENCE_THRESHOLD

        logger.info(
            f"{filepath.name} → {doc_type.value} "
            f"(confidence={confidence:.2f}, review={needs_review})"
        )
        if needs_review:
            logger.warning(f"Low confidence on {filepath.name}: {reasoning}")

        return ClassifiedDocument(
            filename=filepath.name,
            doc_type=doc_type,
            confidence=confidence,
            raw_text=raw_text,
            pages=pages,
            needs_review=needs_review,
        )

    def _call_llm(self, raw_text: str) -> Tuple[DocType, float, str]:
        """
        Sends document preview to Claude and parses the classification response.

        Returns:
            (doc_type, confidence, reasoning)
        """
        preview = raw_text[:CLASSIFICATION_PREVIEW_CHARS]
        prompt = CLASSIFICATION_PROMPT.format(text=preview)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            text_parts = []
            for block in response.content:
                if getattr(block, "type", None) == "text":
                    text_value = getattr(block, "text", "")
                    if isinstance(text_value, str):
                        text_parts.append(text_value)
            content = "".join(text_parts).strip()
            return self._parse_response(content)

        except Exception as e:
            logger.error(f"LLM call failed during classification: {e}")
            return DocType.UNKNOWN, 0.0, f"LLM error: {e}"

    def _parse_response(self, content: str) -> Tuple[DocType, float, str]:
        """Parses LLM JSON response into typed values."""
        # Strip any accidental markdown fences
        content = re.sub(r"```(?:json)?|```", "", content).strip()

        try:
            data = json.loads(content)
            raw_type = data.get("doc_type", "unknown").strip().lower()
            # Map to enum, fall back to UNKNOWN if value is unrecognised
            try:
                doc_type = DocType(raw_type)
            except ValueError:
                doc_type = DocType.UNKNOWN

            confidence = float(data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))  # clamp
            reasoning = data.get("reasoning", "")
            return doc_type, confidence, reasoning

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Failed to parse classifier response: {e}\nRaw: {content}")
            return DocType.UNKNOWN, 0.0, "Parse error"
