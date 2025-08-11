from zeep import Client
from zeep.transports import Transport
from requests import Session
import base64
from typing import Optional, Dict, Any
from config import Config

class MantisHubClient:
    def __init__(self):
        self.soap_url = Config.MANTIS_BASE_URL
        self.username = Config.MANTIS_USERNAME
        self.password = Config.MANTIS_PASSWORD
        self.project_id = Config.MANTIS_PROJECT_ID
        self.api_token = Config.MANTIS_API_TOKEN
        
        # Create SOAP client
        session = Session()
        transport = Transport(session=session)
        self.client = Client(self.soap_url, transport=transport)
        
    def create_ticket(self, summary: str, description: str, reporter_name: str, 
                    category: str = "General", priority: int = 30) -> Optional[str]:
        """Create a new ticket using SOAP API"""
        
        try:
            # SOAP requires different priority mapping
            priority_map = {10: 60, 20: 50, 30: 40, 40: 30, 50: 20}
            soap_priority = priority_map.get(priority, 40)
            
            # Try different default categories if the provided one fails
            categories_to_try = [category, "General", "Bug", "Support", "Issue", "Default"]
            
            for cat_name in categories_to_try:
                try:
                    # Create issue data structure with category
                    issue_data = {
                        'summary': summary,
                        'description': description,
                        'project': {'id': int(self.project_id)},
                        'category': cat_name,
                        'priority': {'id': soap_priority},
                        'severity': {'id': 50},
                        'status': {'id': 10},
                        'reproducibility': {'id': 10},
                        'view_state': {'id': 10}
                    }
                    
                    response = self.client.service.mc_issue_add(
                        username=self.username,
                        password=self.password,
                        issue=issue_data
                    )
                    
                    if response:
                        print(f"✅ SOAP ticket created successfully: #{response} (category: {cat_name})")
                        return str(response)
                        
                except Exception as category_error:
                    print(f"⚠️ Category '{cat_name}' failed: {category_error}")
                    continue
            
            print("❌ All category attempts failed")
            return None
            
        except Exception as e:
            print(f"❌ SOAP Error creating ticket: {e}")
            return None

    def get_ticket_status(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get ticket status using SOAP API"""
        try:
            response = self.client.service.mc_issue_get(
                username=self.username,
                password=self.password,
                issue_id=int(ticket_id)
            )
            
            if response:
                return {
                    'id': response.id,
                    'summary': response.summary,
                    'status': response.status.name if hasattr(response, 'status') else 'Unknown',
                    'priority': response.priority.name if hasattr(response, 'priority') else 'Unknown'
                }
            return None
            
        except Exception as e:
            print(f"Error fetching SOAP ticket: {e}")
            return None
    
    def add_note_to_ticket(self, ticket_id: str, note: str) -> bool:
        """Add a note to existing ticket via SOAP"""
        try:
            note_data = {
                'text': note
            }
            
            response = self.client.service.mc_issue_note_add(
                username=self.username,
                password=self.password,
                issue_id=int(ticket_id),
                note=note_data
            )
            
            return bool(response)
            
        except Exception as e:
            print(f"Error adding SOAP note: {e}")
            return False
    
    def list_projects(self) -> Optional[list]:
        """List available projects (for testing)"""
        try:
            response = self.client.service.mc_projects_get_user_accessible(
                username=self.username,
                password=self.password
            )
            return response
        except Exception as e:
            print(f"Error listing projects: {e}")
            return None
