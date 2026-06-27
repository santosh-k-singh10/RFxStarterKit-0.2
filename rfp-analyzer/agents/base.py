"""
agents/base.py
--------------
Shared LLM API call utility used by every sub-agent.

Handles:
  - JSON parsing with markdown fence stripping
  - Exponential backoff retry on transient errors
  - Rate-limit handling (waits 60s then retries)
  - Structured logging of token usage per call
  - Graceful empty-list return on unrecoverable failure

All agents import `call_claude` from here instead of instantiating
their own client.

Updated to use OpenAI-compatible API with IBM Services Essentials.
"""

from __future__ import annotations

import json
import os
import time
from typing import TYPE_CHECKING, Any, Optional

from openai import OpenAI
import structlog
from dotenv import load_dotenv

if TYPE_CHECKING:
    from org_context.context_schema import OrganizationContext

load_dotenv()

log = structlog.get_logger()

# Single shared client — reuse connection pool across all agents
# Using OpenAI-compatible API with IBM Services Essentials endpoint
_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://servicesessentials.ibm.com/apis/v3"),
    timeout=120.0  # 2 minute timeout to prevent indefinite hangs
)

DEFAULT_MODEL      = os.getenv("MODEL_ID", "global/anthropic.claude-sonnet-4-5-20250929-v1:0")
DEFAULT_MAX_TOKENS = 8192  # Increased for extended thinking models
DEFAULT_RETRIES    = 3


def call_claude(
    system_prompt: str,
    user_content: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    retries: int = DEFAULT_RETRIES,
    org_context: Optional[OrganizationContext] = None,
) -> list[dict[str, Any]]:
    """
    Call LLM with a system prompt and user message via OpenAI-compatible API.

    Expects the model to return a JSON array (list of dicts).
    Returns that list, or [] on failure.

    Parameters
    ----------
    system_prompt : str
        The agent's role and extraction instructions.
    user_content : str
        The document chunk text to analyse.
    model : str
        Model identifier.
    max_tokens : int
        Maximum response tokens.
    retries : int
        Number of retry attempts before giving up.
    org_context : Optional[OrganizationContext]
        Organizational context to enhance extraction with domain knowledge.
        If provided, context will be added to the system prompt.

    Returns
    -------
    list[dict]
        Parsed JSON array from the model response, or [] on failure.
    """
    # Enhance system prompt with organizational context if provided
    if org_context:
        system_prompt = enhance_system_prompt_with_context(system_prompt, org_context)
    # DEBUG: Log input content preview
    log.debug(
        "llm_call_input",
        user_content_length=len(user_content),
        user_content_preview=user_content[:300] + "..." if len(user_content) > 300 else user_content,
        system_prompt_length=len(system_prompt),
    )
    
    for attempt in range(1, retries + 1):
        try:
            # Using OpenAI chat completions format
            response = _client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0,
            )

            raw = (response.choices[0].message.content or "").strip()

            log.info(
                "llm_call_ok",
                attempt=attempt,
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                model=model,
            )
            
            # DEBUG: Log the raw response for troubleshooting
            log.debug(
                "llm_raw_response",
                attempt=attempt,
                response_length=len(raw),
                response_preview=raw[:500] + "..." if len(raw) > 500 else raw,
            )

            return _parse_json_response(raw, attempt)

        except Exception as exc:
            # Get status code if available
            status_code = getattr(exc, 'status_code', None)
            
            # Check if it's a rate limit error (status 429)
            if status_code == 429:
                log.warning("rate_limit", attempt=attempt, wait_secs=60)
                if attempt < retries:
                    time.sleep(60)
                    continue
                else:
                    log.error("rate_limit_retries_exhausted", attempt=attempt)
                    break
            
            # Check if it's a server error (5xx)
            if status_code is not None and status_code >= 500:
                log.error("api_status_error", status=status_code, error=str(exc)[:500], attempt=attempt)
                if attempt < retries:
                    _sleep_backoff(attempt)
                    continue
                else:
                    log.error("server_error_retries_exhausted", status=status_code, attempt=attempt)
                    break
            
            # Check if it's a client error (4xx) - don't retry
            if status_code is not None and 400 <= status_code < 500:
                log.error("api_client_error", status=status_code, error=str(exc)[:500])
                break
            
            # Connection errors and timeouts
            if "connection" in str(exc).lower() or "timeout" in str(exc).lower():
                log.warning("connection_error", attempt=attempt, error=str(exc)[:500])
                if attempt < retries:
                    _sleep_backoff(attempt)
                    continue
                else:
                    log.error("connection_error_retries_exhausted", attempt=attempt)
                    break

            # JSON parsing errors
            if isinstance(exc, json.JSONDecodeError):
                log.warning("json_parse_failed", attempt=attempt, error=str(exc))
                if attempt < retries:
                    _sleep_backoff(attempt)
                    continue
                break

            # Unexpected errors
            log.error("unexpected_error", error=str(exc)[:500], type=type(exc).__name__)
            break

    log.error("all_retries_exhausted", retries=retries)
    return []


def _parse_json_response(raw: str, attempt: int = 1) -> list[dict[str, Any]]:
    """
    Strip markdown fences and parse JSON.
    Handles both arrays [] and single objects {} (wraps object in list).
    """
    # DEBUG: Log before processing
    log.debug(
        "json_parse_start",
        attempt=attempt,
        starts_with_fence=raw.startswith("```"),
        first_char=raw[0] if raw else None,
    )
    
    # Strip ```json ... ``` or ``` ... ```
    original_raw = raw
    if raw.startswith("```"):
        lines = raw.split("\n")
        # Remove first line (```json or ```) and last line (```)
        inner_lines = lines[1:] if len(lines) > 1 else lines
        if inner_lines and inner_lines[-1].strip() == "```":
            inner_lines = inner_lines[:-1]
        raw = "\n".join(inner_lines).strip()
        
        log.debug(
            "markdown_fence_stripped",
            attempt=attempt,
            original_length=len(original_raw),
            stripped_length=len(raw),
        )

    try:
        # DEBUG: Show what we're about to parse
        log.debug(
            "attempting_json_parse",
            attempt=attempt,
            json_preview=raw[:300] + "..." if len(raw) > 300 else raw,
        )
        
        parsed = json.loads(raw)

        if isinstance(parsed, dict):
            log.debug("json_parsed_as_dict", attempt=attempt, wrapping_in_list=True)
            return [parsed]
        if isinstance(parsed, list):
            log.debug("json_parsed_as_list", attempt=attempt, count=len(parsed))
            return parsed

        log.warning("json_parsed_unexpected_type", attempt=attempt, type=type(parsed).__name__)
        return []
        
    except json.JSONDecodeError as e:
        # DEBUG: Log detailed error information
        log.error(
            "json_parse_error_details",
            attempt=attempt,
            error_msg=str(e),
            error_line=e.lineno,
            error_column=e.colno,
            error_pos=e.pos,
            raw_length=len(raw),
            raw_sample_at_error=raw[max(0, e.pos-50):e.pos+50] if e.pos else raw[:100],
        )
        
        # Save the malformed JSON to a file for inspection
        try:
            debug_file = f"debug_json_error_attempt_{attempt}.txt"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write("=== MALFORMED JSON ===\n")
                f.write(f"Error: {str(e)}\n")
                f.write(f"Line: {e.lineno}, Column: {e.colno}, Position: {e.pos}\n\n")
                f.write("=== FULL RAW RESPONSE ===\n")
                f.write(raw)
            log.info("json_error_saved_to_file", file=debug_file)
        except Exception as file_exc:
            log.warning("failed_to_save_debug_file", error=str(file_exc))
        
        raise  # Re-raise so it's caught in call_claude


def enhance_system_prompt_with_context(
    base_prompt: str,
    org_context: OrganizationContext
) -> str:
    """
    Enhance system prompt with organizational context.
    
    Adds context at the beginning of the prompt to guide the LLM with:
    - Organization name and industry
    - Technology stack preferences
    - Compliance frameworks
    - Naming conventions
    
    Parameters
    ----------
    base_prompt : str
        The original system prompt
    org_context : OrganizationContext
        Organizational context to include
        
    Returns
    -------
    str
        Enhanced system prompt with context prepended
    """
    # Build context section
    context_lines = [
        "=" * 80,
        "ORGANIZATIONAL CONTEXT",
        "=" * 80,
        f"Organization: {org_context.name}",
        f"Industry: {org_context.industry}",
    ]
    
    if org_context.description:
        context_lines.append(f"Description: {org_context.description}")
    
    context_lines.append("")
    
    # Technology Stack
    if org_context.tech_stack.preferred_languages:
        langs = ", ".join(org_context.tech_stack.preferred_languages[:5])
        context_lines.append(f"Preferred Languages: {langs}")
    
    if org_context.tech_stack.frameworks:
        frameworks = ", ".join(org_context.tech_stack.frameworks[:5])
        context_lines.append(f"Preferred Frameworks: {frameworks}")
    
    if org_context.tech_stack.cloud_providers:
        clouds = ", ".join(org_context.tech_stack.cloud_providers)
        context_lines.append(f"Cloud Providers: {clouds}")
    
    if org_context.tech_stack.databases:
        dbs = ", ".join(org_context.tech_stack.databases[:5])
        context_lines.append(f"Databases: {dbs}")
    
    if org_context.tech_stack.architecture_patterns:
        patterns = ", ".join(org_context.tech_stack.architecture_patterns[:3])
        context_lines.append(f"Architecture Patterns: {patterns}")
    
    # Compliance
    if org_context.compliance.frameworks:
        frameworks = ", ".join(org_context.compliance.frameworks)
        context_lines.append(f"\nCompliance Frameworks: {frameworks}")
    
    if org_context.compliance.certifications:
        certs = ", ".join(org_context.compliance.certifications)
        context_lines.append(f"Certifications: {certs}")
    
    # Naming Conventions
    context_lines.extend([
        f"\nNaming Convention:",
        f"  - Functional: {org_context.naming_conventions.functional_prefix}{org_context.naming_conventions.separator}###",
        f"  - Non-Functional: {org_context.naming_conventions.non_functional_prefix}{org_context.naming_conventions.separator}###",
        f"  - Compliance: {org_context.naming_conventions.compliance_prefix}{org_context.naming_conventions.separator}###",
    ])
    
    # Industry-specific guidance
    context_lines.extend([
        "",
        "CONTEXT-AWARE EXTRACTION GUIDELINES:",
        "1. Map technology mentions to the organization's preferred tech stack",
        "2. Identify compliance requirements specific to their frameworks",
        "3. Use their naming conventions for requirement IDs",
        "4. Consider industry-specific terminology and standards",
        "5. Align recommendations with their architecture patterns",
        "6. Reference their existing infrastructure when applicable",
    ])
    
    # Add industry-specific notes
    industry_lower = org_context.industry.lower()
    if "health" in industry_lower or "medical" in industry_lower:
        context_lines.extend([
            "",
            "HEALTHCARE-SPECIFIC NOTES:",
            "- PHI (Protected Health Information) = any patient identifiable data",
            "- HIPAA compliance is mandatory for all patient data handling",
            "- HL7/FHIR are standard healthcare data exchange protocols",
            "- EHR = Electronic Health Record system",
        ])
    elif "financ" in industry_lower or "bank" in industry_lower:
        context_lines.extend([
            "",
            "FINANCE-SPECIFIC NOTES:",
            "- PCI-DSS compliance required for payment card data",
            "- SOX compliance for financial reporting",
            "- KYC (Know Your Customer) and AML (Anti-Money Laundering) are regulatory",
        ])
    
    context_lines.extend([
        "=" * 80,
        "",
    ])
    
    context_section = "\n".join(context_lines)
    
    log.debug(
        "context_enhanced_prompt",
        org_name=org_context.name,
        industry=org_context.industry,
        context_length=len(context_section),
    )
    
    return context_section + base_prompt


def _sleep_backoff(attempt: int) -> None:
    """Exponential backoff: 2s, 4s, 8s …"""
    wait = 2 ** attempt
    log.info("backoff_sleep", seconds=wait)
    time.sleep(wait)