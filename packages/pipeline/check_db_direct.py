#!/usr/bin/env python3
"""Direct MongoDB check."""

import sys
from pathlib import Path

# Add package to path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

from src.storage.mongodb import MongoDBClient

mongo = MongoDBClient()
mongo.connect()

db = mongo._db

print('Collections in knowledge_db:')
print(db.list_collection_names())

print('\n' + '='*60)
print('Checking knowledge_pipeline-extractions')
print('='*60)

collection = db['knowledge_pipeline-extractions']
count = collection.count_documents({})
print(f'Total documents: {count}')

if count > 0:
    # Get counts by type
    pipeline = [
        {'$group': {'_id': '$type', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    results = list(collection.aggregate(pipeline))
    print('\nCounts by extraction type:')
    for result in results:
        print(f"  {result['_id']:15}: {result['count']:6,}")

    # Show sample
    sample = collection.find_one()
    print('\nSample extraction:')
    import json
    print(json.dumps(sample, indent=2, default=str)[:500])

mongo.close()
