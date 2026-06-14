#!/usr/bin/env python3
"""Add {% translate '...' %} tags to Russian and English text in Django templates."""

import re
import os
from pathlib import Path

# Russian and English text patterns
RUSSIAN_PATTERN = re.compile(r'[А-Яа-яЁё]')
ENGLISH_PATTERN = re.compile(r'^[A-Za-z0-9\s\.,!?;:\-\'"\(\)\[\]{}@#$%^&*+=|\\/<>~`]+$')

# Patterns to NOT translate
DO_NOT_TRANSLATE = [
    r'&[a-z]+;',  # HTML entities like &larr;, &rarr;, &middot;, &copy;
    r'[^@\s]+@[^\s]+\.[^\s]+',  # email addresses
    r'\d+\s*[А-Яа-яA-Za-z\.\s,]+',  # addresses with numbers
]

def should_translate(text):
    """Check if text should be translated."""
    text = text.strip()
    
    # Skip empty text
    if not text:
        return False
    
    # Skip if contains HTML entities
    if '&' in text and ';' in text:
        return False
    
    # Skip if it's primarily numbers/symbols
    if re.match(r'^[\d\s\.\-]+$', text):
        return False
    
    # Check if entirely Russian or entirely English
    has_russian = bool(RUSSIAN_PATTERN.search(text))
    has_english = bool(re.search(r'[A-Za-z]', text))
    
    # Only translate if entirely one language (not mixed)
    if has_russian and not has_english:
        return True
    if has_english and not has_russian:
        return True
    
    return False

def add_translate_tags_to_file(filepath):
    """Add translate tags to a template file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Add {% load i18n %} if not present
    if '{% load i18n %}' not in content and '{% translate' in content:
        # Add after first line if it's a comment/extends/load tag
        lines = content.split('\n')
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('{%') or line.strip().startswith('{#'):
                insert_idx = i + 1
            else:
                break
        lines.insert(insert_idx, '{% load i18n %}')
        content = '\n'.join(lines)
    
    # Pattern to match text content between HTML tags (not in code/attributes)
    # This is a simplified approach - won't catch all cases
    text_pattern = re.compile(r'(>[^<]*<)')
    
    def replace_text(match):
        text = match.group(1)
        # Extract text between > and <
        inner = text[1:-1]
        
        # Skip if already has translate tag
        if '{% translate' in inner or '{% blocktranslate' in inner:
            return text
        
        # Skip template tags
        if '{%' in inner or '{{' in inner:
            return text
        
        # Check if should be translated
        if should_translate(inner):
            return f'>{{% translate \'{inner.strip()}\' %}}<'
        
        return text
    
    # Apply translation tags
    content = text_pattern.sub(replace_text, content)
    
    # Write back if changed
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    templates_dir = Path('templates')
    
    count = 0
    for html_file in templates_dir.rglob('*.html'):
        if add_translate_tags_to_file(html_file):
            count += 1
            print(f'Updated: {html_file}')
    
    print(f'\nTotal files updated: {count}')

if __name__ == '__main__':
    main()
