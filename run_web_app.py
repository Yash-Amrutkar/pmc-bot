"""
Script to run the PMC Chatbot web application
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit web application"""
    print("🚀 Starting PMC Chatbot Web Application...")
    print("=" * 50)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please run setup.py first or create .env file manually.")
        print("You can copy env_example.txt to .env and add your OpenAI API key.")
        return
    
    # Run the web application
    print("🌐 Starting web application...")
    print("The application will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_app/app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main() 
