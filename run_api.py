"""
Script to run the PMC Chatbot API server
"""
import subprocess
import sys
import os

def main():
    """Run the Flask API server"""
    print("🚀 Starting PMC Chatbot API Server...")
    print("=" * 50)
    
    # Check if flask is installed
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please run setup.py first or create .env file manually.")
        print("You can copy env_example.txt to .env and add your OpenAI API key.")
        return
    
    # Run the API server
    print("🌐 Starting API server...")
    print("The API will be available at http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "api/app.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 API server stopped by user")
    except Exception as e:
        print(f"❌ Error running API server: {e}")

if __name__ == "__main__":
    main() 
