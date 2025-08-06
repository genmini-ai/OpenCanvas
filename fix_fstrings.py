#!/usr/bin/env python3
"""
Script to find and report all f-string issues in evolution folder
"""
import os
import re
from pathlib import Path

def find_fstring_issues(file_path):
    """Find f-strings that might have nested brace issues"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if 'f"""' in line:
                # Found start of f-string, collect until end
                fstring_start = i
                fstring_lines = [line]
                i += 1
                
                # Collect all lines until closing """
                while i < len(lines):
                    fstring_lines.append(lines[i])
                    if '"""' in lines[i] and not lines[i].strip().startswith('f"""'):
                        break
                    i += 1
                
                fstring_content = '\n'.join(fstring_lines)
                
                # Check for problematic patterns
                has_json_template = '```json' in fstring_content.lower()
                has_nested_braces = '{' in fstring_content and '}' in fstring_content
                has_json_dumps = 'json.dumps(' in fstring_content
                
                if has_json_template or (has_nested_braces and has_json_dumps):
                    issues.append({
                        'start_line': fstring_start + 1,
                        'end_line': i + 1,
                        'has_json_template': has_json_template,
                        'has_nested_braces': has_nested_braces,
                        'has_json_dumps': has_json_dumps,
                        'content_preview': fstring_lines[0][:100] + '...' if len(fstring_lines[0]) > 100 else fstring_lines[0]
                    })
            else:
                i += 1
        
        return issues
        
    except Exception as e:
        return [{'error': str(e)}]

def main():
    evolution_dir = Path('/Users/christineh./Downloads/slidebee/OpenCanvas/src/opencanvas/evolution')
    
    print("🔍 Scanning for f-string issues in evolution folder...")
    print("=" * 80)
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk(evolution_dir):
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    total_issues = 0
    files_with_issues = []
    
    for file_path in sorted(python_files):
        rel_path = file_path.relative_to(evolution_dir)
        issues = find_fstring_issues(file_path)
        
        if issues and not (len(issues) == 1 and 'error' in issues[0]):
            print(f"\n❌ {rel_path}")
            print(f"   Found {len(issues)} problematic f-string(s)")
            
            for issue in issues:
                if 'error' in issue:
                    print(f"   Error: {issue['error']}")
                else:
                    print(f"   Lines {issue['start_line']}-{issue['end_line']}:")
                    print(f"     Preview: {issue['content_preview']}")
                    if issue['has_json_template']:
                        print(f"     ⚠️  Contains JSON template (```json)")
                    if issue['has_json_dumps']:
                        print(f"     ⚠️  Contains json.dumps() call")
                    if issue['has_nested_braces']:
                        print(f"     ⚠️  Has nested braces")
            
            files_with_issues.append(str(rel_path))
            total_issues += len(issues)
        elif issues and 'error' in issues[0]:
            print(f"\n⚠️  {rel_path}: Error reading file - {issues[0]['error']}")
        else:
            print(f"✅ {rel_path}: No f-string issues")
    
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"Total Python files scanned: {len(python_files)}")
    print(f"Files with f-string issues: {len(files_with_issues)}")
    print(f"Total f-string issues found: {total_issues}")
    
    if files_with_issues:
        print(f"\n🔧 FILES NEEDING FIXES:")
        for file_path in files_with_issues:
            print(f"   - {file_path}")
        
        print(f"\n💡 COMMON FIXES NEEDED:")
        print("1. Extract json.dumps() calls to variables before f-string")
        print("2. Replace JSON templates with text descriptions")
        print("3. Use double braces {{}} to escape braces in templates")
        print("4. Move complex expressions outside f-string")
    else:
        print("\n✅ No f-string issues found!")

if __name__ == "__main__":
    main()