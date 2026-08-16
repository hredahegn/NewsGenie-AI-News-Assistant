from pathlib import Path
import re
import textwrap

workflow_path = Path('.github/workflows/bright_ui_once.yml')
app_path = Path('app.py')

workflow_text = workflow_path.read_text()
match = re.search(r"css = r'''(.*?)'''", workflow_text, flags=re.S)
if not match:
    raise SystemExit('Could not find embedded CSS payload in workflow file')

css = textwrap.dedent(match.group(1)).strip('\n')
app_text = app_path.read_text()
updated, count = re.subn(
    r'<style>.*?</style>',
    '<style>\n' + css + '\n    </style>',
    app_text,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f'Expected one style block, replaced {count}')

app_path.write_text(updated)
print('Applied bright 3D NewsGenie UI CSS')
