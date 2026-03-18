#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.test import Client
import json

client = Client()

print("="*80)
print("Full Test: Medicine Information Query")
print("="*80)

response = client.post('/chatbot-response/', 
    data=json.dumps({'user_message': 'what is paracetamol used for'}),
    content_type='application/json',
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

result = json.loads(response.content)
print(f"\n✅ Response Type: {result.get('type')}")
print(f"✅ Medicine Found: {result.get('medicine_found')}")
print(f"✅ Is Info Query: {result.get('is_info_query')}")

print(f"\nMedicines Found:")
for med in result.get('medicines', [])[:2]:
    print(f"  - {med['name']} ({med['generic_name']})")

print(f"\n📊 Pharmacies: {result.get('total_pharmacies')} pharmacies have this medicine")

if result.get('medicine_info_html'):
    print(f"\n💊 Medicine Information:")
    info_html = result['medicine_info_html']
    # Extract key info from HTML
    if 'What is it used for?' in info_html:
        print("  ✓ Has 'Usage' section")
    if 'Typical Dosage' in info_html:
        print("  ✓ Has 'Dosage' section")
    if 'Side Effects' in info_html:
        print("  ✓ Has 'Side Effects' section")
    if 'Precautions' in info_html:
        print("  ✓ Has 'Precautions' section")
    
    print(f"\n📝 HTML Content Preview (first 400 chars):")
    print(info_html[:400])

print("\n" + "="*80)
print("Test: Locational Query (should NOT have medicine info)")
print("="*80)

response2 = client.post('/chatbot-response/', 
    data=json.dumps({'user_message': 'find paracetamol near me'}),
    content_type='application/json',
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

result2 = json.loads(response2.content)
print(f"Is Info Query: {result2.get('is_info_query')}")
print(f"Has Medicine Info: {'medicine_info_html' in result2}")
if not result2.get('is_info_query'):
    print("✅ Correct: Locational query doesn't include medicine info")

print("\n" + "="*80)
print("Test: Side Effects Query")
print("="*80)

response3 = client.post('/chatbot-response/', 
    data=json.dumps({'user_message': 'side effects of levosiz'}),
    content_type='application/json',
    HTTP_X_REQUESTED_WITH='XMLHttpRequest'
)

result3 = json.loads(response3.content)
print(f"Medicine Found: {result3.get('medicine_found')}")
print(f"Is Info Query: {result3.get('is_info_query')}")
print(f"Has Medicine Info: {'medicine_info_html' in result3}")
print(f"First Medicine: {result3.get('medicines')[0]['name'] if result3.get('medicines') else 'None'}")
