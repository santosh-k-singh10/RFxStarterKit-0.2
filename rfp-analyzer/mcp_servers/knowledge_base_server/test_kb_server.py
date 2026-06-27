"""
Test Script for Knowledge Base MCP Server
------------------------------------------
Tests the Knowledge Base server functionality without requiring full MCP setup.
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
        sys.stderr.reconfigure(encoding='utf-8')  # type: ignore

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_servers.knowledge_base_server.server import KnowledgeBaseServer
import json


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_search_org_knowledge():
    """Test searching organizational knowledge."""
    print_section("Test 1: Search Organizational Knowledge")
    
    kb = KnowledgeBaseServer(context_root="./org_context")
    
    # Test search for authentication
    print("\n[SEARCH] Searching for 'authentication'...")
    results = kb.search_org_knowledge("authentication", category="all", top_k=3)
    
    print(f"\n[OK] Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. File: {result['file']}")
        print(f"     Category: {result['category']}")
        print(f"     Relevance: {result['relevance']}")
        print(f"     Excerpt: {result['excerpt'][:100]}...")
    
    return len(results) > 0


def test_get_compliance_standard():
    """Test retrieving compliance standards."""
    print_section("Test 2: Get Compliance Standard")
    
    kb = KnowledgeBaseServer(context_root="./org_context")
    
    # Test HIPAA standard
    print("\n[SEARCH] Retrieving HIPAA compliance standard...")
    result = kb.get_compliance_standard("HIPAA")
    
    if result:
        print(f"\n[OK] Found standard:")
        print(f"   Framework: {result['framework']}")
        print(f"   File: {result['file']}")
        print(f"   Content length: {len(result['content'])} characters")
        if 'note' in result:
            print(f"   Note: {result['note']}")
        return True
    else:
        print("\n[WARN] HIPAA standard not found")
        return False


def test_find_similar_rfps():
    """Test finding similar past RFPs."""
    print_section("Test 3: Find Similar Past RFPs")
    
    kb = KnowledgeBaseServer(context_root="./org_context")
    
    # Test with healthcare-related description
    description = "Healthcare patient portal with secure authentication and HIPAA compliance"
    print(f"\n[SEARCH] Finding RFPs similar to: '{description}'...")
    
    results = kb.find_similar_past_rfps(description, top_k=3)
    
    print(f"\n[OK] Found {len(results)} similar RFPs:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. File: {result['file']}")
        print(f"     Similarity: {result['similarity']:.2%}")
        print(f"     Excerpt: {result['excerpt'][:150]}...")
    
    return len(results) > 0


def test_index_document():
    """Test indexing a new document."""
    print_section("Test 4: Index Document")
    
    kb = KnowledgeBaseServer(context_root="./org_context")
    
    # Create a test document
    test_file = Path("./org_context/test_document.md")
    test_content = """# Test Document

This is a test document for the knowledge base.

## Security Requirements
- Authentication required
- HTTPS only
- Data encryption at rest
"""
    
    print("\n[CREATE] Creating test document...")
    test_file.write_text(test_content)
    print(f"   Created: {test_file}")
    
    # Index the document
    print("\n[INDEX] Indexing document...")
    result = kb.index_document(
        str(test_file),
        category="standards",
        metadata={"type": "test", "created": "2024-01-01"}
    )
    
    print(f"\n[OK] Indexing result:")
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Indexed path: {result['indexed_path']}")
        print(f"   Category: {result['category']}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Cleanup
    if test_file.exists():
        test_file.unlink()
        print(f"\n[CLEANUP] Cleaned up test file")
    
    return result['success']


def test_knowledge_base_stats():
    """Display knowledge base statistics."""
    print_section("Knowledge Base Statistics")
    
    kb = KnowledgeBaseServer(context_root="./org_context")
    
    # Count files in each category
    categories = {
        "Standards": kb.standards_dir,
        "Examples": kb.examples_dir,
        "Domain Knowledge": kb.domain_knowledge_dir
    }
    
    print("\n[STATS] Knowledge Base Contents:")
    total_files = 0
    for name, directory in categories.items():
        if directory.exists():
            md_files = list(directory.rglob("*.md"))
            total_files += len(md_files)
            print(f"\n  {name}:")
            print(f"    Directory: {directory}")
            print(f"    Files: {len(md_files)}")
            if md_files:
                for f in md_files[:3]:  # Show first 3 files
                    print(f"      - {f.relative_to(kb.context_root)}")
                if len(md_files) > 3:
                    print(f"      ... and {len(md_files) - 3} more")
        else:
            print(f"\n  {name}: Directory not found")
    
    print(f"\n  Total files: {total_files}")
    return total_files > 0


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  KNOWLEDGE BASE MCP SERVER - TEST SUITE")
    print("=" * 70)
    
    results = {
        "Knowledge Base Stats": test_knowledge_base_stats(),
        "Search Org Knowledge": test_search_org_knowledge(),
        "Get Compliance Standard": test_get_compliance_standard(),
        "Find Similar RFPs": test_find_similar_rfps(),
        "Index Document": test_index_document(),
    }
    
    # Summary
    print_section("Test Summary")
    print()
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}  {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  [SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n  [WARNING] {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
