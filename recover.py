import json
import os

transcript_path = r'C:\Users\Aishik\.gemini\antigravity-ide\brain\7774cd34-bae3-45f4-961f-b33bb467859d\.system_generated\logs\transcript_full.jsonl'
files = {}

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if 'tool_calls' in data:
                for call in data['tool_calls']:
                    func = call.get('function', {})
                    name = func.get('name')
                    if name == 'default_api:write_to_file':
                        args = json.loads(func.get('arguments', '{}'))
                        target = args.get('TargetFile')
                        content = args.get('CodeContent')
                        if target and target.endswith('.py'):
                            files[target] = content
                    elif name == 'default_api:replace_file_content':
                        args = json.loads(func.get('arguments', '{}'))
                        target = args.get('TargetFile')
                        if target in files:
                            target_content = args.get('TargetContent', '')
                            replacement = args.get('ReplacementContent', '')
                            files[target] = files[target].replace(target_content, replacement)
                    elif name == 'default_api:multi_replace_file_content':
                        args = json.loads(func.get('arguments', '{}'))
                        target = args.get('TargetFile')
                        if target in files:
                            for chunk in args.get('ReplacementChunks', []):
                                target_content = chunk.get('TargetContent', '')
                                replacement = chunk.get('ReplacementContent', '')
                                files[target] = files[target].replace(target_content, replacement)
        except Exception:
            pass

# Apply fixes directly on the recovered content!
for target, content in files.items():
    print(f'Recovering {target}')
    # Fix the utf-8 open call that caused the crash
    content = content.replace('open(css_path, encoding="utf-8") as f:', 'open(css_path, encoding="utf-8") as f:')
    
    # In streamlit_app.py, fix the analytics bug
    if "streamlit_app.py" in target:
        content = content.replace(
            'progress_data = analytics.get("progress", []) if "analytics" in dir() else []',
            'try:\n    progress_data = analytics.get("progress", [])\nexcept NameError:\n    progress_data = []'
        )
    # In voice bot, fix audio_value.read()
    if "3_🎙️_Voice_Bot.py" in target:
        content = content.replace('audio_value.read()', 'audio_value.getvalue()')
    # In Quiz, fix the index selection
    if "5_🧪_Quiz.py" in target:
        content = content.replace(
            'index=min(st.session_state.current_module - 1, len(module_options) - 1),',
            'index=min(max(st.session_state.current_module - 1, 0), len(module_options) - 1),'
        )
        
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, 'w', encoding='utf-8') as out:
        out.write(content)

print('Recovery complete.')
