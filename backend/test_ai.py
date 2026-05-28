import sys
sys.path.append('.')

from app.services.ai_service import AIService

ai = AIService()

print("Testing OpenRouter API connection...")

if ai.test_connection():
    print("✅ OpenRouter API connected successfully!")
else:
    print("❌ OpenRouter API connection failed!")