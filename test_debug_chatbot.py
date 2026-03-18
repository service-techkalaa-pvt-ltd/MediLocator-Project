#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import Client

client = Client()

# Test informational query about paracetamol
print("Testing: 'what is paracetamol used for'")
response = client.post('/chatbot-response/', 
    {'user_message': 'what is paracetamol used for'},
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

print("Status Code:", response.status_code)
print("Response Content:", response.content)
print("\nResponse Text:", response.content.decode('utf-8'))
