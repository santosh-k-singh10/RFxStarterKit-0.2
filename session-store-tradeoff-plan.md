# Plan: Document Session Store as a Deliberate MVP Tradeoff

## Top-Level Overview

A reviewer flagged that `rfp-analyzer/app/session_store.py` presents its in-memory
implementation as an afterthought (`# In-memory store (replace with Redis in production)`)
rather than as a deliberate, scoped decision.

The fix is **entirely documentation and presentation** — not a Redis implementation.
The goal is to make it unambiguous to any reader (reviewer, contributor, or future
engineer) that:
- The in-memory store is a **deliberate MVP choice** bounded by known constraints
- The project already has a migration path (Redis blueprint in the same file)
- The horizontal-scaling limitation is surfaced in the right places (ADR, architecture
  doc, Docker guide)

No new runtime behaviour is introduced. A small syntax error in the commented-out
Redis block is fixed in-place.

---

## Sub-Tasks

---

### Sub-Task 1 — Upgrade the `session_store.py` module docstring & inline comments

**Intent**
Replace the single throwaway comment with a structured module-level docstring that
names the tradeoff, the current constraints, and exactly what must change to move to
Redis. Also fix the syntax error in the commented-out Redis block (`if` statement
missing its condition).

**Expected Outcomes**
- `rfp-analyzer/app/session_store.py` opens with a docstring that clearly states:
  - This is MVP / single-instance scope
  - Known limitations (no persistence across restarts, not multi-instance safe)
  - What the Redis path looks like and which env vars drive it
- The `# In-memory store (replace with Redis in production)` comment is removed or
  replaced by something that points to the docstring
- The Redis code block at the bottom has its syntax error corrected
  (`if data:` instead of bare `if`)

**Todo List**
1. Read `rfp-analyzer/app/session_store.py` (already read; no re-read needed)
2. Replace module docstring at the top of the file with the expanded version
3. Remove the bare `# In-memory store (replace with Redis in production)` comment
   above `_store` and replace with a short inline note referencing the docstring
4. Fix the syntax error in the commented Redis block (`if` → `if data:`)

**Relevant Context**
- File: `rfp-analyzer/app/session_store.py`
- Current docstring lines 1–7 (too brief)
- `_store` dict declared at line ~17 with the offending comment
- Redis block starts at line ~87; `if` at line ~183 is incomplete

**Status:** [ ] pending

---

### Sub-Task 2 — Add ADR-0004: Session Store — In-Memory MVP with Redis Migration Path

**Intent**
Give the session-store decision the same formal treatment that ADR-0002 gave to
LangGraph orchestration. A reviewer reading the ADR directory should see that the
in-memory choice was a conscious, bounded decision — not an oversight.

**Expected Outcomes**
- New file `docs/adr/ADR-0004-session-store-mvp.md` exists with:
  - Status, Date, Deciders header
  - **Context** — single-instance local tool scope; Redis adds operational overhead
    not justified for MVP
  - **Decision** — in-memory dict; bounded to single-process, single-instance
  - **Alternatives Considered** table — Redis, SQLite, filesystem pickle; why each
    was deferred
  - **Consequences** — explicit list of known limitations + the migration trigger
    conditions
  - **Migration Path** — numbered steps from in-memory → Redis (env var, package,
    swap implementation, update docker-compose)
- `docs/adr/README.md` index table updated to include ADR-0004

**Todo List**
1. Write `docs/adr/ADR-0004-session-store-mvp.md` following the existing ADR format
   (same structure as ADR-0002)
2. Update the index table in `docs/adr/README.md` to add the new ADR row

**Relevant Context**
- Template: `docs/adr/ADR-0002-multi-agent-langgraph.md` (same format)
- Index: `docs/adr/README.md`
- Alternatives to document: Redis (deferred — ops overhead), SQLite (available but
  overkill for transient session state), filesystem pickle (fragile)
- Migration trigger: multi-instance deployment (Docker scaling > 1 replica)
- Redis env vars already defined in the commented block: `REDIS_HOST`, `REDIS_PORT`

**Status:** [ ] pending

---

### Sub-Task 3 — Add "State & Session Management" section to ARCHITECTURE.md

**Intent**
`docs/ARCHITECTURE.md` covers data flow and LangGraph checkpointing but has no section
on how web-request session state is managed. Adding one means the architecture doc is
the single source of truth for the full state story.

**Expected Outcomes**
- A new "State & Session Management" section added to `docs/ARCHITECTURE.md` that:
  - Distinguishes the two types of state: LangGraph pipeline state (SQLite checkpoint)
    vs. web-session state (in-memory / Redis)
  - States the current scope (single-instance MVP) and cross-references ADR-0004
  - Describes what triggers the upgrade to Redis (multi-replica deployment)
- The ADR table in `docs/ARCHITECTURE.md` (lines 125–129) updated to include ADR-0004

**Todo List**
1. Read `docs/ARCHITECTURE.md` lines 119–170 to find the right insertion point
   (after Key Design Decisions table, before Repository Structure)
2. Insert the new section
3. Add ADR-0004 row to the Key Design Decisions table

**Relevant Context**
- File: `docs/ARCHITECTURE.md`
- Insert after the Key Design Decisions table (~line 130) and before Repository
  Structure (~line 132)
- Cross-reference: `docs/adr/ADR-0004-session-store-mvp.md`

**Status:** [ ] pending

---

### Sub-Task 4 — Add scaling caveat to the Docker Guide

**Intent**
`docs/DOCKER_GUIDE.md` already shows `docker-compose up --scale rfp-analyzer=3` but
gives no warning that this breaks session affinity with the in-memory store. A reader
following that instruction will encounter silent session-loss bugs. Adding a short
caveat surfaces the known limitation at the exact place it matters.

**Expected Outcomes**
- The "Scaling" section in `docs/DOCKER_GUIDE.md` (around line 276) has a callout
  block (or `> **Note:**` blockquote) immediately after the scale command that:
  - States that the default in-memory session store is not safe with > 1 replica
  - Points to ADR-0004 for the Redis migration path

**Todo List**
1. Read `docs/DOCKER_GUIDE.md` lines 276–285 to get exact insertion point
2. Insert the caveat note immediately after the scale command block

**Relevant Context**
- File: `docs/DOCKER_GUIDE.md`
- Scaling section at lines 276–284
- Keep the note short (2–3 lines) — this is a guide, not the ADR

**Status:** [ ] pending

---

## Notes for Implementation

- Sub-tasks 1–4 are independent and can be done in any order
- Sub-task 2 should be completed before sub-task 3 (so the ADR file exists when
  ARCHITECTURE.md links to it)
- No new Python packages, no config changes, no runtime behaviour changes
- The Redis commented block in `session_store.py` stays commented — it is the
  migration blueprint, not production code
