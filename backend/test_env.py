from dotenv import load_dotenv
import os

print("Current directory:", os.getcwd())
print(".env file exists:", os.path.exists('.env'))
print(".env absolute path:", os.path.abspath('.env'))

load_dotenv('.env')
api_key = os.getenv('OPENAI_API_KEY')
print(f"API key loaded: {api_key is not None}")
if api_key:
    print(f"API key starts with: {api_key[:20]}...")
