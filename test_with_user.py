#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import json

# Create or get a test user
user, created = User.objects.get_or_create(username='testuser', defaults={'email': 'test@test.com'})

client = Client()

# First test: without login (test as anonymous user)
print("="*60)
print("Test 1: Anonymous user - 'what is paracetamol used for'")
print("="*60)

response = client.post('/chatbot-response/', 
    {'user_message': 'what is paracetamol used for'},
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

print(f"Status: {response.status_code}")
print(f"Content: {response.content.decode('utf-8')[:500]}")

try:
    result = json.loads(response.content)
    if result.get('type') == 'medicine_search':
        print("\n✅ SUCCESS: Medicine search response!")
        print(f"  is_info_query: {result.get('is_info_query')}")
        print(f"  medicine_info_html present: {'medicine_info_html' in result}")
        if result.get('medicine_info_html'):
            print(f"  medicine_info_html length: {len(result.get('medicine_info_html', ''))}")
    else:
        print(f"\n⚠️ Response type: {result.get('type')}")
        print(f"  Bot reply: {result.get('bot_reply')[:200]}")
except Exception as e:
    print(f"Error: {e}")
