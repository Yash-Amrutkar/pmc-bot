"""
Setup script for PMC Chatbot
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = [
        "data",
        "models",
        "models/chroma_db",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file from template"""
    print("Setting up environment file...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        return True
    
    if os.path.exists("env_example.txt"):
        # Copy env_example.txt to .env
        shutil.copy("env_example.txt", ".env")
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your OpenAI API key")
        return True
    else:
        print("❌ env_example.txt not found")
        return False

def run_scraper():
    """Run the web scraper"""
    print("Running web scraper...")
    try:
        subprocess.check_call([sys.executable, "src/scraper.py"])
        print("✅ Web scraper completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running scraper: {e}")
        return False

def test_chatbot():
    """Test the chatbot"""
    print("Testing chatbot...")
    try:
        subprocess.check_call([sys.executable, "src/chatbot.py"])
        print("✅ Chatbot test completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error testing chatbot: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up PMC Chatbot...")
    print("=" * 50)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Setup failed at package installation")
        return False
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Create .env file
    if not create_env_file():
        print("❌ Setup failed at environment setup")
        return False
    
    # Step 4: Run scraper (optional)
    run_scraper_choice = input("\nDo you want to run the web scraper now? (y/n): ").lower().strip()
    if run_scraper_choice == 'y':
        if not run_scraper():
            print("⚠️  Scraper failed, but setup can continue")
    
    # Step 5: Test chatbot (optional)
    test_choice = input("\nDo you want to test the chatbot? (y/n): ").lower().strip()
    if test_choice == 'y':
        if not test_chatbot():
            print("⚠️  Chatbot test failed, but setup can continue")
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\nNext steps:")
    print("1. Edit .env file and add your OpenAI API key")
    print("2. Run the web scraper: python src/scraper.py")
    print("3. Start the web app: streamlit run web_app/app.py")
    print("4. Or start the API: python api/app.py")
    
    return True

if __name__ == "__main__":
    main() 
