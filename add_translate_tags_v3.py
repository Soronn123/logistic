#!/usr/bin/env python3
"""Carefully add {% translate '...' %} tags to Django templates."""

import re
import os
from pathlib import Path

def add_translate_tags(filepath):
    """Add translate tags to text content in template."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified = False
    result_lines = []
    
    # Check if {% load i18n %} is needed
    needs_i18n = False
    has_load_i18n = False
    
    for line in lines:
        if '{% load i18n %}' in line or '{% load static i18n %}' in line:
            has_load_i18n = True
        if '{% translate' in line and not has_load_i18n:
            needs_i18n = True
    
    # Add {% load i18n %} after first line if needed
    if needs_i18n and not has_load_i18n:
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('{%') or line.strip().startswith('{#'):
                insert_idx = i + 1
            else:
                break
        lines.insert(insert_idx, '{% load i18n %}\n')
    
    # Process lines
    for line in lines:
        # Skip lines with blocktranslate (don't modify)
        if '{% blocktranslate' in line:
            result_lines.append(line)
            continue
        
        # Skip script and style content
        if '<script' in line or '<style' in line or '</script>' in line or '</style>' in line:
            result_lines.append(line)
            continue
        
        # Process the line
        new_line = process_line(line)
        if new_line != line:
            modified = True
        result_lines.append(new_line)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(result_lines)
        return True
    return False

def process_line(line):
    """Process a single line to add translate tags."""
    # Don't modify lines with template tags already
    if '{% translate' in line or '{% blocktranslate' in line:
        return line
    
    # Pattern to match text content between HTML tags
    # Avoid script/style tags and HTML entities
    patterns = [
        # Match >Text< (text between tags)
        (r'>([^<]+)<', process_text_match),
    ]
    
    for pattern, handler in patterns:
        line = re.sub(pattern, handler, line)
    
    return line

def process_text_match(match):
    """Process matched text."""
    text = match.group(1)
    
    # Skip empty text
    if not text.strip():
        return match.group(0)
    
    # Skip HTML entities
    if '&' in text and ';' in text:
        return match.group(0)
    
    # Skip if contains template tags
    if '{%' in text or '{{' in text:
        return match.group(0)
    
    # Skip emails
    if '@' in text:
        return match.group(0)
    
    # Check if should translate
    if should_translate(text):
        return f'>{{% translate \'{text.strip()}\' %}}<'
    
    return match.group(0)

def should_translate(text):
    """Check if text should be translated."""
    text = text.strip()
    
    if not text:
        return False
    
    # Check if entirely Russian or entirely English
    has_cyrillic = bool(re.search(r'[А-Яа-яЁё]', text))
    has_latin = bool(re.search(r'[A-Za-z]', text))
    
    # Only translate if entirely one script (not mixed)
    if has_cyrillic and not has_latin:
        return True
    if has_latin and not has_cyrillic:
        return True
    
    return False

def main():
    templates_dir = Path('templates')
    
    count = 0
    for html_file in templates_dir.rglob('*.html'):
        if add_translate_tags(html_file):
            count += 1
            print(f'Updated: {html_file}')
    
    print(f'\nTotal files updated: {count}')

if __name__ == '__main__':
    main()
