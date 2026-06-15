#!/usr/bin/env python3
"""Fix formula rendering in 论文正文.md: \[ -> $$, \] -> $$, add formula numbers"""
import re

with open('论文正文.md', 'r') as f:
    content = f.read()

# Count before
display_before = len(re.findall(r'\\\[', content))
print(f'Display formulas before: {display_before}')

# Replace \[ with $$
content = content.replace('\\[', '$$')
content = content.replace('\\]', '$$')

# Add formula numbers to standalone $$ ... $$ blocks (not inside aligned or cases)
# Strategy: find all $$...$$ pairs and add sequential \tag{N}
lines = content.split('\n')
in_math = False
math_counter = 0
result = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == '$$' and not in_math:
        in_math = True
        result.append(line)
    elif stripped == '$$' and in_math:
        in_math = False
        math_counter += 1
        # Check if previous line already has \tag or \begin
        has_tag = any('\\tag' in lines[j] for j in range(max(0,i-3), i) if j < len(lines))
        if not has_tag:
            # Add tag before closing $$
            result.append('\\tag{' + str(math_counter) + '}')
        result.append(line)
    else:
        result.append(line)

content = '\n'.join(result)

# Count after
display_after = len(re.findall(r'\$\$', content))
print(f'Display delimiters after: {display_after}')
print(f'Total formula numbers added: {math_counter}')

with open('论文正文.md', 'w') as f:
    f.write(content)
print('Done - 论文正文.md updated')
