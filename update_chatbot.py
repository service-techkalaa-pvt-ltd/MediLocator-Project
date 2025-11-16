import re
import os

def update_prescription_scanner():
    path = 'webapp/templates/accounts/PrescriptionScanner.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove old chatbot CSS block (more lenient regex)
    content = re.sub(
        r'/\* Chatbot Float Button \*/\s*\.chatbot-float\s*\{[^}]*\}.*?\.chatbot-float:hover\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove old chatbot button HTML
    content = re.sub(
        r'<!-- Chatbot Float Button -->.*?</a>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove duplicate @keyframes pulse-bot
    content = re.sub(
        r'@keyframes pulse-bot\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add widget include before closing body tag
    widget_include = '''  <!-- Floating Chatbot Widget -->
  {% include 'accounts/chatbot_widget.html' %}

</body>'''
    
    content = content.replace('</body>', widget_include)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ PrescriptionScanner.html updated!')

def update_index():
    path = 'webapp/templates/accounts/index.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove old chatbot CSS if present
    content = re.sub(
        r'/\* Chatbot Float Button \*/.*?\.chatbot-float:hover\s*\{[^}]*\}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove old chatbot button HTML
    content = re.sub(
        r'<!-- Chatbot Float Button -->.*?</a>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add widget include before closing body tag
    widget_include = '''  <!-- Floating Chatbot Widget -->
  {% include 'accounts/chatbot_widget.html' %}

</body>'''
    
    content = content.replace('</body>', widget_include)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ index.html updated!')

def update_about_us():
    path = 'webapp/templates/accounts/about_us.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove old chatbot button if present
    content = re.sub(
        r'<!-- Chatbot Float Button -->.*?</a>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove inline styles
    content = re.sub(
        r'<style>.*?@keyframes pulse-bot.*?</style>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add widget include before closing body tag
    widget_include = '''  <!-- Floating Chatbot Widget -->
  {% include 'accounts/chatbot_widget.html' %}

</body>'''
    
    content = content.replace('</body>', widget_include)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ about_us.html updated!')

def update_feedback():
    path = 'webapp/templates/accounts/feedback.html'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove old chatbot button if present
    content = re.sub(
        r'<!-- Chatbot Float Button -->.*?</a>\s*',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Remove inline styles
    content = re.sub(
        r'<style>.*?@keyframes pulse-bot.*?</style>',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Add widget include before closing body tag
    widget_include = '''  <!-- Floating Chatbot Widget -->
  {% include 'accounts/chatbot_widget.html' %}

</body>'''
    
    content = content.replace('</body>', widget_include)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ feedback.html updated!')

if __name__ == '__main__':
    try:
        update_prescription_scanner()
        update_index()
        update_about_us()
        update_feedback()
        print('\n✅ ALL PAGES UPDATED SUCCESSFULLY!')
    except Exception as e:
        print(f'❌ Error: {e}')
