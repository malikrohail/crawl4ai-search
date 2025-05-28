#!/usr/bin/env python3

from search_engine import perform_web_search
import asyncio
import yaml

async def test_search():
    # Load config
    with open('config.yml', 'r') as f:
        config = yaml.safe_load(f)
    
    try:
        print("Testing search with new search engine...")
        results = await perform_web_search(
            query='python tutorial',
            limit=2,
            lang='en',
            country='us',
            config=config.get('search', {})
        )
        print(f'Found {len(results)} results')
        
        for i, result in enumerate(results):
            print(f'{i+1}. {result.title}')
            print(f'   URL: {result.url}')
            print(f'   Description: {result.description[:100]}...')
            print()
            
    except Exception as e:
        print(f'Search failed: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_search()) 