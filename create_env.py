# Create .env file with proper UTF-8 encoding
with open('.env', 'w', encoding='utf-8') as f:
    f.write('Username=User\n')
    f.write('Assistantname=Bloom\n')
    f.write('GroqAPIKey=gsk_BVgwZHgPMGZdnfEqwvIhujWEZvJEOYvgMVXAW96RiIAXwROb\n')  # This is a placeholder key, won't work
    f.write('CohereAPIKey=1234567890abcdefghijklmnopqrstuvwxyz\n')  # This is a placeholder key, won't work
    f.write('InputLanguage=en-US\n')
    f.write('AssistantVoice=en-US-AriaNeural\n') 