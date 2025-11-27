"""
Diagnostic script to check .env file and API key loading
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("Environment Variable Diagnostic")
print("=" * 60)
print()

# Get the backend directory
BASE_DIR = Path(__file__).parent.absolute()
ENV_FILE = BASE_DIR / '.env'

print(f"Backend directory: {BASE_DIR}")
print(f".env file path: {ENV_FILE}")
print(f".env file exists: {ENV_FILE.exists()}")
print()

if ENV_FILE.exists():
    print("Reading .env file...")
    print("-" * 60)
    
    # Read raw file content (handle BOM if present)
    with open(ENV_FILE, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    print(f"Total lines in .env: {len(lines)}")
    print()
    
    # Check for OPENAI_API_KEY
    found_key = False
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if line_stripped.startswith('OPENAI_API_KEY'):
            found_key = True
            print(f"FOUND: OPENAI_API_KEY on line {i}")
            print(f"   Raw line: {repr(line)}")
            
            # Parse the value
            if '=' in line_stripped:
                parts = line_stripped.split('=', 1)
                key_name = parts[0].strip()
                key_value = parts[1].strip()
                
                # Remove quotes if present
                if (key_value.startswith('"') and key_value.endswith('"')) or \
                   (key_value.startswith("'") and key_value.endswith("'")):
                    key_value = key_value[1:-1]
                
                print(f"   Key name: {key_name}")
                print(f"   Key value length: {len(key_value)} characters")
                
                if len(key_value) == 0:
                    print("   WARNING: Key value is EMPTY!")
                elif len(key_value) < 20:
                    print(f"   WARNING: Key seems too short (expected ~50+ chars)")
                    print(f"   First 10 chars: {key_value[:10]}...")
                else:
                    print(f"   OK: Key value looks valid")
                    print(f"   First 10 chars: {key_value[:10]}...")
                    print(f"   Last 4 chars: ...{key_value[-4:]}")
            else:
                print("   WARNING: No '=' found in line")
            
            print()
    
    if not found_key:
        print("ERROR: OPENAI_API_KEY not found in .env file")
        print()
        print("Available keys in .env:")
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            if line_stripped and not line_stripped.startswith('#'):
                if '=' in line_stripped:
                    key_name = line_stripped.split('=', 1)[0].strip()
                    try:
                        print(f"   Line {i}: {key_name}")
                    except:
                        print(f"   Line {i}: (key name contains special characters)")
        print()
else:
    print("ERROR: .env file does not exist!")
    print(f"   Expected location: {ENV_FILE}")
    print()

# Try loading with dotenv
print("=" * 60)
print("Testing dotenv loading...")
print("=" * 60)
print()

load_dotenv(ENV_FILE)
loaded_key = os.getenv('OPENAI_API_KEY')

if loaded_key:
    print("SUCCESS: OPENAI_API_KEY loaded successfully!")
    print(f"   Length: {len(loaded_key)} characters")
    print(f"   First 10 chars: {loaded_key[:10]}...")
    print(f"   Last 4 chars: ...{loaded_key[-4:]}")
else:
    print("ERROR: OPENAI_API_KEY not loaded by dotenv")
    print()
    print("Common issues:")
    print("   1. Key name has typos (should be exactly 'OPENAI_API_KEY')")
    print("   2. Key value is empty")
    print("   3. Extra spaces around the '=' sign")
    print("   4. Quotes around the value (may cause issues)")
    print("   5. .env file has wrong encoding")

print()
print("=" * 60)
print("Recommendations:")
print("=" * 60)
print()
print("Your .env file should look like this:")
print()
print("OPENAI_API_KEY=sk-proj-...your-actual-key-here...")
print()
print("NOT like this:")
print("  OPENAI_API_KEY = sk-...  (spaces around =)")
print("  OPENAI_API_KEY='sk-...'  (quotes)")
print("  OPENAI_API_KEY=          (empty)")
print("  openai_api_key=sk-...    (wrong case)")
print()

