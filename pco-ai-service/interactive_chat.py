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

def add_person(first_name, last_name, gender=None, birthdate=None, email=None):
    """Add a new person to PCO"""
    url = "http://localhost:5000/api/people"
    payload = {
        "first_name": first_name,
        "last_name": last_name
    }
    
    if gender:
        payload["gender"] = gender
    if birthdate:
        payload["birthdate"] = birthdate
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        # Check HTTP status code (200 OK or 201 Created are both success)
        if response.status_code not in [200, 201]:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
        
        result = response.json()
        
        # Check if person was created (API returns id and data)
        if result.get("id") and result.get("data"):
            result["success"] = True
            
            # If email provided, add it
            if email:
                person_id = result["id"]
                email_url = f"http://localhost:5000/api/people/{person_id}/emails"
                email_payload = {
                    "email_address": email,
                    "location": "Home"
                }
                try:
                    email_response = requests.post(email_url, json=email_payload, timeout=30)
                    if email_response.status_code == 200:
                        result["email_added"] = True
                    else:
                        result["email_error"] = f"Failed to add email: {email_response.text}"
                except Exception as e:
                    result["email_error"] = f"Failed to add email: {str(e)}"
        else:
            result["success"] = False
            if not result.get("error"):
                result["error"] = "Unknown error - no person ID returned"
        
        return result
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to PCO API at http://localhost:5000"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def interactive_add_person():
    """Interactive wizard to add a new person"""
    print("\n" + "=" * 70)
    print("👤 Add New Person to PCO")
    print("=" * 70)
    print("Please provide the following information:")
    print("-" * 70 + "\n")
    
    # Get required fields
    first_name = input("First Name (required): ").strip()
    if not first_name:
        print("❌ First name is required!")
        return
    
    last_name = input("Last Name (required): ").strip()
    if not last_name:
        print("❌ Last name is required!")
        return
    
    # Get optional fields
    gender = input("Gender (Male/Female/optional): ").strip() or None
    birthdate = input("Birthdate (YYYY-MM-DD/optional): ").strip() or None
    email = input("Email (optional): ").strip() or None
    
    # Confirm
    print("\n" + "-" * 70)
    print("📋 Review Information:")
    print("-" * 70)
    print(f"Name: {first_name} {last_name}")
    if gender:
        print(f"Gender: {gender}")
    if birthdate:
        print(f"Birthdate: {birthdate}")
    if email:
        print(f"Email: {email}")
    print("-" * 70)
    
    confirm = input("\nAdd this person? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Cancelled\n")
        return
    
    # Add person
    print("\n⏳ Adding person to PCO...", end="", flush=True)
    result = add_person(first_name, last_name, gender, birthdate, email)
    print("\r" + " " * 40 + "\r", end="", flush=True)
    
    if result.get("success"):
        print("=" * 70)
        print("✅ Person Added Successfully!")
        print("=" * 70)
        person_data = result.get("data", {})
        person_attrs = person_data.get("attributes", {}) if isinstance(person_data, dict) else {}
        print(f"\nPerson ID: {result.get('id')}")
        print(f"Name: {person_attrs.get('name', f'{first_name} {last_name}')}")
        print(f"Status: {person_attrs.get('status', 'active')}")
        
        if result.get("email_added"):
            print(f"✅ Email: {email} (added successfully)")
        elif result.get("email_error"):
            print(f"⚠️  Email: {result.get('email_error')}")
        elif email:
            print(f"ℹ️  Email: {email} (not added)")
            
        print("\n" + "=" * 70 + "\n")
    else:
        print("=" * 70)
        print("❌ Failed to Add Person")
        print("=" * 70)
        error_msg = result.get('error', 'Unknown error occurred')
        print(f"\nError: {error_msg}\n")
        print("=" * 70 + "\n")

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
    print("  /help       - Show this help message")
    print("  /new        - Start a new session")
    print("  /context    - Show conversation history")
    print("  /clear      - Clear conversation history")
    print("  /addperson  - Add a new person to PCO")
    print("  /quit       - Exit the chat")
    print("  /exit       - Exit the chat")
    print("\n💡 Tips:")
    print("  - Ask questions about your church members and services")
    print("  - The AI remembers your conversation within a session")
    print("  - Use /new to start fresh on a different topic")
    print("  - Use /addperson to quickly add new members")
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
                
                elif command == '/addperson':
                    interactive_add_person()
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