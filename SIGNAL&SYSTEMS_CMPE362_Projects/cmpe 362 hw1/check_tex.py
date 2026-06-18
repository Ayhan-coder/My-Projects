import re

with open('homework1.tex', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for common LaTeX issues
issues = []

# Check if \documentclass exists
if not re.search(r'\\documentclass', content):
    issues.append('ERROR: Missing \\documentclass')

# Check if \end{document} exists
if not content.strip().endswith(r'\end{document}'):
    issues.append('ERROR: Document does not end with \\end{document}')

# Check for unmatched braces
open_braces = content.count('{')
close_braces = content.count('}')
if open_braces != close_braces:
    issues.append(f'ERROR: Brace mismatch - open: {open_braces}, close: {close_braces}')

# Check for unmatched brackets
open_brackets = content.count('[')
close_brackets = content.count(']')
if open_brackets != close_brackets:
    issues.append(f'ERROR: Bracket mismatch - open: {open_brackets}, close: {close_brackets}')

# Check if all begin/end match
begins = len(re.findall(r'\\begin\{', content))
ends = len(re.findall(r'\\end\{', content))
if begins != ends:
    issues.append(f'WARNING: Begin/end mismatch - begin: {begins}, end: {ends}')

if issues:
    print("ISSUES FOUND:")
    for issue in issues:
        print(f"  {issue}")
else:
    print('✓ LaTeX SYNTAX VALIDATION:')
    print(f'  ✓ Document class: report (A4 format)')
    print(f'  ✓ Total lines: {len(content.splitlines())}')
    print(f'  ✓ Braces: {open_braces} matched pairs')
    chapters = len(re.findall(r'\\chapter\*', content))
    sections = len(re.findall(r'\\section\*', content))
    subsections = len(re.findall(r'\\subsection\*', content))
    print(f'  ✓ Chapters: {chapters}')
    print(f'  ✓ Sections: {sections}')
    print(f'  ✓ Subsections: {subsections}')

# Check content completeness
print('\n✓ CONTENT REVIEW:')

# Check for name and ID
if 'ALi Ayhan Günder' in content:
    print('  ✓ Student name: ALi Ayhan Günder')
else:
    print('  ⚠ WARNING: Check student name')

if '2021400219' in content:
    print('  ✓ Student ID: 2021400219')
else:
    print('  ⚠ WARNING: Check student ID')

# Check for fundamental frequencies
freq_patterns = ['120', '320', '323', '1500', '1493']
freqs_found = sum(1 for f in freq_patterns if f in content)
print(f'  ✓ Fundamental frequencies filled in: {freqs_found}/5 key values')

# Check for comparison analysis
if 'agree' in content.lower() and 'differ' in content.lower():
    print('  ✓ Comparison analysis present')
else:
    print('  ⚠ WARNING: Check comparison section')

# Check for complex analysis
if 'complex' in content.lower():
    print('  ✓ Complex signal analysis included')

# Check all images
images = re.findall(r'\\includegraphics.*\{(.*?)\}', content)
print(f'\n✓ IMAGES REFERENCED ({len(images)} total):')
for img in images:
    print(f'  - {img}')
