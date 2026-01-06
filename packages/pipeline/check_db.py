#!/usr/bin/env python3
"""Check MongoDB extraction counts."""

import sys
from pathlib import Path

# Add package to path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))

from src.storage.mongodb import MongoDBClient

mongo = MongoDBClient()
mongo.connect()

# Count extractions by type
extraction_types = ['decision', 'pattern', 'warning', 'methodology', 'checklist', 'workflow', 'persona']

print('='*60)
print('EXTRACTION COUNTS BY TYPE')
print('='*60)

for ext_type in extraction_types:
    count = mongo._db['knowledge_pipeline-extractions'].count_documents({'type': ext_type})
    print(f'{ext_type:15} : {count:6,} extractions')

print('\n' + '='*60)
print('EXTRACTIONS BY SOURCE')
print('='*60)

sources = mongo._db['knowledge_pipeline-extractions'].aggregate([
    {'$group': {'_id': '$source_id', 'count': {'$sum': 1}, 'types': {'$addToSet': '$type'}}}
])

for source in sources:
    source_doc = mongo._db['sources'].find_one({'_id': source['_id']})
    name = source_doc['name'] if source_doc else 'Unknown'
    print(f'{name:40} : {source["count"]:6,} extractions')
    print(f'  Types: {sorted(source["types"])}')

mongo.close()
