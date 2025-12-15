import json
import pandas as pd
from datetime import datetime

# Load the exported JSON
with open('assets/erinGPTfile/conversations.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Flatten into a list of message records
messages = []
for convo in data:
    title = convo.get('title', 'Untitled')
    create_time = datetime.fromtimestamp(convo.get('create_time', 0))
    for msg in convo.get('mapping', {}).values():
        info = msg.get('message')
        if info and info.get('content') and info['content'].get('parts'):
            role = info.get('author', {}).get('role', 'unknown')
            content = info['content']['parts'][0]
            messages.append({
                'conversation_title': title,
                'timestamp': create_time,
                'role': role,
                'content': content
            })

# Create DataFrame
df = pd.DataFrame(messages)

# Optional: Filter out system/internal messages
df = df[df['role'].isin(['user', 'assistant'])]

# Save cleaned data
df.to_csv('cleaned_chatgpt_history.csv', index=False)
print(f"Exported {len(df)} messages to CSV.")