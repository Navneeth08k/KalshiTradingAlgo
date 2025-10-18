"""
Setup script for the Kalshi Trading Algorithm with Virtual Environment
"""
import os
import subprocess
import sys
import venv
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment"""
    print("🐍 Creating virtual environment...")
    try:
        venv_path = Path("venv")
        if venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        venv.create("venv", with_pip=True)
        print("✅ Virtual environment created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def get_venv_python():
    """Get the path to the virtual environment Python executable"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "python.exe")
    else:  # Unix/Linux/MacOS
        return os.path.join("venv", "bin", "python")

def get_venv_pip():
    """Get the path to the virtual environment pip executable"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "pip.exe")
    else:  # Unix/Linux/MacOS
        return os.path.join("venv", "bin", "pip")

def install_requirements():
    """Install required packages in virtual environment"""
    print("📦 Installing required packages in virtual environment...")
    try:
        pip_path = get_venv_pip()
        subprocess.check_call([pip_path, "install", "-r", "requirements.txt"])
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

def create_activation_scripts():
    """Create activation scripts for easy virtual environment activation"""
    print("📝 Creating activation scripts...")
    
    # Windows batch file
    with open("activate.bat", "w") as f:
        f.write("""@echo off
echo Activating virtual environment...
call venv\\Scripts\\activate.bat
echo Virtual environment activated!
echo.
echo To run the system:
echo   python main.py --mode dashboard
echo   python main.py --mode run
echo   python test_system.py
echo.
""")
    
    # Unix/Linux/MacOS shell script
    with open("activate.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Activating virtual environment..."
source venv/bin/activate
echo "Virtual environment activated!"
echo ""
echo "To run the system:"
echo "  python main.py --mode dashboard"
echo "  python main.py --mode run"
echo "  python test_system.py"
echo ""
""")
    
    # Make shell script executable on Unix systems
    if os.name != 'nt':
        os.chmod("activate.sh", 0o755)
    
    print("✅ Activation scripts created")
    return True

def test_installation():
    """Test if the system can be imported in virtual environment"""
    print("🧪 Testing installation...")
    try:
        python_path = get_venv_python()
        result = subprocess.run([
            python_path, "-c", 
            "from trading_algorithm import TradingAlgorithm; print('Import successful')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Trading algorithm can be imported")
            return True
        else:
            print(f"❌ Import error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Kalshi Trading Algorithm with Virtual Environment")
    print("=" * 60)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("❌ Setup failed at virtual environment creation")
        return False
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        return False
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed at .env file creation")
        return False
    
    # Create activation scripts
    if not create_activation_scripts():
        print("❌ Setup failed at activation script creation")
        return False
    
    # Test installation
    if not test_installation():
        print("❌ Setup failed at installation test")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':
        print("   Windows: activate.bat")
        print("   Or manually: venv\\Scripts\\activate")
    else:
        print("   Unix/Linux/MacOS: source activate.sh")
        print("   Or manually: source venv/bin/activate")
    
    print("\n2. Edit .env file with your API keys")
    print("\n3. Test the system:")
    print("   python test_system.py")
    print("\n4. Run the dashboard:")
    print("   python main.py --mode dashboard")
    print("\n5. Or run automated trading:")
    print("   python main.py --mode run")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
