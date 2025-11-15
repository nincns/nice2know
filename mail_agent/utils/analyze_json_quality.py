#!/usr/bin/env python3
"""
Nice2Know - JSON Quality Analyzer
Analyzes extracted JSON data and marks fields as complete/missing/unclear
For visual display in confirmation mail (not interactive)
"""
import json
from pathlib import Path
from typing import Dict, List

def analyze_quality(problem: Dict, solution: Dict, asset: Dict) -> Dict:
    """
    Analyze JSON quality and return status for each field
    Returns: dict with 'complete', 'missing', 'unclear' lists
    """
    results = {
        'complete': [],   # ✓ Green - good
        'missing': [],    # ⚠ Yellow - empty/null
        'unclear': []     # ❓ Blue - generic/placeholder
    }
    
    # === PROBLEM ANALYSIS ===
    prob = problem.get('problem', {})
    reporter = problem.get('reporter', {})
    classification = problem.get('classification', {})
    
    # Title
    if prob.get('title'):
        results['complete'].append('problem_title')
    else:
        results['missing'].append('problem_title')
    
    # Description
    desc = prob.get('description', '')
    if desc and len(desc) > 20:
        results['complete'].append('problem_description')
    elif desc:
        results['unclear'].append('problem_description')
    else:
        results['missing'].append('problem_description')
    
    # Symptoms
    symptoms = prob.get('symptoms', [])
    if symptoms and len(symptoms) > 0:
        results['complete'].append('problem_symptoms')
    else:
        results['missing'].append('problem_symptoms')
    
    # Reporter Department
    if reporter.get('department'):
        results['complete'].append('reporter_department')
    else:
        results['missing'].append('reporter_department')
    
    # Severity
    if classification.get('severity'):
        results['complete'].append('classification_severity')
    
    # Affected Users
    affected = classification.get('affected_users', '')
    if affected and affected != 'single user':
        results['complete'].append('affected_users')
    elif affected == 'single user':
        results['unclear'].append('affected_users')
    else:
        results['missing'].append('affected_users')
    
    # === SOLUTION ANALYSIS ===
    sol = solution.get('solution', {})
    metadata = solution.get('metadata', {})
    
    # Title
    if sol.get('title'):
        results['complete'].append('solution_title')
    else:
        results['missing'].append('solution_title')
    
    # Steps
    steps = sol.get('steps', [])
    if steps and len(steps) > 0:
        results['complete'].append('solution_steps')
    else:
        results['missing'].append('solution_steps')
    
    # Approach
    if sol.get('approach'):
        results['complete'].append('solution_approach')
    else:
        results['missing'].append('solution_approach')
    
    # Complexity
    complexity = metadata.get('complexity')
    if complexity and len(steps) > 0:
        # Check if complexity matches step count
        if (complexity == 'low' and len(steps) <= 3) or \
           (complexity == 'medium' and 3 < len(steps) <= 5) or \
           (complexity == 'high' and len(steps) > 5):
            results['complete'].append('solution_complexity')
        else:
            results['unclear'].append('solution_complexity')
    else:
        results['missing'].append('solution_complexity')
    
    # === ASSET ANALYSIS ===
    ast = asset.get('asset', {})
    technical = asset.get('technical', {})
    
    # Name
    if ast.get('name'):
        results['complete'].append('asset_name')
    
    # Version
    if technical.get('version'):
        results['complete'].append('asset_version')
    else:
        results['missing'].append('asset_version')
    
    # Platform
    if technical.get('platform'):
        results['complete'].append('asset_platform')
    else:
        results['missing'].append('asset_platform')
    
    # Deployment
    deployment = technical.get('deployment')
    if deployment and deployment != 'cloud-based':
        results['complete'].append('asset_deployment')
    elif deployment == 'cloud-based':
        results['unclear'].append('asset_deployment')
    else:
        results['missing'].append('asset_deployment')
    
    # Calculate scores
    total = len(results['complete']) + len(results['missing']) + len(results['unclear'])
    completeness = (len(results['complete']) / total * 100) if total > 0 else 0
    
    results['summary'] = {
        'completeness_percent': round(completeness, 1),
        'complete_count': len(results['complete']),
        'missing_count': len(results['missing']),
        'unclear_count': len(results['unclear']),
        'total_fields': total,
        'quality': 'good' if completeness >= 75 else 'medium' if completeness >= 50 else 'needs_work'
    }
    
    return results

# Helper function to check field status
def get_field_status(field_name: str, analysis: Dict) -> str:
    """Returns: 'complete', 'missing', 'unclear', or 'unknown'"""
    if field_name in analysis['complete']:
        return 'complete'
    elif field_name in analysis['missing']:
        return 'missing'
    elif field_name in analysis['unclear']:
        return 'unclear'
    return 'unknown'

if __name__ == "__main__":
    # Test
    print("JSON Quality Analyzer ready")
