#!/usr/bin/env python
import os
import django
import json

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
result = json.loads(response.content)
print("Response Type:", result.get('type'))
print("Medicine Found:", result.get('medicine_found'))
print("Is Info Query:", result.get('is_info_query'))
print("Has Medicine Info:", 'medicine_info_html' in result)
print("\nMedicines:", [m['name'] for m in result.get('medicines', [])])
print("Total Pharmacies:", result.get('total_pharmacies'))

if result.get('medicine_info_html'):
    print("\n✅ Medicine Info HTML generated successfully!")
    print("Success! The response includes medicine information.")
else:
    print("\n⚠️ Medicine Info HTML NOT found in response")

print("\n" + "="*60)
print("Testing: 'find paracetamol near me'")
response2 = client.post('/chatbot-response/', 
    {'user_message': 'find paracetamol near me'},
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

result2 = json.loads(response2.content)
print("Is Info Query:", result2.get('is_info_query'))
print("Has Medicine Info:", 'medicine_info_html' in result2)
print("This request should NOT include medicine info (locational query)")

print("\n" + "="*60)
print("Testing: 'side effects of levosiz'")
response3 = client.post('/chatbot-response/', 
    {'user_message': 'side effects of levosiz'},
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

result3 = json.loads(response3.content)
print("Is Info Query:", result3.get('is_info_query'))
print("Has Medicine Info:", 'medicine_info_html' in result3)
print("Medicine Found:", result3.get('medicine_found'))
if 'medicine_info_html' in result3:
    print("✅ Levosiz information retrieved!")
