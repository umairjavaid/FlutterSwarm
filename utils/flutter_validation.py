"""
Flutter project validation utilities.
Provides comprehensive validation of Flutter project structure and files.
"""

import os
import yaml
from typing import Dict, Any, List
from pathlib import Path


async def validate_flutter_project(project_path: str) -> Dict[str, Any]:
    """
    Validate Flutter project structure and files.
    
    Args:
        project_path: Path to the Flutter project directory
        
    Returns:
        Dictionary with validation results including:
        - valid: Boolean indicating if project is valid
        - missing_files: List of missing required files
        - project_path: The validated project path
        - details: Detailed validation information
    """
    missing_files = []
    validation_details = {}
    
    # Ensure project path exists
    if not os.path.exists(project_path):
        return {
            'valid': False,
            'missing_files': ['project_directory'],
            'project_path': project_path,
            'details': {'error': f'Project directory does not exist: {project_path}'}
        }
    
    # Required files for a valid Flutter project
    required_files = [
        'pubspec.yaml',
        'lib/main.dart',
        'android/app/build.gradle',
        'ios/Runner/Info.plist'
    ]
    
    # Check each required file
    for file_path in required_files:
        full_path = os.path.join(project_path, file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
    
    # Validate pubspec.yaml structure if it exists
    pubspec_path = os.path.join(project_path, 'pubspec.yaml')
    pubspec_valid = False
    pubspec_errors = []
    
    if os.path.exists(pubspec_path):
        try:
            with open(pubspec_path, 'r', encoding='utf-8') as f:
                pubspec_content = yaml.safe_load(f)
            
            # Check required pubspec fields
            required_pubspec_fields = ['name', 'description', 'version', 'environment', 'dependencies']
            for field in required_pubspec_fields:
                if field not in pubspec_content:
                    pubspec_errors.append(f'Missing required field: {field}')
            
            # Check Flutter dependency
            dependencies = pubspec_content.get('dependencies', {})
            if 'flutter' not in dependencies:
                pubspec_errors.append('Missing flutter dependency')
            
            # Check Dart SDK constraint
            environment = pubspec_content.get('environment', {})
            if 'sdk' not in environment:
                pubspec_errors.append('Missing Dart SDK constraint in environment')
            
            pubspec_valid = len(pubspec_errors) == 0
            validation_details['pubspec'] = {
                'valid': pubspec_valid,
                'errors': pubspec_errors,
                'content': pubspec_content
            }
            
        except yaml.YAMLError as e:
            pubspec_errors.append(f'Invalid YAML syntax: {str(e)}')
            validation_details['pubspec'] = {
                'valid': False,
                'errors': pubspec_errors
            }
        except Exception as e:
            pubspec_errors.append(f'Error reading file: {str(e)}')
            validation_details['pubspec'] = {
                'valid': False,
                'errors': pubspec_errors
            }
    else:
        validation_details['pubspec'] = {
            'valid': False,
            'errors': ['File does not exist']
        }
    
    # Validate main.dart structure if it exists
    main_dart_path = os.path.join(project_path, 'lib/main.dart')
    main_dart_valid = False
    main_dart_errors = []
    
    if os.path.exists(main_dart_path):
        try:
            with open(main_dart_path, 'r', encoding='utf-8') as f:
                main_dart_content = f.read()
            
            # Check for essential Flutter app components
            required_patterns = [
                'void main()',
                'runApp(',
                'MaterialApp',
                'import \'package:flutter/material.dart\';'
            ]
            
            for pattern in required_patterns:
                if pattern not in main_dart_content:
                    main_dart_errors.append(f'Missing required pattern: {pattern}')
            
            main_dart_valid = len(main_dart_errors) == 0
            validation_details['main_dart'] = {
                'valid': main_dart_valid,
                'errors': main_dart_errors,
                'size_bytes': len(main_dart_content)
            }
            
        except Exception as e:
            main_dart_errors.append(f'Error reading file: {str(e)}')
            validation_details['main_dart'] = {
                'valid': False,
                'errors': main_dart_errors
            }
    else:
        validation_details['main_dart'] = {
            'valid': False,
            'errors': ['File does not exist']
        }
    
    # Check Android configuration
    android_gradle_path = os.path.join(project_path, 'android/app/build.gradle')
    android_valid = False
    
    if os.path.exists(android_gradle_path):
        try:
            with open(android_gradle_path, 'r', encoding='utf-8') as f:
                gradle_content = f.read()
            
            # Check for essential Android configuration
            android_patterns = [
                'android {',
                'compileSdkVersion',
                'applicationId',
                'targetSdkVersion'
            ]
            
            android_errors = []
            for pattern in android_patterns:
                if pattern not in gradle_content:
                    android_errors.append(f'Missing Android pattern: {pattern}')
            
            android_valid = len(android_errors) == 0
            validation_details['android'] = {
                'valid': android_valid,
                'errors': android_errors
            }
            
        except Exception as e:
            validation_details['android'] = {
                'valid': False,
                'errors': [f'Error reading build.gradle: {str(e)}']
            }
    else:
        validation_details['android'] = {
            'valid': False,
            'errors': ['build.gradle does not exist']
        }
    
    # Check iOS configuration
    ios_info_path = os.path.join(project_path, 'ios/Runner/Info.plist')
    ios_valid = False
    
    if os.path.exists(ios_info_path):
        try:
            with open(ios_info_path, 'r', encoding='utf-8') as f:
                info_content = f.read()
            
            # Check for essential iOS configuration
            ios_patterns = [
                'CFBundleName',
                'CFBundleIdentifier',
                'CFBundleVersion',
                'CFBundleShortVersionString'
            ]
            
            ios_errors = []
            for pattern in ios_patterns:
                if pattern not in info_content:
                    ios_errors.append(f'Missing iOS pattern: {pattern}')
            
            ios_valid = len(ios_errors) == 0
            validation_details['ios'] = {
                'valid': ios_valid,
                'errors': ios_errors
            }
            
        except Exception as e:
            validation_details['ios'] = {
                'valid': False,
                'errors': [f'Error reading Info.plist: {str(e)}']
            }
    else:
        validation_details['ios'] = {
            'valid': False,
            'errors': ['Info.plist does not exist']
        }
    
    # Check for additional recommended directories
    recommended_dirs = [
        'test',
        'lib/core',
        'lib/features',
        'lib/shared'
    ]
    
    missing_dirs = []
    for dir_path in recommended_dirs:
        full_dir_path = os.path.join(project_path, dir_path)
        if not os.path.exists(full_dir_path):
            missing_dirs.append(dir_path)
    
    validation_details['recommended_dirs'] = {
        'missing': missing_dirs,
        'checked': recommended_dirs
    }
    
    # Determine overall validity
    core_components_valid = (
        len(missing_files) == 0 and
        pubspec_valid and
        main_dart_valid and
        android_valid and
        ios_valid
    )
    
    return {
        'valid': core_components_valid,
        'missing_files': missing_files,
        'project_path': project_path,
        'details': validation_details,
        'summary': {
            'pubspec_valid': pubspec_valid,
            'main_dart_valid': main_dart_valid,
            'android_valid': android_valid,
            'ios_valid': ios_valid,
            'missing_required_files': len(missing_files),
            'missing_recommended_dirs': len(missing_dirs)
        }
    }


def validate_flutter_project_sync(project_path: str) -> Dict[str, Any]:
    """
    Synchronous version of validate_flutter_project for compatibility.
    
    Args:
        project_path: Path to the Flutter project directory
        
    Returns:
        Dictionary with validation results
    """
    import asyncio
    
    # Try to get the current event loop, create one if none exists
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If we're in an async context, we can't use loop.run_until_complete
            # In this case, the caller should use the async version
            raise RuntimeError("Cannot run sync validation in async context. Use validate_flutter_project() instead.")
        return loop.run_until_complete(validate_flutter_project(project_path))
    except RuntimeError:
        # No event loop exists, create a new one
        return asyncio.run(validate_flutter_project(project_path))


def get_flutter_project_health_score(validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate a health score for a Flutter project based on validation results.
    
    Args:
        validation_result: Result from validate_flutter_project
        
    Returns:
        Dictionary with health score and breakdown
    """
    if not validation_result.get('valid'):
        return {
            'score': 0,
            'grade': 'F',
            'issues': validation_result.get('missing_files', []),
            'recommendations': ['Fix missing required files before proceeding']
        }
    
    details = validation_result.get('details', {})
    summary = validation_result.get('summary', {})
    
    # Calculate score based on different factors
    score = 100
    issues = []
    recommendations = []
    
    # Core structure (40 points)
    if not summary.get('pubspec_valid', False):
        score -= 15
        issues.append('Invalid pubspec.yaml')
        recommendations.append('Fix pubspec.yaml structure and dependencies')
    
    if not summary.get('main_dart_valid', False):
        score -= 15
        issues.append('Invalid main.dart')
        recommendations.append('Ensure main.dart has proper Flutter app structure')
    
    if not summary.get('android_valid', False):
        score -= 5
        issues.append('Android configuration issues')
        recommendations.append('Check android/app/build.gradle configuration')
    
    if not summary.get('ios_valid', False):
        score -= 5
        issues.append('iOS configuration issues')
        recommendations.append('Check ios/Runner/Info.plist configuration')
    
    # Project structure (30 points)
    missing_dirs = summary.get('missing_recommended_dirs', 0)
    if isinstance(missing_dirs, list):
        missing_dirs = len(missing_dirs)
    
    if missing_dirs > 0:
        dir_penalty = min(missing_dirs * 7, 30)
        score -= dir_penalty
        issues.append(f'{missing_dirs} missing recommended directories')
        recommendations.append('Add recommended directories like lib/core, lib/features, test/')
    
    # File quality (30 points)
    pubspec_details = details.get('pubspec', {})
    if pubspec_details.get('errors'):
        error_count = len(pubspec_details['errors'])
        error_penalty = min(error_count * 5, 15)
        score -= error_penalty
        issues.extend(pubspec_details['errors'])
    
    main_dart_details = details.get('main_dart', {})
    if main_dart_details.get('errors'):
        error_count = len(main_dart_details['errors'])
        error_penalty = min(error_count * 3, 15)
        score -= error_penalty
        issues.extend(main_dart_details['errors'])
    
    # Ensure score doesn't go below 0
    score = max(0, score)
    
    # Determine grade
    if score >= 90:
        grade = 'A'
    elif score >= 80:
        grade = 'B'
    elif score >= 70:
        grade = 'C'
    elif score >= 60:
        grade = 'D'
    else:
        grade = 'F'
    
    return {
        'score': score,
        'grade': grade,
        'issues': issues,
        'recommendations': recommendations,
        'breakdown': {
            'pubspec_valid': summary.get('pubspec_valid', False),
            'main_dart_valid': summary.get('main_dart_valid', False),
            'android_valid': summary.get('android_valid', False),
            'ios_valid': summary.get('ios_valid', False),
            'missing_dirs': missing_dirs
        }
    }
