"""
Test script for PMC Chatbot
"""
import os
import sys
import json
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test if all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from utils import setup_logging, get_config, validate_config
        print("✅ Utils module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing utils: {e}")
        return False
    
    try:
        from vector_store import PMCVectorStore
        print("✅ Vector store module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing vector store: {e}")
        return False
    
    try:
        from chatbot import PMCChatbot
        print("✅ Chatbot module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing chatbot: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from utils import get_config, validate_config
        config = get_config()
        
        if validate_config(config):
            print("✅ Configuration is valid")
            print(f"   Model: {config.get('model_name', 'Unknown')}")
            print(f"   Base URL: {config.get('base_url', 'Unknown')}")
            return True
        else:
            print("❌ Configuration is invalid")
            return False
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def test_vector_store():
    """Test vector store functionality"""
    print("\n🔍 Testing vector store...")
    
    try:
        from vector_store import PMCVectorStore
        
        # Initialize vector store
        vector_store = PMCVectorStore()
        print("✅ Vector store initialized")
        
        # Test search functionality
        results = vector_store.search("test query", n_results=1)
        print(f"✅ Search test completed (found {len(results)} results)")
        
        # Get stats
        stats = vector_store.get_collection_stats()
        print(f"✅ Collection stats: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing vector store: {e}")
        return False

def test_chatbot():
    """Test chatbot functionality"""
    print("\n🔍 Testing chatbot...")
    
    try:
        from chatbot import PMCChatbot
        
        # Initialize chatbot
        chatbot = PMCChatbot()
        print("✅ Chatbot initialized")
        
        # Test suggested questions
        suggestions = chatbot.get_suggested_questions()
        print(f"✅ Suggested questions: {len(suggestions)} questions")
        
        # Test system info
        info = chatbot.get_system_info()
        print("✅ System info retrieved")
        
        return True
    except Exception as e:
        print(f"❌ Error testing chatbot: {e}")
        return False

def test_data_files():
    """Test if data files exist"""
    print("\n🔍 Testing data files...")
    
    files_to_check = [
        "data/pmc_scraped_data.json",
        "models/chroma_db"
    ]
    
    all_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"⚠️  {file_path} not found (will be created when needed)")
            all_exist = False
    
    return all_exist

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version too old: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False
    
    # Check if .env exists
    if os.path.exists(".env"):
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found (copy from env_example.txt)")
    
    # Check requirements.txt
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt exists")
    else:
        print("❌ requirements.txt not found")
        return False
    
    return True

def run_demo():
    """Run a quick demo if possible"""
    print("\n🎯 Running demo...")
    
    try:
        from chatbot import PMCChatbot
        
        # Initialize chatbot
        chatbot = PMCChatbot()
        
        # Test questions
        test_questions = [
            "What is the Prime Minister's Office?",
            "What are the main functions of the PMO?"
        ]
        
        for question in test_questions:
            print(f"\n🤔 Question: {question}")
            
            try:
                response = chatbot.get_response(question, use_context=False)
                print(f"🤖 Response: {response['response'][:200]}...")
                print(f"   Context used: {response.get('context_used', False)}")
            except Exception as e:
                print(f"❌ Error getting response: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error running demo: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 PMC Chatbot Test Suite")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Environment", test_environment),
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Data Files", test_data_files),
        ("Vector Store", test_vector_store),
        ("Chatbot", test_chatbot),
        ("Demo", run_demo)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your chatbot is ready to use.")
        print("\nNext steps:")
        print("1. Run: python run_web_app.py")
        print("2. Open: http://localhost:8501")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Run: python setup.py")
        print("2. Check your .env file")
        print("3. Install missing dependencies")

if __name__ == "__main__":
    main() 
