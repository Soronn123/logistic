#!/usr/bin/env python3
"""
Add {% translate %} tags to Django HTML templates.
Run from the project root directory.
"""

import re
import sys
from pathlib import Path

def is_translatable(text):
    """Check if text is entirely Russian or English and should be translated."""
    text = text.strip()
    if not text:
        return False
    # Check for Cyrillic (Russian)
    has_cyrillic = bool(re.search(r'[А-Яа-яЁё]', text))
    has_latin = bool(re.search(r'[A-Za-z]', text))
    
    # Entirely Russian
    if has_cyrillic and not has_latin:
        return True
    # Entirely English  
    if has_latin and not has_cyrillic:
        return True
    return False

def wrap_text(text):
    """Wrap text in {% translate '...' %} tag."""
    # Preserve leading/trailing whitespace
    leading = ''
    trailing = ''
    for c in text:
        if c in ' \t':
            leading += c
        else:
            break
    for c in reversed(text):
        if c in ' \t\n\r':
            trailing = c + trailing
        else:
            break
    
    stripped = text.strip()
    if not stripped:
        return text
    
    # Escape single quotes
    escaped = stripped.replace("'", "\\'")
    return f"{leading}{{% translate '{escaped}' %}}{trailing}"

def find_tag_end(s, start):
    """Find matching > for HTML tag, respecting quotes."""
    i = start
    single = False
    double = False
    while i < len(s):
        c = s[i]
        if c == "'" and not double:
            single = not single
        elif c == '"' and not single:
            double = not double
        elif c == '>' and not single and not double:
            return i
        i += 1
    return -1

def process_template(content):
    """Process template content and add translate tags."""
    result = []
    i = 0
    n = len(content)
    changed = False
    in_script = False
    in_style = False
    
    while i < n:
        # Check for script/style tags
        if not in_script and content[i:i+7].lower() == '<script':
            end = find_tag_end(content, i)
            if end == -1:
                result.append(content[i:])
                break
            result.append(content[i:end+1])
            i = end + 1
            in_script = True
            continue
            
        if in_script and content[i:i+9].lower() == '</script>':
            result.append(content[i:i+9])
            i += 9
            in_script = False
            continue
            
        if not in_style and content[i:i+6].lower() == '<style':
            end = find_tag_end(content, i)
            if end == -1:
                result.append(content[i:])
                break
            result.append(content[i:end+1])
            i = end + 1
            in_style = True
            continue
            
        if in_style and content[i:i+8].lower() == '</style>':
            result.append(content[i:i+8])
            i += 8
            in_style = False
            continue
            
        # Skip script/style content
        if in_script or in_style:
            result.append(content[i])
            i += 1
            continue
            
        # Skip HTML tags
        if content[i] == '<':
            end = find_tag_end(content, i)
            if end == -1:
                result.append(content[i:])
                break
            result.append(content[i:end+1])
            i = end + 1
            continue
            
        # Skip Django template tags
        if content[i:i+2] in ('{%', '{{', '{#'):
            if content[i:i+2] == '{#':
                end = content.find('#}', i)
            elif content[i:i+2] == '{{':
                end = content.find('}}', i)
            else:
                end = content.find('%}', i)
            if end == -1:
                result.append(content[i:])
                break
            result.append(content[i:end+2])
            i = end + 2
            continue
            
        # Collect text content
        start = i
        while i < n and content[i] != '<' and content[i:i+2] not in ('{%', '{{', '{#'):
            i += 1
            
        text = content[start:i]
        if text.strip() and is_translatable(text):
            result.append(wrap_text(text))
            changed = True
        else:
            result.append(text)
    
    return ''.join(result), changed

def has_i18n(content):
    """Check if template already loads i18n."""
    for line in content.split('\n'):
        if '{%' in line and 'load' in line and 'i18n' in line and '%}' in line:
            return True
    return False

def main():
    templates_dir = Path('templates')
    if not templates_dir.exists():
        print("Error: templates/ directory not found", file=sys.stderr)
        sys.exit(1)
        
    html_files = list(templates_dir.rglob('*.html'))
    print(f"Found {len(html_files)} HTML files", file=sys.stderr)
    
    updated = 0
    for fpath in html_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            new_content, changed = process_template(content)
            
            if changed:
                if not has_i18n(content):
                    new_content = '{% load i18n %}\n' + new_content
                    
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
                print(f"Updated: {fpath}", file=sys.stderr)
                updated += 1
            else:
                print(f"No changes: {fpath}", file=sys.stderr)
                
        except Exception as e:
            print(f"Error processing {fpath}: {e}", file=sys.stderr)
    
    print(f"\nDone! Updated {updated} files.", file=sys.stderr)

if __name__ == '__main__':
    main()
