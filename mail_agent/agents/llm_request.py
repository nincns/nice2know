#!/usr/bin/env python3
"""
Nice2Know - LLM Request Script
Standalone script for making LLM requests with prompts and structured output
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import requests

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.credentials import get_credentials

class LLMClient:
    def __init__(self, provider: str = "ollama"):
        """Initialize LLM client with credentials"""
        creds = get_credentials()

        # Nutze die Convenience-Methode
        try:
            llm_config = creds.get_llm_config()
        except KeyError:
            print("[LLM] ⚠️  No 'llm' configuration in secrets.json")
            llm_config = {}

        self.provider = provider
        provider_config = llm_config.get(provider, {})

        self.base_url = provider_config.get('base_url', 'http://localhost:11434')
        self.model = provider_config.get('model', 'llama3:8b')
        self.api_key = provider_config.get('api_key')

        print(f"[LLM] Provider: {self.provider}")
        print(f"[LLM] Base URL: {self.base_url}")
        print(f"[LLM] Model:    {self.model}")
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                print(f"[LLM] ✓ Connection OK - {len(models)} models available")
                
                # Check if our model exists
                model_names = [m['name'] for m in models]
                if self.model in model_names:
                    print(f"[LLM] ✓ Model '{self.model}' found")
                    return True
                else:
                    print(f"[LLM] ⚠️  Model '{self.model}' not found")
                    print(f"[LLM]    Available: {', '.join(model_names)}")
                    return False
            else:
                print(f"[LLM] ✗ Connection failed: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"[LLM] ✗ Cannot connect to {self.base_url}")
            print(f"[LLM]    Is Ollama running? Try: ollama serve")
            return False
        except Exception as e:
            print(f"[LLM] ✗ Error: {e}")
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None,
                 json_schema: Optional[Dict] = None) -> Optional[str]:
        """
        Generate response from LLM with strict JSON enforcement
        """
        if not self.test_connection():
            return None
        
        # Build enhanced prompt with schema as example
        if json_schema and system_prompt:
            # Format schema as example
            schema_example = json.dumps(json_schema, indent=2, ensure_ascii=False)
            full_prompt = f"""{system_prompt}

EXPECTED JSON STRUCTURE (use this as template):
{schema_example}

EMAIL TO ANALYZE:
{prompt}

Remember: Return ONLY valid JSON matching the structure above. No explanations."""
        elif system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            full_prompt = prompt
        
        # Build request with strict JSON formatting
        data = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.1,
            "top_p": 0.9,
            "format": "json"  # Force JSON
        }
        
        try:
            print(f"[LLM] Sending request...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                generated = result.get('response', '').strip()
                
                print(f"[LLM] ✓ Response received ({len(generated)} chars)")
                
                # Clean up markdown if present
                if generated.startswith('```'):
                    lines = generated.split('\n')
                    if len(lines) > 2:
                        generated = '\n'.join(lines[1:-1]).strip()
                
                # Validate and format JSON
                if json_schema:
                    try:
                        parsed = json.loads(generated)
                        
                        # POST-PROCESSING: Fix IDs based on mail_id
                        import re
                        
                        # Extract mail_id if we have mailbody path
                        mail_id_base = None
                        if hasattr(self, '_current_mail_id'):
                            mail_id_base = self._current_mail_id
                        
                        if mail_id_base:
                            print(f"[LLM] Using mail_id base: {mail_id_base[:16]}...")
                            
                            # Fix solution ID
                            if 'type' in parsed and parsed['type'] == 'n2k_solution':
                                if 'id' in parsed and ('demo' in parsed['id'] or '123456' in parsed['id']):
                                    parsed['id'] = f"sol_{mail_id_base}"
                                    print(f"[LLM] ✓ Generated solution ID from mail")
                            
                            # Fix problem ID
                            if 'type' in parsed and parsed['type'] == 'n2k_problem':
                                if 'id' in parsed and ('demo' in parsed['id'] or '123456' in parsed['id']):
                                    parsed['id'] = f"prob_{mail_id_base}"
                                    print(f"[LLM] ✓ Generated problem ID from mail")
                            
                            # Fix problem_ids array (in solution)
                            if 'problem_ids' in parsed:
                                new_problem_ids = []
                                for pid in parsed['problem_ids']:
                                    if 'demo' in pid or '123456' in pid:
                                        new_problem_ids.append(f"prob_{mail_id_base}")
                                        print(f"[LLM] ✓ Generated problem_id from mail")
                                    else:
                                        new_problem_ids.append(pid)
                                parsed['problem_ids'] = new_problem_ids
                            
                            # Fix mail_id field
                            if 'mail_id' in parsed:
                                parsed['mail_id'] = mail_id_base
                                print(f"[LLM] ✓ Set mail_id")
                        
                        print(f"[LLM] ✓ Valid JSON structure")
                        return json.dumps(parsed, indent=2, ensure_ascii=False)
                    except json.JSONDecodeError as e:
                        print(f"[LLM] ⚠️  Invalid JSON: {e}")
                        print(f"[LLM]    Attempting to extract JSON...")
                        
                        # Try to find JSON in response
                        start = generated.find('{')
                        end = generated.rfind('}')
                        if start != -1 and end != -1 and start < end:
                            json_candidate = generated[start:end+1]
                            try:
                                parsed = json.loads(json_candidate)
                                print(f"[LLM] ✓ Extracted valid JSON")
                                return json.dumps(parsed, indent=2, ensure_ascii=False)
                            except:
                                pass
                        
                        return None
                
                return generated
            else:
                print(f"[LLM] ✗ Request failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[LLM] ✗ Error: {e}")
            return None

def load_file(filepath: Path) -> Optional[str]:
    """Load text file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"[FILE] Loaded: {filepath.name} ({len(content)} chars)")
        return content
    except Exception as e:
        print(f"[FILE] ✗ Failed to load {filepath}: {e}")
        return None

def load_json_schema(filepath: Path) -> Optional[Dict]:
    """Load JSON schema file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        print(f"[SCHEMA] Loaded: {filepath.name}")
        return schema
    except Exception as e:
        print(f"[SCHEMA] ✗ Failed to load {filepath}: {e}")
        return None

def extract_mail_id(mailbody_path: Path) -> Optional[str]:
    """
    Extract message ID from mail filename
    Filename format: YYYYMMDD_HHMMSS_<UUID>@domain.eml
    Returns: UUID part without hyphens (lowercase hex)
    """
    try:
        filename = mailbody_path.stem  # Without .eml
        # Split by @ to get part before domain
        if '@' in filename:
            before_at = filename.split('@')[0]
        else:
            before_at = filename
        
        # Extract UUID part (after last underscore)
        parts = before_at.split('_')
        if len(parts) >= 3:
            uuid_part = parts[-1]  # Last part is UUID
        else:
            uuid_part = before_at
        
        # Remove all hyphens and convert to lowercase
        mail_id = uuid_part.replace('-', '').lower()
        
        # Validate it's hex (32 chars)
        if len(mail_id) >= 32 and all(c in '0123456789abcdef' for c in mail_id[:32]):
            return mail_id[:32]
        else:
            print(f"[MAIL_ID] ⚠️  Invalid UUID format in filename: {mailbody_path.name}")
            return None
    except Exception as e:
        print(f"[MAIL_ID] ✗ Failed to extract mail ID: {e}")
        return None

def save_output(content: str, filepath: Path):
    """Save generated content to file"""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OUTPUT] Saved: {filepath}")
    except Exception as e:
        print(f"[OUTPUT] ✗ Failed to save {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(
        description='Nice2Know LLM Request Script',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test connection
  python llm_request.py --test

  # Simple prompt
  python llm_request.py --prompt "Hello, how are you?"

  # With system prompt from file
  python llm_request.py --pre_prompt catalog/prompts/extract_asset.txt \\
                        --mailbody storage/mails/test.eml

  # With JSON schema validation
  python llm_request.py --pre_prompt catalog/prompts/extract_problem.txt \\
                        --json catalog/json_store/problem_schema.json \\
                        --mailbody storage/mails/test.eml \\
                        --export storage/processed/test_problem.json
        """
    )
    
    # Connection test
    parser.add_argument('--test', action='store_true',
                        help='Test LLM connection and exit')
    
    # Input
    parser.add_argument('--prompt', type=str,
                        help='Direct prompt text')
    parser.add_argument('--pre_prompt', type=Path,
                        help='System/instruction prompt file')
    parser.add_argument('--mailbody', type=Path,
                        help='Mail file (.eml or .txt) to analyze')
    
    # Output validation
    parser.add_argument('--json', type=Path,
                        help='JSON schema file for validation')
    
    # Export
    parser.add_argument('--export', type=Path,
                        help='Output file path')
    
    # Provider
    parser.add_argument('--provider', type=str, default='ollama',
                        choices=['ollama', 'openai', 'anthropic'],
                        help='LLM provider (default: ollama)')
    
    args = parser.parse_args()
    
    # Initialize client
    client = LLMClient(provider=args.provider)
    
    # Test mode
    if args.test:
        success = client.test_connection()
        sys.exit(0 if success else 1)
    
    # Load system prompt
    system_prompt = None
    if args.pre_prompt:
        system_prompt = load_file(args.pre_prompt)
        if not system_prompt:
            sys.exit(1)
    
    # Load mail body
    mail_content = None
    mail_id = None
    if args.mailbody:
        mail_content = load_file(args.mailbody)
        if not mail_content:
            sys.exit(1)
        
        # Extract mail ID from filename
        mail_id = extract_mail_id(args.mailbody)
        if mail_id:
            print(f"[MAIL_ID] Extracted: {mail_id[:16]}...{mail_id[-8:]}")
    
    # Build prompt
    if args.prompt:
        user_prompt = args.prompt
    elif mail_content:
        user_prompt = f"Analyze the following email:\n\n{mail_content}"
    else:
        print("[ERROR] No prompt or mailbody provided!")
        parser.print_help()
        sys.exit(1)
    
    # Load JSON schema
    json_schema = None
    if args.json:
        json_schema = load_json_schema(args.json)
        if not json_schema:
            sys.exit(1)
    
    # Generate
    print("\n" + "=" * 60)
    
    # Pass mail_id to client for post-processing
    if mail_id:
        client._current_mail_id = mail_id
    
    response = client.generate(user_prompt, system_prompt, json_schema)
    print("=" * 60 + "\n")
    
    if response:
        # Print to console
        print(response)
        
        # Export if requested
        if args.export:
            save_output(response, args.export)
        
        sys.exit(0)
    else:
        print("[ERROR] Failed to generate response")
        sys.exit(1)

if __name__ == "__main__":
    main()
