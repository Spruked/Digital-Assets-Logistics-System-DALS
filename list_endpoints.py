"""List all DALS API endpoints"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"t:\Digital Assets Logistics Systems")

from iss_module.api.api import app

print("\n" + "="*80)
print("DALS API ENDPOINT REVIEW")
print("="*80 + "\n")

routes_by_tag = {}

for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
        if methods:
            tags = getattr(route, 'tags', ['Untagged'])
            tag = tags[0] if tags else 'Untagged'
            
            if tag not in routes_by_tag:
                routes_by_tag[tag] = []
            
            routes_by_tag[tag].append({
                'path': route.path,
                'methods': methods,
                'name': route.name
            })

# Print organized by tag
for tag in sorted(routes_by_tag.keys()):
    print(f"\n{'-'*80}")
    print(f"MODULE: {tag}")
    print(f"{'-'*80}")
    
    for route in sorted(routes_by_tag[tag], key=lambda x: x['path']):
        print(f"  {route['methods']:12} {route['path']}")

print(f"\n{'='*80}")
print(f"Total Endpoints: {sum(len(routes) for routes in routes_by_tag.values())}")
print(f"Total Tags: {len(routes_by_tag)}")
print("="*80 + "\n")
