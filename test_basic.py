#!/usr/bin/env python3
"""
Basic test to verify Project Synapse structure and imports
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_project_structure():
    """Test that all required files and directories exist"""
    
    required_files = [
        "README.md",
        "requirements.txt", 
        "setup.py",
        "synapse/__init__.py",
        "synapse/models.py",
        "synapse/core/__init__.py",
        "synapse/security/__init__.py",
        "synapse/api/__init__.py",
        "synapse/cli/__init__.py",
        "config/default.yaml",
        "examples/basic_usage.py",
        "tests/test_core.py",
        "ARCHITECTURE.md",
        "DEPLOYMENT.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_basic_imports():
    """Test basic imports without heavy dependencies"""
    
    try:
        # Test models import (no external dependencies)
        from synapse.models import (
            UserContext, SiloMetadata, KnowledgeResult, 
            AccessLevel, SiloType, QueryRequest
        )
        print("✅ Models import successfully")
        
        # Test creating basic objects
        user = UserContext(
            user_id="test_user",
            organization_id="test_org", 
            team_ids=["test_team"],
            access_levels=[AccessLevel.INTERNAL]
        )
        
        silo = SiloMetadata(
            silo_id="test_silo",
            name="Test Silo",
            silo_type=SiloType.DOCUMENTATION,
            organization_id="test_org",
            team_id="test_team",
            access_rules={},
            data_classification=AccessLevel.INTERNAL
        )
        
        query = QueryRequest(
            query="test query",
            user_context=user,
            max_results=10,
            privacy_budget=0.1
        )
        
        print("✅ Basic object creation works")
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def test_configuration():
    """Test configuration file loading"""
    
    try:
        import yaml
        
        with open("config/default.yaml", "r") as f:
            config = yaml.safe_load(f)
            
        required_sections = ["synapse", "silos"]
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing config section: {section}")
                return False
                
        print("✅ Configuration file is valid")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    
    print("🚀 Project Synapse - Basic Structure Test")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Basic Imports", test_basic_imports), 
        ("Configuration", test_configuration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! Project structure is correct.")
        print("\n📖 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run full tests: python -m pytest tests/")
        print("   3. Try examples: python examples/basic_usage.py")
        print("   4. Start API server: python -m synapse.api.server")
        return True
    else:
        print("❌ Some tests failed. Please check the project structure.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)