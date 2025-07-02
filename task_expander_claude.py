#!/usr/bin/env python3
"""
Task Expander - Claude Direct Integration
Uses Claude directly through the current session
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from database_manager import WasTaskDatabase, connect_and_run

class TaskExpanderClaude:
    def __init__(self):
        self.model = "claude-direct"  # Using Claude directly
        
    def should_expand_task(self, task: Dict[str, Any]) -> bool:
        """Determine if a task should be expanded based on complexity indicators"""
        
        # Don't expand already expanded tasks
        if task.get('is_expanded', False):
            return False
            
        # Don't expand subtasks (expansion_level > 0)
        if task.get('expansion_level', 0) > 0:
            return False
        
        # Expand if estimated hours > 8 (more than 1 day)
        if task.get('estimated_hours', 0) > 8:
            return True
            
        # Expand if complexity is high
        if task.get('complexity', '').lower() in ['high', 'complex']:
            return True
            
        # Expand if title contains expansion indicators
        title = task.get('title', '').lower()
        expansion_keywords = [
            'implement', 'develop', 'create', 'build', 'design',
            'integration', 'system', 'complete', 'full'
        ]
        
        if any(keyword in title for keyword in expansion_keywords):
            return True
            
        return False
    
    async def expand_task(self, task: Dict[str, Any], project_context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Expand a single task into subtasks"""
        
        # Build context for expansion
        context = self._build_expansion_context(task, project_context)
        
        # Generate subtasks
        subtasks_data = await self._generate_subtasks_with_claude(context)
        
        if not subtasks_data:
            return []
        
        # Process and validate subtasks
        subtasks = self._process_subtasks(subtasks_data, task)
        
        return subtasks
    
    def _build_expansion_context(self, task: Dict[str, Any], project_context: Dict[str, Any] = None) -> str:
        """Build context string for task expansion"""
        
        context = f"""
Task to expand:
- Title: {task.get('title', '')}
- Description: {task.get('description', '')}
- Category: {task.get('category', '')}
- Priority: {task.get('priority', '')}
- Estimated Hours: {task.get('estimated_hours', 0)}
- Complexity: {task.get('complexity', '')}
"""
        
        if project_context:
            context += f"""
Project Context:
- Name: {project_context.get('name', '')}
- Technologies: {', '.join([t.get('technology', '') for t in project_context.get('technologies', [])])}
- Complexity: {project_context.get('complexity_score', 0)}/10
- Package Manager: {project_context.get('package_manager', 'pnpm')}
"""
        
        return context
    
    async def _generate_subtasks_with_claude(self, context: str) -> Optional[List[Dict]]:
        """Generate subtasks - this will be processed by Claude in the session"""
        
        prompt = f"""You are an expert software project manager. Break down the following task into 3-7 specific, actionable subtasks.

{context}

Requirements for subtasks:
1. Each subtask should be completable in 1-4 hours
2. Subtasks should be specific and actionable (not vague)
3. Include proper sequencing and dependencies
4. Estimate hours realistically
5. Maintain same technology stack as project
6. Use SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)

Return ONLY a JSON array with this exact structure, no additional text:
[
  {{
    "title": "Specific action-oriented title",
    "description": "Detailed description of what needs to be done",
    "estimated_hours": 2,
    "complexity": "low|medium|high",
    "priority": "high|medium|low",
    "category": "design|backend|frontend|database|testing|deployment",
    "depends_on": []
  }}
]

Focus on technical implementation steps, not planning or documentation unless specifically needed."""

        print(f"\n📝 CLAUDE PROMPT:\n{prompt}\n")
        print("⏳ Waiting for Claude response...")
        
        # Since we can't directly call Claude from within the script,
        # we'll return a marker that tells us to process this manually
        return "NEEDS_CLAUDE_RESPONSE"
    
    def _process_subtasks(self, subtasks_data: List[Dict], parent_task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and validate generated subtasks"""
        
        processed = []
        for i, subtask_data in enumerate(subtasks_data):
            subtask = {
                'title': subtask_data.get('title', f'Subtask {i+1}'),
                'description': subtask_data.get('description', ''),
                'priority': subtask_data.get('priority', parent_task.get('priority', 'medium')),
                'estimated_hours': subtask_data.get('estimated_hours', 2),
                'complexity': subtask_data.get('complexity', 'medium'),
                'category': subtask_data.get('category', parent_task.get('category', 'general')),
                'status': 'todo',
                'parent_task_id': parent_task['id'],
                'expansion_level': parent_task.get('expansion_level', 0) + 1,
                'is_expanded': False,
                'depends_on': subtask_data.get('depends_on', [])
            }
            processed.append(subtask)
        
        return processed
    
    async def expand_task_by_id(self, task_id: int) -> Dict[str, Any]:
        """Expand a task by its ID"""
        
        async def expand_task_operation(db):
            # Get task details
            task = await db.get_task(task_id)
            if not task:
                return {"status": "error", "message": f"Task {task_id} not found"}
            
            # Check if should expand
            if not self.should_expand_task(task):
                return {"status": "skipped", "message": f"Task {task_id} doesn't need expansion"}
            
            # Get project context
            project = await db.get_project(task['project_id'])
            project_context = {
                'name': project['name'],
                'technologies': await db.get_project_technologies(task['project_id']),
                'complexity_score': project.get('complexity_score', 5),
                'package_manager': 'pnpm'
            }
            
            # Generate subtasks
            subtasks = await self.expand_task(task, project_context)
            
            if isinstance(subtasks, str) and subtasks == "NEEDS_CLAUDE_RESPONSE":
                return {"status": "needs_claude", "task": task, "context": project_context}
            
            if not subtasks:
                return {"status": "error", "message": "Failed to generate subtasks"}
            
            # Save subtasks to database
            subtask_ids = []
            for subtask in subtasks:
                subtask['project_id'] = task['project_id']
                subtask_id = await db.create_task(
                    project_id=task['project_id'],
                    title=subtask['title'],
                    description=subtask['description'],
                    priority=subtask['priority'],
                    estimated_hours=subtask['estimated_hours'],
                    complexity=subtask['complexity'],
                    category=subtask['category'],
                    parent_task_id=task['id'],
                    expansion_level=subtask['expansion_level']
                )
                subtask_ids.append(subtask_id)
            
            # Mark parent task as expanded
            await db.mark_task_expanded(task_id)
            
            return {
                "status": "success",
                "task_id": task_id,
                "task_title": task['title'],
                "subtasks_created": len(subtasks),
                "subtask_ids": subtask_ids
            }
        
        return await connect_and_run(expand_task_operation)

# Create instance for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python task_expander_claude.py <task_id>")
        sys.exit(1)
    
    task_id = int(sys.argv[1])
    expander = TaskExpanderClaude()
    
    async def test_expansion():
        result = await expander.expand_task_by_id(task_id)
        
        if result.get("status") == "needs_claude":
            task = result["task"]
            context = result["context"]
            
            # Print the context for Claude to process
            print("\n" + "="*60)
            print("TASK EXPANSION NEEDED")
            print("="*60)
            
            expansion_context = expander._build_expansion_context(task, context)
            await expander._generate_subtasks_with_claude(expansion_context)
            
            print("\n⚡ Claude, please generate the subtasks JSON above!")
            print("="*60)
        else:
            print(json.dumps(result, indent=2))
    
    asyncio.run(test_expansion())