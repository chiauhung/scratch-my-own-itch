#!/usr/bin/env python3
"""
Quick test script to verify the Search API is working
"""

import requests
import json

API_BASE = "http://localhost:8080"

def test_health():
    """Test API health check"""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"✓ API is up: {response.json()}")
        return True
    except Exception as e:
        print(f"✗ API not responding: {e}")
        return False

def test_collections():
    """Test listing collections"""
    print("\nTesting collections endpoint...")
    try:
        response = requests.get(f"{API_BASE}/collections")
        data = response.json()
        print(f"✓ Collections: {data['collections']}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_search(query="vector databases"):
    """Test semantic search"""
    print(f"\nTesting search with query: '{query}'...")
    try:
        response = requests.post(
            f"{API_BASE}/search",
            json={"query": query, "n_results": 3}
        )
        data = response.json()
        print(f"✓ Found {data['count']} results")
        for result in data['results'][:2]:  # Show first 2
            print(f"  - {result['title']} ({result['url']})")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_ask(question="What is this article about?"):
    """Test RAG Q&A"""
    print(f"\nTesting Q&A with question: '{question}'...")
    try:
        response = requests.post(
            f"{API_BASE}/ask",
            json={"question": question, "n_results": 3}
        )
        data = response.json()
        print(f"✓ Answer received:")
        print(f"  {data['answer'][:200]}...")
        print(f"\n  Sources used: {len(data['sources'])}")
        for source in data['sources']:
            print(f"    - {source['title']}")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Substack Search API Test")
    print("="*60)

    results = {
        "health": test_health(),
        "collections": test_collections(),
        "search": test_search(),
        "ask": test_ask()
    }

    print("\n" + "="*60)
    print("Test Results:")
    print("="*60)
    for test, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test:15s} {status}")

    all_passed = all(results.values())
    print("="*60)
    if all_passed:
        print("All tests passed! Your search API is working correctly.")
    else:
        print("Some tests failed. Check the errors above.")
        print("\nCommon issues:")
        print("- Docker services not running: docker-compose up -d")
        print("- No articles indexed: python indexer.py")
        print("- GLM API key missing: Check .env file")
    print("="*60)
