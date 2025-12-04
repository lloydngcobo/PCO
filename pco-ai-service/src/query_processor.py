"""
Natural Language Query Processor
Processes natural language queries about PCO data using AI
"""

import os
import requests
from typing import Dict, Any, Optional, List
from ollama_client import get_ollama_client


class QueryProcessor:
    """Processes natural language queries about PCO data"""
    
    def __init__(self, pco_api_url: str):
        """
        Initialize query processor.
        
        Args:
            pco_api_url: Base URL for PCO API wrapper service
        """
        self.pco_api_url = pco_api_url.rstrip('/')
        self.ollama = get_ollama_client()
        # Disable SSL verification for self-signed certificates (development only)
        self.verify_ssl = os.getenv("VERIFY_SSL", "true").lower() == "true"
        
    def fetch_pco_data(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fetch data from PCO API wrapper.
        
        Args:
            endpoint: API endpoint (e.g., '/api/people')
            params: Optional query parameters
            
        Returns:
            API response data
        """
        url = f"{self.pco_api_url}{endpoint}"
        try:
            # Increased timeout for large datasets (5 minutes)
            response = requests.get(url, params=params, timeout=300, verify=self.verify_ssl)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout fetching PCO data from {url}. The request took longer than 5 minutes. Try using filters to reduce the dataset size.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching PCO data: {str(e)}")
    
    def generate_context_from_people(self, people_data: List[Dict[str, Any]]) -> str:
        """
        Generate context string from people data.
        
        Args:
            people_data: List of people dictionaries
            
        Returns:
            Formatted context string
        """
        if not people_data:
            return "No people data available."
        
        context_lines = []
        for person in people_data:
            line = (
                f"{person.get('first_name', 'N/A')} {person.get('last_name', 'N/A')}, "
                f"Gender: {person.get('gender', 'N/A')}, "
                f"Birthdate: {person.get('birthdate', 'N/A')}, "
                f"Membership: {person.get('membership', 'Unknown')}, "
                f"Status: {person.get('status', 'N/A')}, "
                f"Campus: {person.get('campuses', 'N/A')}"
            )
            context_lines.append(line)
        
        return "\n".join(context_lines)
    
    def process_people_query(self, 
                            query: str,
                            role: Optional[str] = None,
                            status: Optional[str] = None,
                            campus_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a natural language query about people.
        
        Args:
            query: Natural language query
            role: Optional role filter
            status: Optional status filter
            campus_id: Optional campus filter
            
        Returns:
            Dict with query results and AI response
        """
        # Fetch people data with filters
        params = {}
        if role:
            params['role'] = role
        if status:
            params['status'] = status
        if campus_id:
            params['campus_id'] = campus_id
        
        try:
            pco_response = self.fetch_pco_data('/api/people', params)
            people_data = pco_response.get('data', [])
            count = pco_response.get('count', 0)
            
            # Generate context
            context = self.generate_context_from_people(people_data)
            
            # Create prompt for AI
            system_prompt = """You are a helpful assistant that manages church member information from Planning Center Online.
You provide accurate, detailed responses based on the data provided.
When answering questions about people, include relevant details like names, gender, birthdate, membership status, and campus.
If the data doesn't contain the answer, say so clearly."""
            
            user_prompt = f"""Here is the church member data:

{context}

Total members: {count}
Filters applied: Role={role or 'None'}, Status={status or 'None'}, Campus={campus_id or 'None'}

User Question: {query}

Please provide a detailed and accurate response based on the given data."""
            
            # Get AI response
            ai_response = self.ollama.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3  # Lower temperature for more factual responses
            )
            
            return {
                'success': True,
                'query': query,
                'filters': {
                    'role': role,
                    'status': status,
                    'campus_id': campus_id
                },
                'data_count': count,
                'ai_response': ai_response,
                'raw_data': people_data if count <= 50 else None  # Include raw data only for small datasets
            }
            
        except Exception as e:
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }
    
    def process_services_query(self, query: str) -> Dict[str, Any]:
        """
        Process a natural language query about services.
        
        Args:
            query: Natural language query
            
        Returns:
            Dict with query results and AI response
        """
        try:
            # Fetch services data
            services_response = self.fetch_pco_data('/api/services/upcoming')
            services_data = services_response.get('data', [])
            
            # Generate context
            context_lines = []
            for service in services_data:
                line = (
                    f"Service: {service.get('service_type_name', 'N/A')}, "
                    f"Date: {service.get('sort_date', 'N/A')}, "
                    f"Plans: {service.get('plan_count', 0)}"
                )
                context_lines.append(line)
            
            context = "\n".join(context_lines) if context_lines else "No services data available."
            
            # Create prompt for AI
            system_prompt = """You are a helpful assistant that manages church service information from Planning Center Online.
You provide accurate, detailed responses about upcoming services, service types, and plans."""
            
            user_prompt = f"""Here is the church services data:

{context}

User Question: {query}

Please provide a detailed and accurate response based on the given data."""
            
            # Get AI response
            ai_response = self.ollama.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            return {
                'success': True,
                'query': query,
                'data_count': len(services_data),
                'ai_response': ai_response,
                'raw_data': services_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'query': query,
                'error': str(e)
            }
    
    def analyze_data(self, data_type: str = 'people') -> Dict[str, Any]:
        """
        Perform AI-powered analysis on PCO data.
        
        Args:
            data_type: Type of data to analyze ('people' or 'services')
            
        Returns:
            Dict with analysis results
        """
        try:
            if data_type == 'people':
                # Fetch all people data
                pco_response = self.fetch_pco_data('/api/people')
                people_data = pco_response.get('data', [])
                context = self.generate_context_from_people(people_data)
                
                analysis_prompt = f"""Analyze the following church member data and provide insights:

{context}

Please provide:
1. Demographics summary (gender distribution, age groups if birthdate available)
2. Membership status breakdown
3. Campus distribution
4. Any notable patterns or trends
5. Recommendations for engagement or follow-up

Be specific and use actual numbers from the data."""
                
            else:  # services
                services_response = self.fetch_pco_data('/api/services/upcoming')
                services_data = services_response.get('data', [])
                
                context_lines = []
                for service in services_data:
                    line = f"{service.get('service_type_name', 'N/A')} on {service.get('sort_date', 'N/A')}"
                    context_lines.append(line)
                
                context = "\n".join(context_lines)
                
                analysis_prompt = f"""Analyze the following church services data and provide insights:

{context}

Please provide:
1. Service frequency and patterns
2. Service type distribution
3. Planning status overview
4. Any scheduling gaps or concerns
5. Recommendations for service planning

Be specific and use actual data."""
            
            system_prompt = "You are a data analyst specializing in church management and Planning Center Online data."
            
            # Get AI analysis
            analysis = self.ollama.generate(
                prompt=analysis_prompt,
                system_prompt=system_prompt,
                temperature=0.5
            )
            
            return {
                'success': True,
                'data_type': data_type,
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'success': False,
                'data_type': data_type,
                'error': str(e)
            }