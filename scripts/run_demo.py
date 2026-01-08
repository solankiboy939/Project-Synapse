#!/usr/bin/env python3
"""
Demo script for Project Synapse
Runs various demonstrations to showcase capabilities
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from examples.basic_usage import main as basic_demo
from examples.enterprise_demo import run_enterprise_demo


async def run_all_demos():
    """Run all available demonstrations"""
    
    print("🚀 Project Synapse - Complete Demonstration Suite")
    print("=" * 60)
    
    demos = [
        ("Basic Usage", basic_demo),
        ("Enterprise Scale", run_enterprise_demo),
    ]
    
    for demo_name, demo_func in demos:
        print(f"\n🎯 Running {demo_name} Demo...")
        print("-" * 40)
        
        try:
            await demo_func()
            print(f"✅ {demo_name} Demo completed successfully!")
            
        except Exception as e:
            print(f"❌ {demo_name} Demo failed: {e}")
            
        print("\n" + "=" * 60)
        
        # Pause between demos
        if demo_name != demos[-1][0]:
            input("Press Enter to continue to next demo...")
    
    print("\n🎉 All demonstrations completed!")
    print("📖 Check the examples/ directory for more detailed code")


def main():
    """Main demo runner"""
    
    parser = argparse.ArgumentParser(description="Project Synapse Demo Runner")
    parser.add_argument(
        "--demo", 
        choices=["basic", "enterprise", "all"],
        default="all",
        help="Which demo to run"
    )
    
    args = parser.parse_args()
    
    if args.demo == "basic":
        asyncio.run(basic_demo())
    elif args.demo == "enterprise":
        asyncio.run(run_enterprise_demo())
    else:
        asyncio.run(run_all_demos())


if __name__ == "__main__":
    main()