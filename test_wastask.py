#!/usr/bin/env python3
"""
Simple test script for WasTask functionality
"""
import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    from wastask.agents.coordinator.agent import coordinator
    from wastask.core.models import Project, Task
    print("✅ WasTask modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_coordinator():
    """Test the coordinator agent"""
    print("\n🤖 Testing Coordinator Agent...")
    
    try:
        response = await coordinator.process_message(
            user_id="test_user",
            message="Hello WasTask! Can you help me create a new project?"
        )
        
        print(f"✅ Response: {response.response}")
        print(f"   Agent: {response.agent_type}")
        if response.suggestions:
            print(f"   Suggestions: {response.suggestions}")
        
    except Exception as e:
        print(f"❌ Coordinator test failed: {e}")


def test_models():
    """Test Pydantic models"""
    print("\n📊 Testing Data Models...")
    
    try:
        # Test Project model
        project = Project(
            name="Test Project",
            description="A test project for WasTask",
            owner_id="550e8400-e29b-41d4-a716-446655440000"
        )
        print(f"✅ Project model: {project.name}")
        
        # Test Task model
        task = Task(
            title="Test Task",
            description="A test task",
            project_id="550e8400-e29b-41d4-a716-446655440000",
            creator_id="550e8400-e29b-41d4-a716-446655440001"
        )
        print(f"✅ Task model: {task.title}")
        
    except Exception as e:
        print(f"❌ Models test failed: {e}")


async def test_project_planning():
    """Test project planning functionality"""
    print("\n📋 Testing Project Planning...")
    
    try:
        from wastask.agents.planning.agent import planning_agent
        
        result = await planning_agent.create_project_plan(
            project_description="Build a simple web application with user authentication",
            constraints={"max_duration_days": 30},
            preferences={"methodology": "agile", "team_size": 2}
        )
        
        if result['status'] == 'success':
            plan = result['plan']
            print(f"✅ Project plan created: {plan['project_summary']['title']}")
            print(f"   Phases: {len(plan['phases'])}")
            print(f"   Duration: {plan['timeline']['total_duration_days']} days")
        else:
            print(f"⚠️  Planning returned: {result['message']}")
            
    except Exception as e:
        print(f"❌ Planning test failed: {e}")


def show_cli_commands():
    """Show available CLI-like commands"""
    print("\n💻 Available Commands (simulated):")
    print("   wastask project create --name 'My Project'")
    print("   wastask project list")
    print("   wastask task create --project proj_001 --title 'My Task'")
    print("   wastask chat 'Hello WasTask!'")
    print("   wastask analyze --project proj_001")


async def main():
    """Main test function"""
    print("🚀 WasTask Functionality Test")
    print("=" * 40)
    
    # Test models
    test_models()
    
    # Test coordinator
    await test_coordinator()
    
    # Test planning
    await test_project_planning()
    
    # Show commands
    show_cli_commands()
    
    print("\n🎉 WasTask tests completed!")
    print("\nNext steps:")
    print("1. Edit .env with your API keys")
    print("2. Try: uv run python test_wastask.py")
    print("3. Explore the code in wastask/ directory")


if __name__ == '__main__':
    asyncio.run(main())