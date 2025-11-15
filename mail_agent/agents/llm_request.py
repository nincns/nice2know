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
        
        Args:
            prompt: User prompt
            system_prompt: System/instruction prompt
            json_schema: Expected JSON structure (for validation)
        
        Returns:
            Generated text or None on error
        """
        if not self.test_connection():
            return None
        
        # Build enhanced prompt for JSON
        if json_schema:
            full_prompt = f"{system_prompt}\n\n{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No explanations. No markdown. Just JSON."
        else:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        # Build request with strict JSON formatting
        data = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.1,  # Low temperature for consistent output
            "top_p": 0.9
        }
        
        # Force JSON format in Ollama
        if json_schema:
            data["format"] = "json"
        
        if system_prompt and not json_schema:
            data["system"] = system_prompt
        
        try:
            print(f"[LLM] Sending request...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=120  # 2 minutes for large responses
            )
            
            if response.status_code == 200:
                result = response.json()
                generated = result.get('response', '').strip()
                
                print(f"[LLM] ✓ Response received ({len(generated)} chars)")
                
                # Clean up markdown code blocks if present
                if generated.startswith('```'):
                    lines = generated.split('\n')
                    # Remove first line (```json or ```) and last line (```)
                    if len(lines) > 2:
                        generated = '\n'.join(lines[1:-1]).strip()
                
                # Validate and format JSON if schema provided
                if json_schema:
                    try:
                        parsed = json.loads(generated)
                        print(f"[LLM] ✓ Valid JSON structure")
                        return json.dumps(parsed, indent=2, ensure_ascii=False)
                    except json.JSONDecodeError as e:
                        print(f"[LLM] ⚠️  Invalid JSON: {e}")
                        print(f"[LLM]    Raw response (first 500 chars):")
                        print(f"[LLM]    {generated[:500]}")
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
                print(f"[LLM]    {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[LLM] ✗ Request timeout (>120s)")
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
    if args.mailbody:
        mail_content = load_file(args.mailbody)
        if not mail_content:
            sys.exit(1)
    
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
