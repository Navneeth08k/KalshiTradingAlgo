"""
Setup script for the Kalshi Trading Algorithm
"""
import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file from template"""
    print("🔧 Setting up environment file...")
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists("env_example.txt"):
        try:
            with open("env_example.txt", "r") as f:
                content = f.read()
            
            with open(".env", "w") as f:
                f.write(content)
            
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual API keys")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("❌ env_example.txt not found")
        return False

def test_installation():
    """Test if the system can be imported"""
    print("🧪 Testing installation...")
    try:
        from trading_algorithm import TradingAlgorithm
        print("✅ Trading algorithm can be imported")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Kalshi Trading Algorithm")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        return False
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed at .env file creation")
        return False
    
    # Test installation
    if not test_installation():
        print("❌ Setup failed at installation test")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your API keys")
    print("2. Run: python test_system.py")
    print("3. Run: python main.py --mode dashboard")
    print("4. Or run: python main.py --mode run")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
