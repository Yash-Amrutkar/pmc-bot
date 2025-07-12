"""
Main chatbot logic for PMC website
"""
import openai
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
from utils import setup_logging, get_config, validate_config
from vector_store import PMCVectorStore

logger = setup_logging()

class PMCChatbot:
    def __init__(self):
        self.config = get_config()
        if not validate_config(self.config):
            raise ValueError("Invalid configuration")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.config['openai_api_key'])
        
        # Initialize vector store
        self.vector_store = PMCVectorStore()
        
        # Chat history
        self.conversation_history: List[Dict[str, str]] = []
        
        # System prompt
        self.system_prompt = """You are an AI assistant for the Prime Minister's Office (PMO) website. Your role is to help users find information about:

1. PMO policies and announcements
2. Government initiatives and programs
3. Prime Minister's speeches and statements
4. Administrative information about the PMO
5. General information about the Indian government

Always be helpful, accurate, and professional. If you don't have information about something, say so clearly. Base your responses on the provided context from the PMO website.

Key guidelines:
- Be respectful and maintain a professional tone
- Provide accurate information based on the context
- If asked about something not in the context, say you don't have that information
- Always cite sources when possible
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
            
            # Get relevant context if enabled
            context = ""
            if use_context:
                context = self.vector_store.get_relevant_context(user_message)
            
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add context if available
            if context:
                context_message = f"""Use the following information from the PMO website to answer the user's question:

{context}

Please provide a helpful response based on this information. If the information doesn't answer the question completely, say so."""
                messages.append({"role": "system", "content": context_message})
            
            # Add conversation history (last 5 messages to avoid token limits)
            recent_history = self.conversation_history[-10:]  # Last 10 messages
            for msg in recent_history:
                if msg['role'] == 'user':
                    messages.append({"role": "user", "content": msg['content']})
                elif msg['role'] == 'assistant':
                    messages.append({"role": "assistant", "content": msg['content']})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.config['model_name'],
                messages=messages,
                temperature=self.config['temperature'],
                max_tokens=self.config['max_tokens']
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_message or "",
                'timestamp': datetime.now().isoformat()
            })
            
            # Prepare response
            response_data = {
                'response': assistant_message,
                'context_used': bool(context),
                'context_length': len(context),
                'timestamp': datetime.now().isoformat(),
                'model_used': self.config['model_name']
            }
            
            logger.info(f"Generated response for: {user_message[:50]}...")
            return response_data
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            error_response = {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again later.",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return error_response
    
    def search_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents"""
        try:
            results = self.vector_store.search(query, n_results)
            return results
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        try:
            stats = self.vector_store.get_collection_stats()
            return {
                'model_name': self.config['model_name'],
                'temperature': self.config['temperature'],
                'max_tokens': self.config['max_tokens'],
                'vector_store_stats': stats,
                'conversation_length': len(self.conversation_history)
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def initialize_data(self) -> bool:
        """Initialize the chatbot with data"""
        try:
            logger.info("Initializing chatbot data...")
            success = self.vector_store.load_and_index_data()
            
            if success:
                logger.info("Chatbot initialized successfully")
            else:
                logger.warning("Chatbot initialized with limited data")
            
            return success
            
        except Exception as e:
            logger.error(f"Error initializing chatbot: {e}")
            return False
    
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
            with open('data/feedback.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(feedback_data, ensure_ascii=False) + '\n')
            
            logger.info(f"Feedback received: rating={feedback.get('rating', 0)}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing feedback: {e}")
            return False

def main():
    """Test the chatbot"""
    try:
        chatbot = PMCChatbot()
        
        # Initialize data
        chatbot.initialize_data()
        
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
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main() 
