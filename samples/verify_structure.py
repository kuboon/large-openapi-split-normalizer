#!/usr/bin/env python3
"""
Verification script to compare the structure of single-file and multi-file schemas.
This script checks that both versions represent the same API structure.
"""

import yaml
import json
from pathlib import Path

def load_yaml(file_path):
    """Load and parse a YAML file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

def get_single_file_info():
    """Extract key information from the single-file schema."""
    schema = load_yaml('single-file/openapi.yaml')
    
    info = {
        'version': schema.get('openapi'),
        'title': schema.get('info', {}).get('title'),
        'paths': list(schema.get('paths', {}).keys()),
        'schemas': list(schema.get('components', {}).get('schemas', {}).keys()),
    }
    
    # Extract circular references
    user = schema['components']['schemas']['User']
    org = schema['components']['schemas']['Organization']
    
    info['user_refs_org'] = 'organization' in user.get('properties', {})
    info['org_refs_user'] = 'owner' in org.get('properties', {})
    
    return info

def get_multi_file_info():
    """Extract key information from the multi-file schema."""
    schema = load_yaml('multi-file/openapi.yaml')
    
    info = {
        'version': schema.get('openapi'),
        'title': schema.get('info', {}).get('title'),
        'paths': list(schema.get('paths', {}).keys()),
        'schemas': list(schema.get('components', {}).get('schemas', {}).keys()),
    }
    
    # Check for circular references in the split files
    user = load_yaml('multi-file/components/schemas/User.yaml')
    org = load_yaml('multi-file/components/schemas/Organization.yaml')
    
    info['user_refs_org'] = 'organization' in user.get('properties', {})
    info['org_refs_user'] = 'owner' in org.get('properties', {})
    
    return info

def main():
    print("=" * 70)
    print("OpenAPI Schema Structure Verification")
    print("=" * 70)
    print()
    
    single = get_single_file_info()
    multi = get_multi_file_info()
    
    print("Single-File Schema:")
    print(f"  Version: {single['version']}")
    print(f"  Title: {single['title']}")
    print(f"  Paths: {len(single['paths'])} endpoints")
    print(f"  Schemas: {len(single['schemas'])} components")
    print(f"  Circular refs: User→Org={single['user_refs_org']}, Org→User={single['org_refs_user']}")
    print()
    
    print("Multi-File Schema:")
    print(f"  Version: {multi['version']}")
    print(f"  Title: {multi['title']}")
    print(f"  Paths: {len(multi['paths'])} endpoints")
    print(f"  Schemas: {len(multi['schemas'])} components")
    print(f"  Circular refs: User→Org={multi['user_refs_org']}, Org→User={multi['org_refs_user']}")
    print()
    
    print("=" * 70)
    print("Comparison Results:")
    print("=" * 70)
    
    checks = [
        ("OpenAPI version matches", single['version'] == multi['version']),
        ("API title matches", single['title'] == multi['title']),
        ("Same number of paths", len(single['paths']) == len(multi['paths'])),
        ("Same paths defined", set(single['paths']) == set(multi['paths'])),
        ("Same number of schemas", len(single['schemas']) == len(multi['schemas'])),
        ("Same schemas defined", set(single['schemas']) == set(multi['schemas'])),
        ("Both have User→Organization ref", single['user_refs_org'] and multi['user_refs_org']),
        ("Both have Organization→User ref", single['org_refs_user'] and multi['org_refs_user']),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {check_name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 SUCCESS: Both schemas represent the same API structure!")
        print("    Including circular references: User ↔ Organization")
    else:
        print("⚠ WARNING: Schemas have differences!")
        return 1
    
    print()
    print("Paths defined:")
    for path in sorted(single['paths']):
        print(f"  - {path}")
    
    print()
    print("Schemas defined:")
    for schema in sorted(single['schemas']):
        print(f"  - {schema}")
    
    return 0

if __name__ == '__main__':
    exit(main())
