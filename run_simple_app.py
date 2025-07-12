"""
Script to run the simplified PMC Chatbot web application
"""
import subprocess
import sys
import os

def main():
    """Run the simplified Streamlit web application"""
    print("🚀 Starting Simplified PMC Chatbot Web Application...")
    print("=" * 60)
    
    # Check if streamlit is installed
    try:
        import streamlit
        print("✅ Streamlit is installed")
    except ImportError:
        print("❌ Streamlit not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Creating from template...")
        if os.path.exists("env_example.txt"):
            import shutil
            shutil.copy("env_example.txt", ".env")
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file and add your OpenAI API key")
        else:
            print("❌ env_example.txt not found")
            return
    
    # Run the simplified web application
    print("🌐 Starting simplified web application...")
    print("The application will open in your browser at http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_app/simple_app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main() 
