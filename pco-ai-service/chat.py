#!/usr/bin/env python3
"""
Simple command-line chat interface for PCO AI Service
Usage: python chat.py "Your message" [session_id]
"""

import sys
import requests
import json

def chat(message, session_id="default"):
    """Send a message to the AI chat service"""
    url = "http://localhost:5001/api/ai/chat"
    
    payload = {
        "message": message,
        "session_id": session_id
    }
    
    print(f"\n🤔 Sending message to AI...\n")
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        result = response.json()
        
        if result.get("success"):
            print("=" * 70)
            print(f"🤖 AI Response:")
            print("=" * 70)
            print(f"\n{result['response']}\n")
            print("-" * 70)
            print(f"📊 Context size: {result.get('context_size', 0)} messages")
            print(f"🆔 Session ID: {session_id}")
            print(f"⏱️  Timestamp: {result.get('timestamp', '')}")
            print("=" * 70)
        else:
            print("=" * 70)
            print(f"❌ Error:")
            print("=" * 70)
            print(f"\n{result.get('error', 'Unknown error')}\n")
            print("=" * 70)
        
        return result
        
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out. The AI is taking too long to respond.")
        print("   Try a simpler question or wait a moment and try again.\n")
        return {"success": False, "error": "Timeout"}
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to AI service.")
        print("   Make sure the service is running on http://localhost:5001\n")
        return {"success": False, "error": "Connection error"}
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        return {"success": False, "error": str(e)}

def main():
    if len(sys.argv) < 2:
        print("\n" + "=" * 70)
        print("💬 PCO AI Chat - Command Line Interface")
        print("=" * 70)
        print("\nUsage:")
        print('  python chat.py "Your message here" [session_id]')
        print("\nExamples:")
        print('  python chat.py "Hello! What can you help me with?"')
        print('  python chat.py "How many members do we have?" user123')
        print('  python chat.py "Show me active members" user123')
        print("\nTips:")
        print("  - Use the same session_id for related questions")
        print("  - The AI remembers your conversation within a session")
        print("  - Start a new session_id for unrelated topics")
        print("=" * 70 + "\n")
        sys.exit(1)
    
    message = sys.argv[1]
    session_id = sys.argv[2] if len(sys.argv) > 2 else "default"
    
    chat(message, session_id)

if __name__ == "__main__":
    main()