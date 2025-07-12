"""
Simplified chatbot for PMC website (no complex dependencies)
"""
import openai
from typing import List, Dict, Any
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimplePMCChatbot:
    def __init__(self):
        # Get configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.model_name = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
        self.temperature = float(os.getenv('TEMPERATURE', '0.7'))
        self.max_tokens = int(os.getenv('MAX_TOKENS', '1000'))
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Chat history
        self.conversation_history: List[Dict[str, str]] = []
        
        # System prompt with PMC knowledge
        self.system_prompt = """You are an AI assistant for the Prime Minister's Office (PMO) website. Your role is to help users find information about:

1. PMO policies and announcements
2. Government initiatives and programs
3. Prime Minister's speeches and statements
4. Administrative information about the PMO
5. General information about the Indian government

You have knowledge about the Prime Minister's Office including:
- The PMO is the administrative office of the Prime Minister of India
- It provides secretarial assistance to the Prime Minister
- It coordinates between various ministries and departments
- It handles important policy matters and government initiatives
- It manages the Prime Minister's schedule and official communications

Always be helpful, accurate, and professional. If you don't have specific information about something, say so clearly and suggest where they might find more information.

Key guidelines:
- Be respectful and maintain a professional tone
- Provide accurate information based on your knowledge
- If asked about something not in your knowledge, say you don't have that specific information
- Be concise but informative
- Respond in a helpful and friendly manner"""
    
    def get_response(self, user_message: str, use_context: bool = True) -> Dict[str, Any]:
        """Generate a response to user message"""
        try:
            # Add user message to history
            self.conversation_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add conversation history (last 6 messages to avoid token limits)
            recent_history = self.conversation_history[-6:]  # Last 6 messages
            for msg in recent_history:
                if msg['role'] == 'user':
                    messages.append({"role": "user", "content": msg['content']})
                elif msg['role'] == 'assistant':
                    messages.append({"role": "assistant", "content": msg['content']})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            assistant_message = response.choices[0].message.content or ""
            
            # Add assistant response to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_message,
                'timestamp': datetime.now().isoformat()
            })
            
            # Prepare response
            response_data = {
                'response': assistant_message,
                'context_used': False,  # Simplified version doesn't use vector store
                'context_length': 0,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.model_name
            }
            
            print(f"Generated response for: {user_message[:50]}...")
            return response_data
            
        except Exception as e:
            print(f"Error generating response: {e}")
            error_response = {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return error_response
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        print("Conversation history cleared")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'conversation_length': len(self.conversation_history),
            'vector_store_stats': {'total_documents': 0}  # Simplified version
        }
    
    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions for users"""
        return [
            "What is the Prime Minister's Office?",
            "What are the main functions of the PMO?",
            "How can I contact the Prime Minister's Office?",
            "What are the latest announcements from the PMO?",
            "What government initiatives has the PMO announced?",
            "What are the key policies of the current government?",
            "How does the PMO support various ministries?",
            "What is the role of the Prime Minister in the government?"
        ]
    
    def process_feedback(self, feedback: Dict[str, Any]) -> bool:
        """Process user feedback"""
        try:
            # Log feedback for improvement
            feedback_data = {
                'timestamp': datetime.now().isoformat(),
                'user_message': feedback.get('user_message', ''),
                'assistant_response': feedback.get('assistant_response', ''),
                'rating': feedback.get('rating', 0),
                'comments': feedback.get('comments', ''),
                'helpful': feedback.get('helpful', False)
            }
            
            # Save feedback to file
            os.makedirs('data', exist_ok=True)
            with open('data/feedback.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_data, ensure_ascii=False) + '\n')
            
            print(f"Feedback received: rating={feedback.get('rating', 0)}")
            return True
            
        except Exception as e:
            print(f"Error processing feedback: {e}")
            return False

def main():
    """Test the simplified chatbot"""
    try:
        chatbot = SimplePMCChatbot()
        
        # Test conversation
        test_questions = [
            "What is the Prime Minister's Office?",
            "What are the main functions of the PMO?",
            "How can I contact the PMO?"
        ]
        
        for question in test_questions:
            print(f"\nUser: {question}")
            response = chatbot.get_response(question)
            print(f"Assistant: {response['response']}")
            print(f"Context used: {response['context_used']}")
        
        # Print system info
        info = chatbot.get_system_info()
        print(f"\nSystem Info: {info}")
        
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main() 
