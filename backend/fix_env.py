"""
Fix .env file - ensure proper format for OPENAI_API_KEY
"""
from pathlib import Path
import re

ENV_FILE = Path(__file__).parent / '.env'

if not ENV_FILE.exists():
    print(f"ERROR: .env file not found at {ENV_FILE}")
    exit(1)

print("Reading .env file...")
with open(ENV_FILE, 'r', encoding='utf-8-sig') as f:
    content = f.read()

print(f"Original file size: {len(content)} characters")
print()

# Find OPENAI_API_KEY
lines = content.splitlines()
new_lines = []
found_openai_key = False

for line in lines:
    stripped = line.strip()
    
    # Check if this is the OPENAI_API_KEY line
    if stripped.startswith('OPENAI_API_KEY'):
        found_openai_key = True
        # Extract the key value
        if '=' in stripped:
            parts = stripped.split('=', 1)
            key_name = parts[0].strip()
            key_value = parts[1].strip()
            
            # Remove any quotes
            if (key_value.startswith('"') and key_value.endswith('"')) or \
               (key_value.startswith("'") and key_value.endswith("'")):
                key_value = key_value[1:-1]
            
            # Remove any trailing whitespace or newlines
            key_value = key_value.rstrip()
            
            # Create clean line
            clean_line = f"{key_name}={key_value}"
            new_lines.append(clean_line)
            print(f"Fixed OPENAI_API_KEY line:")
            print(f"  Old: {repr(line)}")
            print(f"  New: {clean_line}")
            print(f"  Key length: {len(key_value)} characters")
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

if not found_openai_key:
    print("WARNING: OPENAI_API_KEY not found in file!")
    print("Please add it manually:")
    print("OPENAI_API_KEY=your-key-here")
else:
    # Write back the cleaned file
    new_content = '\n'.join(new_lines)
    if new_content and not new_content.endswith('\n'):
        new_content += '\n'
    
    # Backup original
    backup_file = ENV_FILE.with_suffix('.env.backup')
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"\nBackup saved to: {backup_file}")
    
    # Write cleaned version
    with open(ENV_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    
    print(f"Cleaned .env file written")
    print("\nNext steps:")
    print("1. Restart your backend server")
    print("2. The API key should now load correctly")


