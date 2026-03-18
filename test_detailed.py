#!/usr/bin/env python
import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import Client
import json

try:
    client = Client()
    
    print("="*60)
    print("Test 1: Informational query - 'what is paracetamol used for'")
    print("="*60)
    
    response = client.post('/chatbot-response/', 
        {'user_message': 'what is paracetamol used for'},
        HTTP_X_REQUESTED_WITH='XMLHttpRequest'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.content.decode('utf-8')}")
    
    if response.status_code == 200:
        try:
            result = json.loads(response.content)
            print(f"\nParsed Response:")
            print(f"  Type: {result.get('type')}")
            print(f"  Is Info Query: {result.get('is_info_query')}")
            print(f"  Has Medicine Info: {'medicine_info_html' in result}")
            print(f"  Medicines: {[m.get('name') for m in result.get('medicines', [])]}")
        except Exception as parse_error:
            print(f"Error parsing JSON: {parse_error}")
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
