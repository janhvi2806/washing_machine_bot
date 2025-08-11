import google.generativeai as genai
import json
import asyncio
from typing import Dict, Any, Optional
from config import Config

class LLMHandler:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_API_KEY)
        # self.model = genai.GenerativeModel('gemini-pro')
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.system_prompt = """
You are a helpful washing machine support assistant. Your goal is to help users with washing machine problems.

For each user query, you must respond in EXACTLY this JSON format:
{
    "action": "troubleshoot" or "create_ticket" or "clarify",
    "response": "Your helpful response text to the user",
    "ticket_summary": "Brief summary for ticket (only if action is create_ticket)",
    "category": "Hardware" or "Software" or "Maintenance" or "General",
    "priority": 30
}

RULES:
- If you can provide basic troubleshooting steps, use "action": "troubleshoot"
- If the issue requires technical assistance, use "action": "create_ticket" 
- If you need more information, use "action": "clarify"
- Always provide helpful, specific advice in the "response" field
- Use priority: 10=immediate, 20=urgent, 30=high, 40=normal, 50=low

Common issues you can troubleshoot:
- Detergent not dispensing
- Drainage problems  
- Machine not starting
- Excessive noise
- Clothes not getting clean
- Water temperature issues

Create tickets for:
- Complex mechanical failures
- Electrical problems  
- Issues needing technician visit
- Problems basic troubleshooting can't resolve
        """
    
    async def process_query(self, user_message: str, conversation_history: Optional[list] = None) -> Dict[str, Any]:
        """Process user query and determine appropriate response"""
        
        try:
            # Build the full prompt
            context = ""
            if conversation_history:
                # Add recent conversation context
                recent_messages = conversation_history[-4:]  # Last 4 messages for context
                for msg in recent_messages:
                    context += f"{msg['role']}: {msg['content']}\n"
            
            full_prompt = f"""
{self.system_prompt}

{f"Previous conversation context:{context}" if context else ""}

Current user message: {user_message}

Respond with JSON only:"""

            response = self.model.generate_content(full_prompt)            
            try:
                # Clean the response text (remove code block markers if present)
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3].strip()
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3].strip()
                
                parsed_response = json.loads(response_text)
                
                # Validate required fields
                if not all(key in parsed_response for key in ['action', 'response', 'category', 'priority']):
                    raise ValueError("Missing required fields in response")
                
                return parsed_response
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON parsing error: {e}")
                print(f"Raw response: {response.text}")
                # Return fallback response
                return self.get_fallback_response(user_message)
                
        except Exception as e:
            print(f"Error processing with Gemini: {e}")
            return self.get_fallback_response(user_message)
    
    def get_fallback_response(self, user_message: str) -> Dict[str, Any]:
        """Provide fallback response when AI processing fails"""
        
        user_message_lower = user_message.lower()
        
        # Simple keyword-based responses
        if any(keyword in user_message_lower for keyword in ['drain', 'draining', 'water won\'t drain', 'not draining']):
            return {
                "action": "troubleshoot",
                "response": """**Drainage Issue - Try These Steps:**

🔧 **Quick Fixes:**
1. **Check the drain hose** - Ensure it's not kinked or clogged
2. **Clean the drain filter** - Usually located at bottom front of machine
3. **Remove blockages** - Check for lint, coins, or debris
4. **Verify drain height** - Hose shouldn't be higher than 96cm

If these don't work, I can create a support ticket for professional help.""",
                "category": "Hardware",
                "priority": 30
            }
        
        elif any(keyword in user_message_lower for keyword in ['detergent', 'soap', 'dispenser', 'not dispensing']):
            return {
                "action": "troubleshoot",
                "response": """**Detergent Dispensing Issue - Try These Steps:**

🧽 **Quick Fixes:**
1. **Clean the detergent drawer** - Remove and wash thoroughly with warm water
2. **Check water pressure** - Ensure strong water flow to machine
3. **Use correct amount** - Don't overfill compartments
4. **Right detergent type** - Use HE detergent for high-efficiency machines

If problem continues, I can create a support ticket.""",
                "category": "Maintenance", 
                "priority": 30
            }
        
        elif any(keyword in user_message_lower for keyword in ['won\'t start', 'not starting', 'no power', 'dead']):
            return {
                "action": "create_ticket",
                "response": "Power and startup issues often require technical diagnosis. I'll create a support ticket so our technicians can properly assist you with this problem.",
                "ticket_summary": "Washing machine power/startup failure",
                "category": "Hardware",
                "priority": 20
            }
        
        elif any(keyword in user_message_lower for keyword in ['noise', 'loud', 'banging', 'grinding', 'squeaking']):
            return {
                "action": "create_ticket",
                "response": "Unusual noises can indicate mechanical issues that need professional attention. I'll create a support ticket for a technician to diagnose the problem safely.",
                "ticket_summary": "Washing machine making unusual noises",
                "category": "Hardware", 
                "priority": 30
            }
        
        else:
            return {
                "action": "create_ticket",
                "response": "I'll create a support ticket for your washing machine issue so our technical team can provide the best assistance.",
                "ticket_summary": f"Washing machine issue: {user_message[:50]}{'...' if len(user_message) > 50 else ''}",
                "category": "General",
                "priority": 30
            }
