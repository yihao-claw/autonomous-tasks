#!/usr/bin/env python3
"""
DuckDuckGo Search Skill for OpenClaw
Search the web without needing an API key
"""

import sys
import json
import argparse
from ddgs import DDGS

def search(query, num_results=10):
    """
    Search using DuckDuckGo
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 10)
    
    Returns:
        List of search results with title, URL, and description
    """
    try:
        with DDGS() as ddgs:
            results = []
            for result in ddgs.text(query, max_results=num_results):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'description': result.get('body', ''),
                    'source': 'ddg'
                })
            return results
    except Exception as e:
        return {
            'error': str(e),
            'query': query
        }

def main():
    parser = argparse.ArgumentParser(
        description='Search the web using DuckDuckGo',
        prog='ddg-search'
    )
    parser.add_argument('query', help='Search query')
    parser.add_argument('-n', '--num-results', type=int, default=10,
                       help='Number of results (default: 10)')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    
    args = parser.parse_args()
    
    # Perform search
    results = search(args.query, args.num_results)
    
    # Output
    if args.json or True:  # Always output JSON for tool integration
        print(json.dumps({
            'query': args.query,
            'results': results
        }, indent=2))
    else:
        print(f"Search: {args.query}")
        print(f"Results ({len(results)} found):")
        print("-" * 80)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   {result['description'][:100]}...")
            print()

if __name__ == '__main__':
    main()
