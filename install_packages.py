"""
Simplified package installation script for PMC Chatbot
"""
import subprocess
import sys
import os

def install_package(package_name):
    """Install a single package"""
    try:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing {package_name}: {e}")
        return False

def main():
    """Install packages step by step"""
    print("🚀 Installing PMC Chatbot Dependencies")
    print("=" * 50)
    
    # Core packages (should work with Python 3.13)
    core_packages = [
        "flask",
        "requests", 
        "beautifulsoup4",
        "python-dotenv",
        "flask-cors"
    ]
    
    # AI/ML packages (may need specific versions)
    ai_packages = [
        "openai",
        "numpy",
        "pandas",
        "streamlit"
    ]
    
    # Optional packages (may fail but won't break the app)
    optional_packages = [
        "chromadb",
        "sentence-transformers",
        "langchain",
        "langchain-openai",
        "tiktoken",
        "faiss-cpu"
    ]
    
    print("Installing core packages...")
    for package in core_packages:
        install_package(package)
    
    print("\nInstalling AI/ML packages...")
    for package in ai_packages:
        install_package(package)
    
    print("\nInstalling optional packages...")
    for package in optional_packages:
        try:
            install_package(package)
        except:
            print(f"⚠️  {package} failed to install - will use fallback")
    
    print("\n" + "=" * 50)
    print("✅ Package installation completed!")
    print("\nNext steps:")
    print("1. Copy env_example.txt to .env")
    print("2. Add your OpenAI API key to .env")
    print("3. Run: python run_web_app.py")

if __name__ == "__main__":
    main() 
