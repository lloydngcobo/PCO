#!/usr/bin/env python3
"""
Interactive chat interface for PCO AI Service
Run this for a conversational experience with the AI
"""

import requests
import json
from datetime import datetime
import sys

def chat(message, session_id):
    """Send message to AI and return response"""
    url = "http://localhost:5001/api/ai/chat"
    payload = {"message": message, "session_id": session_id}
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        return response.json()
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out (>300s)"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to AI service at http://localhost:5001"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_context(session_id):
    """Get conversation context"""
    url = f"http://localhost:5001/api/ai/chat/context/{session_id}"
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def clear_context(session_id):
    """Clear conversation context"""
    url = f"http://localhost:5001/api/ai/chat/context/{session_id}"
    try:
        response = requests.delete(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def print_help():
    """Print help message"""
    print("\n" + "=" * 70)
    print("📚 Available Commands:")
    print("=" * 70)
    print("  /help     - Show this help message")
    print("  /new      - Start a new session")
    print("  /context  - Show conversation history")
    print("  /clear    - Clear conversation history")
    print("  /quit     - Exit the chat")
    print("  /exit     - Exit the chat")
    print("\n💡 Tips:")
    print("  - Ask questions about your church members and services")
    print("  - The AI remembers your conversation within a session")
    print("  - Use /new to start fresh on a different topic")
    print("=" * 70 + "\n")

def main():
    print("\n" + "=" * 70)
    print("🤖 PCO AI Chat Assistant - Interactive Mode")
    print("=" * 70)
    print("Type /help for commands, /quit to exit")
    print("-" * 70)
    
    session_id = f"user-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(f"Session ID: {session_id}")
    print("=" * 70 + "\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith('/'):
                command = user_input.lower()
                
                if command in ['/quit', '/exit']:
                    print("\n👋 Goodbye! Thanks for chatting!\n")
                    break
                
                elif command == '/help':
                    print_help()
                    continue
                
                elif command == '/new':
                    session_id = f"user-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                    print(f"\n🔄 New session started: {session_id}\n")
                    continue
                
                elif command == '/context':
                    print("\n📚 Fetching conversation history...\n")
                    context = get_context(session_id)
                    if context.get("success"):
                        print("=" * 70)
                        print(f"Conversation History ({context['context_size']} messages):")
                        print("=" * 70)
                        for i, msg in enumerate(context.get('context', []), 1):
                            role = msg.get('role', 'unknown').upper()
                            content = msg.get('content', '')
                            print(f"\n{i}. {role}:")
                            print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
                        print("\n" + "=" * 70 + "\n")
                    else:
                        print(f"❌ Error: {context.get('error')}\n")
                    continue
                
                elif command == '/clear':
                    result = clear_context(session_id)
                    if result.get("success"):
                        print("\n✅ Conversation history cleared!\n")
                    else:
                        print(f"\n❌ Error: {result.get('error')}\n")
                    continue
                
                else:
                    print(f"\n❌ Unknown command: {user_input}")
                    print("   Type /help for available commands\n")
                    continue
            
            # Send message to AI
            print("\n🤔 Thinking...", end="", flush=True)
            result = chat(user_input, session_id)
            
            # Clear "Thinking..." message
            print("\r" + " " * 20 + "\r", end="", flush=True)
            
            if result.get("success"):
                print("=" * 70)
                print("🤖 AI:")
                print("=" * 70)
                print(f"\n{result['response']}\n")
                print("-" * 70)
                print(f"📊 Context: {result.get('context_size', 0)} messages | "
                      f"⏱️  {result.get('timestamp', '')}")
                print("=" * 70 + "\n")
            else:
                print("=" * 70)
                print("❌ Error:")
                print("=" * 70)
                print(f"\n{result.get('error')}\n")
                print("=" * 70 + "\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! (Ctrl+C pressed)\n")
            break
        
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")

if __name__ == "__main__":
    main()