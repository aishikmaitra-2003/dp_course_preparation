import glob
import re
import os

# Update all python files (mostly inline styles with purple)
py_files = glob.glob('**/*.py', recursive=True)
for f in py_files:
    if f in ['change_color.py', 'recover.py', 'recover2.py', 'streamlit_app.py'] or f.startswith('pages'):
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Change purple to Azure Electric Blue (#0078d4 or #2563eb)
        # We will use #2563eb for vibrant blue
        new_content = content.replace('#2563eb', '#2563eb')
        new_content = new_content.replace('37,99,235', '37,99,235')
        new_content = new_content.replace('37, 99, 235', '37, 99, 235')
        new_content = new_content.replace('--accent-primary', '--accent-primary')
        new_content = new_content.replace('badge-primary', 'badge-primary')
        
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)

# Update style.css specifically
css_path = 'assets/style.css'
with open(css_path, 'r', encoding='utf-8') as file:
    css = file.read()

# Replace colors in CSS
css = css.replace('#2563eb', '#2563eb')
css = css.replace('37, 99, 235', '37, 99, 235')
css = css.replace('37,99,235', '37, 99, 235')
css = css.replace('--accent-primary', '--accent-primary')
css = css.replace('badge-primary', 'badge-primary')

# Fix chat message selectors
css = css.replace('[data-testid="stChatMessage"]:has([aria-label="🧑‍💻"])', '[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])')
css = css.replace('[data-testid="stChatMessage"]:has([aria-label="🤖"])', '[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])')

with open(css_path, 'w', encoding='utf-8') as file:
    file.write(css)

print("Colors and layout updated!")
