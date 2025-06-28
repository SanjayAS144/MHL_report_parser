"""Quick start script for Food Tech Analytics Data Parser."""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up basic environment for testing."""
    print("Setting up environment...")
    
    # Create .env file from template
    env_file = Path(".env")
    template_file = Path("env_template.txt")
    
    if not env_file.exists() and template_file.exists():
        # Copy template to .env with some default values
        with open(template_file, 'r') as f:
            content = f.read()
        
        # Replace some placeholders with test values
        content = content.replace('your_username', 'postgres')
        content = content.replace('your_password', 'postgres')
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ Created .env file from template")
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    print("✓ Created logs directory")


def run_basic_tests():
    """Run basic tests to verify setup."""
    print("\nRunning basic tests...")
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    try:
        # Import test module
        from tests.test_basic import (
            test_imports, test_config_models, 
            test_container, test_parser_factory
        )
        
        # Set test environment
        os.environ['DB_PASSWORD'] = 'test_password'
        
        # Run tests
        test_imports()
        test_config_models()
        test_container()
        test_parser_factory()
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_usage_examples():
    """Show usage examples."""
    print("\n" + "="*60)
    print("USAGE EXAMPLES")
    print("="*60)
    
    print("\n1. List all configured partners:")
    print("   python main.py list-partners")
    
    print("\n2. Validate a partner configuration:")
    print("   python main.py validate-config --partner-id zomato")
    
    print("\n3. Create database tables:")
    print("   python main.py create-tables")
    
    print("\n4. Parse data for a specific partner (dry run):")
    print("   python main.py parse-partner --partner-id zomato --dry-run")
    
    print("\n5. Parse all partners (dry run):")
    print("   python main.py parse-all --dry-run")
    
    print("\n6. Parse specific partner with actual database insertion:")
    print("   python main.py parse-partner --partner-id zomato")
    
    print("\n" + "="*60)
    print("CONFIGURATION")
    print("="*60)
    
    print("\n1. Edit .env file with your database credentials")
    print("2. Create partner configurations in configs/partners/")
    print("3. Place your data files in the structure matching your Data_Sources path")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    
    print("\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n2. Set up your PostgreSQL database")
    
    print("\n3. Update .env file with your database credentials")
    
    print("\n4. Create database tables:")
    print("   python main.py create-tables")
    
    print("\n5. Test with sample configurations:")
    print("   python main.py validate-config --partner-id zomato")
    
    print("\n6. Run dry-run to test parsing:")
    print("   python main.py parse-all --dry-run")


def main():
    """Main quick start function."""
    print("Food Tech Analytics Data Parser - Quick Start")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    tests_passed = run_basic_tests()
    
    if tests_passed:
        print("\n✅ Project setup is working correctly!")
        show_usage_examples()
    else:
        print("\n❌ There are issues with the project setup.")
        print("Please check the error messages above and ensure all dependencies are installed.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 