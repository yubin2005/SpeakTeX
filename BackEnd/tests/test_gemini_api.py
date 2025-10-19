"""
Test Gemini API Connectivity and Text Generation
Tests Gemini API for LaTeX conversion capability
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in backend directory
backend_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=backend_dir / '.env')

# Gemini API configuration from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# Validate that API key is loaded
if not GEMINI_API_KEY:
    raise ValueError(
        "Gemini API key not found. Please ensure .env file exists in backend/ directory with:\n"
        "  GEMINI_API_KEY=your_api_key"
    )


def test_gemini_api():
    """Test Gemini API with a simple LaTeX conversion request"""
    
    print("\n" + "="*60)
    print("Testing Gemini API...")
    print("="*60 + "\n")
    
    # Test prompt
    test_prompt = "Convert this to LaTeX: x squared"
    print(f'Sending request: "{test_prompt}"')
    print()
    
    # Prepare request
    url = f"{GEMINI_ENDPOINT}?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": test_prompt
                    }
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Send request
        print("Sending HTTP request... ", end="", flush=True)
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        
        # Check response status
        if response.status_code == 200:
            print("✅")
            print("Response received ✅\n")
            
            # Parse response
            result = response.json()
            
            # Extract generated text
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    generated_text = candidate['content']['parts'][0]['text']
                    print(f"Generated text: {generated_text.strip()}")
                    
                    # Check if response contains LaTeX-like content
                    if 'x^2' in generated_text or 'x^{2}' in generated_text or 'LaTeX' in generated_text:
                        print("\n" + "="*60)
                        print("✅ Gemini API working!")
                        print("="*60 + "\n")
                        return True
                    else:
                        print(f"\n⚠️  API responded but content may not be LaTeX: {generated_text}")
                        print("\n" + "="*60)
                        print("✅ Gemini API working (but check response format)")
                        print("="*60 + "\n")
                        return True
            
            print("\n❌ Unexpected response format")
            print(f"Full response: {json.dumps(result, indent=2)}")
            return False
            
        else:
            print(f"❌\n")
            print(f"HTTP Status: {response.status_code}")
            print(f"Response: {response.text}")
            print("\n" + "="*60)
            print("❌ Gemini API request failed")
            print("="*60 + "\n")
            return False
            
    except requests.exceptions.Timeout:
        print("❌\n")
        print("Error: Request timed out")
        print("\n" + "="*60)
        print("❌ Gemini API timeout")
        print("="*60 + "\n")
        return False
        
    except requests.exceptions.RequestException as e:
        print("❌\n")
        print(f"Network error: {str(e)}")
        print("\n" + "="*60)
        print("❌ Gemini API connection failed")
        print("="*60 + "\n")
        return False
        
    except json.JSONDecodeError as e:
        print("❌\n")
        print(f"JSON parsing error: {str(e)}")
        print(f"Response text: {response.text}")
        print("\n" + "="*60)
        print("❌ Gemini API response parsing failed")
        print("="*60 + "\n")
        return False
        
    except Exception as e:
        print("❌\n")
        print(f"Unexpected error: {str(e)}")
        print("\n" + "="*60)
        print("❌ Gemini API test failed")
        print("="*60 + "\n")
        return False


def main():
    """Main test function"""
    return test_gemini_api()


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

