#!/usr/bin/env python3
"""
Test script to verify the bot setup and dependencies
"""
import sys
import os
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    required_modules = [
        'aiogram',
        'asyncpg', 
        'sqlalchemy',
        'alembic',
        'cv2',
        'PIL',
        'numpy',
        'redis',
        'aiofiles',
        'psutil',
        'dotenv'
    ]
    
    optional_modules = [
        'caffe'  # This might not be available in development
    ]
    
    print("Testing required modules...")
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    print("\nTesting optional modules...")
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"⚠️  {module}: Not available (this is OK for development)")
    
    return failed_imports

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        from config import BOT_TOKEN, DATABASE_URL, REDIS_URL
        print("✅ Configuration loaded successfully")
        
        if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            print("⚠️  BOT_TOKEN not set (use environment variable or .env file)")
        else:
            print("✅ BOT_TOKEN is configured")
            
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_model_files():
    """Test if model files exist"""
    print("\nTesting model files...")
    model_files = [
        'models/colorization_release_v2.caffemodel',
        'models/colorization_deploy_v2.prototxt',
        'models/pts_in_hull.npy'
    ]
    
    missing_files = []
    for file_path in model_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}: Not found")
            missing_files.append(file_path)
    
    return missing_files

def main():
    """Run all tests"""
    print("🤖 Telegram Colorization Bot - Setup Test")
    print("=" * 50)
    
    # Test imports
    failed_imports = test_imports()
    
    # Test configuration
    config_ok = test_config()
    
    # Test model files
    missing_files = test_model_files()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    
    if not failed_imports:
        print("✅ All required modules are available")
    else:
        print(f"❌ Missing modules: {', '.join(failed_imports)}")
        print("   Install with: pip install -r requirements.txt")
    
    if config_ok:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration issues detected")
    
    if not missing_files:
        print("✅ All model files are present")
    else:
        print(f"⚠️  Missing model files: {', '.join(missing_files)}")
        print("   Download the model files to the models/ directory")
    
    if not failed_imports and config_ok:
        print("\n🎉 Setup looks good! You can run the bot with: python bot.py")
    else:
        print("\n⚠️  Please fix the issues above before running the bot")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

