#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import Client
import json

client = Client()

print("="*60)
print("Test: Sending JSON request properly")
print("="*60)

# Send as JSON with proper content-type
response = client.post('/chatbot-response/', 
    data=json.dumps({'user_message': 'what is paracetamol used for'}),
    content_type='application/json',
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

print(f"Status: {response.status_code}")
print(f"Content: {response.content.decode('utf-8')[:800]}")

try:
    result = json.loads(response.content)
    print(f"\nResponse type: {result.get('type')}")
    if result.get('type') == 'medicine_search':
        print(f"✅ Medicine search!")
        print(f"  medicine_found: {result.get('medicine_found')}")
        print(f"  is_info_query: {result.get('is_info_query')}")
        print(f"  medicine_info_html: {'medicine_info_html' in result}")
except Exception as e:
    print(f"  Error parsing: {e}")
