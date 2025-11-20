#!/usr/bin/env python3
"""
Fix duplicate <main> and <script> tags in HTML files
"""
import re
from pathlib import Path

# Files that need fixing based on audit
files_to_fix = [
    "src/frontend/planificador.html",
    "src/frontend/uploads.html",
    "src/frontend/solicitudes.html",
    "src/frontend/presupuesto.html",
    "src/frontend/home.html",
    "src/frontend/nueva-solicitud.html",
    "src/frontend/centros.html",
    "src/frontend/mi-cuenta.html",
    "src/frontend/opciones-diseño.html",
]

def fix_html_file(filepath):
    """Remove duplicate <main> and <script> tags from HTML file"""
    path = Path(filepath)
    if not path.exists():
        print(f"⚠️  {filepath} not found, skipping")
        return False

    content = path.read_text(encoding='utf-8')
    original_content = content
    changes = []

    # Track all <main> and </main> positions
    lines = content.split('\n')
    main_opens = []
    main_closes = []
    script_app_js = []

    for i, line in enumerate(lines):
        # Find <main> tags
        if re.search(r'<main[^>]*>', line):
            main_opens.append(i)
        # Find </main> tags
        if '</main>' in line:
            main_closes.append(i)
        # Find <script src="/app.js">
        if re.search(r'<script\s+src=["\']\/app\.js["\']', line):
            script_app_js.append(i)

    # Remove duplicate <main> tags (keep first)
    if len(main_opens) > 1:
        for line_num in main_opens[1:]:
            lines[line_num] = ''  # Remove duplicate
            changes.append(f"Removed duplicate <main> at line {line_num + 1}")

    # Remove duplicate </main> tags (keep last)
    if len(main_closes) > 1:
        for line_num in main_closes[:-1]:
            lines[line_num] = ''  # Remove duplicate
            changes.append(f"Removed duplicate </main> at line {line_num + 1}")

    # Remove duplicate <script src="/app.js"> tags (keep first)
    if len(script_app_js) > 1:
        for line_num in script_app_js[1:]:
            lines[line_num] = ''  # Remove duplicate
            changes.append(f"Removed duplicate <script src='/app.js'> at line {line_num + 1}")

    # Reconstruct content
    new_content = '\n'.join(lines)

    # Remove consecutive empty lines (cleanup)
    new_content = re.sub(r'\n\n\n+', '\n\n', new_content)

    if new_content != original_content:
        path.write_text(new_content, encoding='utf-8')
        print(f"✅ {filepath}")
        for change in changes:
            print(f"   - {change}")
        return True
    else:
        print(f"ℹ️  {filepath} - No changes needed")
        return False

def main():
    print("🔧 Fixing duplicate HTML tags...\n")
    fixed_count = 0

    for filepath in files_to_fix:
        if fix_html_file(filepath):
            fixed_count += 1
        print()

    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
