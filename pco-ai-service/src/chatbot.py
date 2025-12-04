"""
Chatbot Interface
Provides conversational AI interface for PCO data with context management
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from ollama_client import get_ollama_client
from query_processor import QueryProcessor


class ConversationContext:
    """Manages conversation context and history"""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize conversation context.
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.messages: List[Dict[str, str]] = []
        self.max_history = max_history
        self.metadata: Dict[str, Any] = {
            'created_at': datetime.utcnow().isoformat(),
            'last_updated': datetime.utcnow().isoformat()
        }
        
    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history.
        
        Args:
            role: Message role ('system', 'user', or 'assistant')
            content: Message content
        """
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Keep only recent messages
        if len(self.messages) > self.max_history:
            # Always keep system message if it exists
            system_messages = [m for m in self.messages if m['role'] == 'system']
            other_messages = [m for m in self.messages if m['role'] != 'system']
            
            # Keep most recent messages
            self.messages = system_messages + other_messages[-(self.max_history - len(system_messages)):]
        
        self.metadata['last_updated'] = datetime.utcnow().isoformat()
    
    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """
        Get messages formatted for Ollama API.
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        return [{'role': m['role'], 'content': m['content']} for m in self.messages]
    
    def clear(self):
        """Clear conversation history"""
        self.messages = []
        self.metadata['last_updated'] = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            'messages': self.messages,
            'metadata': self.metadata,
            'message_count': len(self.messages)
        }


class PCOChatbot:
    """Chatbot for interacting with PCO data"""
    
    def __init__(self, pco_api_url: str):
        """
        Initialize chatbot.
        
        Args:
            pco_api_url: Base URL for PCO API wrapper service
        """
        self.ollama = get_ollama_client()
        self.query_processor = QueryProcessor(pco_api_url)
        self.contexts: Dict[str, ConversationContext] = {}
        
        # System prompt for the chatbot
        self.system_prompt = """You are a helpful AI assistant for Planning Center Online (PCO) church management.

Your capabilities:
1. Answer questions about church members (people data)
2. Provide information about church services and events
3. Analyze data and provide insights
4. Help with data queries and filtering

When users ask questions:
- Be friendly and conversational
- Provide accurate information based on the data
- If you need to fetch data, explain what you're doing
- If data is not available, suggest alternatives
- Remember context from previous messages in the conversation

Available data types:
- People: church members with details like name, gender, birthdate, membership, status, campus
- Services: upcoming services with dates and service types
- Campuses: church campus information

You can help with queries like:
- "How many members do we have?"
- "Show me all members from the youth group"
- "What services are coming up?"
- "Analyze our membership demographics"
- "Who joined in the last month?"
"""
    
    def get_or_create_context(self, session_id: str) -> ConversationContext:
        """
        Get existing conversation context or create new one.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            ConversationContext instance
        """
        if session_id not in self.contexts:
            context = ConversationContext()
            context.add_message('system', self.system_prompt)
            self.contexts[session_id] = context
        return self.contexts[session_id]
    
    def chat(self, 
             message: str, 
             session_id: str = 'default',
             fetch_data: bool = True) -> Dict[str, Any]:
        """
        Process a chat message.
        
        Args:
            message: User message
            session_id: Session identifier for context management
            fetch_data: Whether to fetch PCO data for context
            
        Returns:
            Dict with response and metadata
        """
        context = self.get_or_create_context(session_id)
        
        try:
            # Determine if we need to fetch data based on the message
            needs_people_data = any(keyword in message.lower() for keyword in 
                                   ['member', 'people', 'person', 'who', 'how many'])
            needs_services_data = any(keyword in message.lower() for keyword in 
                                     ['service', 'event', 'upcoming', 'schedule'])
            
            # Fetch relevant data if needed
            additional_context = ""
            if fetch_data and needs_people_data:
                try:
                    pco_response = self.query_processor.fetch_pco_data('/api/people', {'format': 'text'})
                    if pco_response.get('context'):
                        additional_context += f"\n\nCurrent People Data:\n{pco_response['context'][:2000]}"  # Limit context size
                except:
                    pass
            
            if fetch_data and needs_services_data:
                try:
                    services_response = self.query_processor.fetch_pco_data('/api/services/upcoming')
                    services_data = services_response.get('data', [])
                    if services_data:
                        services_summary = "\n".join([
                            f"- {s.get('service_type_name', 'N/A')} on {s.get('sort_date', 'N/A')}"
                            for s in services_data[:10]
                        ])
                        additional_context += f"\n\nUpcoming Services:\n{services_summary}"
                except:
                    pass
            
            # Add user message with additional context if available
            user_message = message
            if additional_context:
                user_message += additional_context
            
            context.add_message('user', user_message)
            
            # Get AI response
            messages = context.get_messages_for_api()
            response = self.ollama.chat(
                messages=messages,
                temperature=0.7
            )
            
            # Add assistant response to context
            context.add_message('assistant', response)
            
            return {
                'success': True,
                'session_id': session_id,
                'message': message,
                'response': response,
                'context_size': len(context.messages),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'session_id': session_id,
                'message': message,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation context for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Context dictionary or None if not found
        """
        if session_id in self.contexts:
            return self.contexts[session_id].to_dict()
        return None
    
    def clear_context(self, session_id: str) -> bool:
        """
        Clear conversation context for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleared, False if session not found
        """
        if session_id in self.contexts:
            self.contexts[session_id].clear()
            # Re-add system prompt
            self.contexts[session_id].add_message('system', self.system_prompt)
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a conversation session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if session not found
        """
        if session_id in self.contexts:
            del self.contexts[session_id]
            return True
        return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active sessions.
        
        Returns:
            List of session info dicts
        """
        return [
            {
                'session_id': session_id,
                'message_count': len(context.messages),
                'created_at': context.metadata['created_at'],
                'last_updated': context.metadata['last_updated']
            }
            for session_id, context in self.contexts.items()
        ]