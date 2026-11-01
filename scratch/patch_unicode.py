"""Patch pipeline files for Windows UTF-8 stdout and unicode arrows."""
import os, sys

files = [
    'ml/pipeline/embedding.py',
    'ml/pipeline/graph_builder.py',
    'ml/pipeline/train_gat.py',
    'ml/pipeline/train_ensemble.py',
    'ml/pipeline/run_full_pipeline.py',
]

utf8_header = (
    'import sys\n'
    'if sys.platform == "win32":\n'
    '    sys.stdout.reconfigure(encoding="utf-8", errors="replace")\n'
)

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    # Replace unicode arrows / dashes
    content = content.replace('\u2192', '>>').replace('\u2013', '-').replace('\u2014', '--')
    # Add header if not already present
    if 'sys.stdout.reconfigure' not in content:
        # Find end of module docstring, insert after it
        lines = content.split('\n')
        insert_idx = 0
        in_doc = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('"""') and not in_doc:
                in_doc = True
                if stripped.count('"""') >= 2 and len(stripped) > 6:
                    insert_idx = i + 1
                    in_doc = False
                    break
            elif in_doc and '"""' in stripped:
                insert_idx = i + 1
                in_doc = False
                break
        lines.insert(insert_idx, utf8_header)
        content = '\n'.join(lines)
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Patched: {fpath}')

print('All files patched.')
