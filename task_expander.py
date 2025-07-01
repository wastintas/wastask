#!/usr/bin/env python3
"""
Task Expansion Engine
Module for expanding high-level tasks into detailed subtasks using AI
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
try:
    import litellm
except ImportError:
    print("⚠️ litellm not available - task expansion will use mock data")
    litellm = None
from database_manager import WasTaskDatabase, connect_and_run

class TaskExpander:
    def __init__(self):
        self.model = "claude-3-5-haiku-20241022"  # Fast model for task breakdown
        
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
        """Expand a single task into subtasks using AI"""
        
        # Build context for AI
        context = self._build_expansion_context(task, project_context)
        
        # Generate subtasks with AI
        subtasks_data = await self._generate_subtasks_with_ai(context)
        
        if not subtasks_data:
            return []
        
        # Process and validate subtasks
        subtasks = self._process_subtasks(subtasks_data, task)
        
        return subtasks
    
    def _build_expansion_context(self, task: Dict[str, Any], project_context: Dict[str, Any] = None) -> str:
        """Build context string for AI task expansion"""
        
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
- Package Manager: {project_context.get('package_manager', 'npm')}
"""
        
        return context
    
    async def _generate_subtasks_with_ai(self, context: str) -> Optional[List[Dict]]:
        """Use AI to generate subtasks breakdown"""
        
        prompt = f"""You are an expert software project manager. Break down the following task into 3-7 specific, actionable subtasks.

{context}

Requirements for subtasks:
1. Each subtask should be completable in 1-4 hours
2. Subtasks should be specific and actionable (not vague)
3. Include proper sequencing and dependencies
4. Estimate hours realistically
5. Maintain same technology stack as project
6. Use SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)

Return JSON array with this exact structure:
[
  {{
    "title": "Specific action-oriented title",
    "description": "Detailed description of what needs to be done",
    "estimated_hours": 2,
    "complexity": "low|medium|high",
    "priority": "low|medium|high",
    "category": "same as parent or more specific",
    "depends_on": [] // array of subtask titles this depends on
  }}
]

Focus on technical implementation steps, not planning or documentation unless specifically needed."""

        try:
            if litellm is None:
                # Mock data for testing when AI is not available
                return self._generate_mock_subtasks(context)
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].strip()
            
            return json.loads(content)
            
        except Exception as e:
            print(f"❌ AI expansion failed: {e}")
            # Fallback to mock data
            return self._generate_mock_subtasks(context)
    
    def _generate_mock_subtasks(self, context: str) -> List[Dict]:
        """Generate mock subtasks for testing purposes"""
        print("🔄 Using mock subtask generation")
        
        # Extract task title from context
        task_title = "API Implementation"
        if "Title:" in context:
            task_title = context.split("Title:")[1].split("\n")[0].strip()
        
        return [
            {
                "title": f"Design {task_title} architecture",
                "description": f"Create architectural design and data flow for {task_title}",
                "estimated_hours": 2,
                "complexity": "medium",
                "priority": "high",
                "category": "design",
                "depends_on": []
            },
            {
                "title": f"Implement core {task_title} logic",
                "description": f"Develop the main business logic for {task_title}",
                "estimated_hours": 4,
                "complexity": "high",
                "priority": "high", 
                "category": "implementation",
                "depends_on": [f"Design {task_title} architecture"]
            },
            {
                "title": f"Add {task_title} validation",
                "description": f"Implement input validation and error handling",
                "estimated_hours": 2,
                "complexity": "medium",
                "priority": "medium",
                "category": "validation",
                "depends_on": [f"Implement core {task_title} logic"]
            },
            {
                "title": f"Test {task_title} integration",
                "description": f"Create and run integration tests for {task_title}",
                "estimated_hours": 3,
                "complexity": "medium",
                "priority": "medium",
                "category": "testing",
                "depends_on": [f"Add {task_title} validation"]
            }
        ]
    
    def _process_subtasks(self, subtasks_data: List[Dict], parent_task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and validate AI-generated subtasks"""
        
        processed = []
        parent_id = parent_task.get('id')
        project_id = parent_task.get('project_id')
        
        for i, subtask in enumerate(subtasks_data):
            processed_subtask = {
                'project_id': project_id,
                'title': subtask.get('title', f'Subtask {i+1}'),
                'description': subtask.get('description', ''),
                'estimated_hours': min(max(subtask.get('estimated_hours', 2), 1), 8),  # 1-8 hours
                'complexity': subtask.get('complexity', 'medium').lower(),
                'priority': subtask.get('priority', parent_task.get('priority', 'medium')).lower(),
                'category': subtask.get('category', parent_task.get('category', 'implementation')),
                'status': 'todo',
                'parent_task_id': parent_id,
                'expansion_level': (parent_task.get('expansion_level', 0) + 1),
                'is_expanded': False,
                'depends_on_titles': subtask.get('depends_on', [])  # Will be resolved to IDs later
            }
            processed.append(processed_subtask)
        
        return processed
    
    async def expand_task_by_id(self, task_id: int) -> Dict[str, Any]:
        """Expand a specific task by ID"""
        
        async def expansion_operation(db):
            # Get task and project context
            task = await self._get_task_by_id(db, task_id)
            if not task:
                return {"status": "error", "message": f"Task {task_id} not found"}
            
            if not self.should_expand_task(dict(task)):
                return {"status": "skipped", "message": "Task doesn't need expansion"}
            
            project_context = await self._get_project_context(db, task['project_id'])
            
            # Generate subtasks
            subtasks = await self.expand_task(dict(task), project_context)
            
            if not subtasks:
                return {"status": "error", "message": "Failed to generate subtasks"}
            
            # Save subtasks to database
            subtask_ids = await self._save_subtasks(db, subtasks)
            
            # Mark parent task as expanded
            await db.update_task_expansion_status(task_id, True)
            
            return {
                "status": "success",
                "task_id": task_id,
                "subtasks_created": len(subtasks),
                "subtask_ids": subtask_ids
            }
        
        return await connect_and_run(expansion_operation)
    
    async def expand_project_tasks(self, project_id: int, max_tasks: int = 10) -> Dict[str, Any]:
        """Expand all expandable tasks in a project"""
        
        async def expansion_operation(db):
            # Get expandable tasks
            expandable_tasks = await self._get_expandable_tasks(db, project_id)
            
            if not expandable_tasks:
                return {"status": "complete", "message": "No tasks need expansion"}
            
            # Limit number of tasks to expand
            tasks_to_expand = expandable_tasks[:max_tasks]
            
            project_context = await self._get_project_context(db, project_id)
            
            results = []
            for task in tasks_to_expand:
                try:
                    subtasks = await self.expand_task(dict(task), project_context)
                    if subtasks:
                        subtask_ids = await self._save_subtasks(db, subtasks)
                        await db.update_task_expansion_status(task['id'], True)
                        results.append({
                            "task_id": task['id'],
                            "task_title": task['title'],
                            "subtasks_created": len(subtasks),
                            "subtask_ids": subtask_ids
                        })
                    
                except Exception as e:
                    print(f"❌ Failed to expand task {task['id']}: {e}")
                    continue
            
            return {
                "status": "success",
                "project_id": project_id,
                "tasks_expanded": len(results),
                "results": results
            }
        
        return await connect_and_run(expansion_operation)
    
    async def _get_task_by_id(self, db, task_id: int):
        """Get task by ID"""
        query = "SELECT * FROM wastask_tasks WHERE id = $1"
        return await db.pool.fetchrow(query, task_id)
    
    async def _get_project_context(self, db, project_id: int):
        """Get project context for task expansion"""
        project_data = await db.get_project(project_id)
        if project_data:
            return {
                'name': project_data['project']['name'],
                'complexity_score': project_data['project']['complexity_score'],
                'package_manager': project_data['project']['package_manager'],
                'technologies': project_data['technologies']
            }
        return {}
    
    async def _get_expandable_tasks(self, db, project_id: int):
        """Get tasks that can be expanded"""
        query = """
        SELECT * FROM wastask_tasks 
        WHERE project_id = $1 
          AND is_expanded = FALSE 
          AND expansion_level = 0
          AND (estimated_hours > 8 OR complexity IN ('high', 'complex'))
        ORDER BY priority DESC, estimated_hours DESC
        """
        return await db.pool.fetch(query, project_id)
    
    async def _save_subtasks(self, db, subtasks: List[Dict]) -> List[int]:
        """Save subtasks to database"""
        subtask_ids = []
        
        for subtask in subtasks:
            # Remove depends_on_titles before inserting
            depends_on_titles = subtask.pop('depends_on_titles', [])
            
            query = """
            INSERT INTO wastask_tasks 
            (project_id, title, description, priority, estimated_hours, complexity, 
             category, status, parent_task_id, expansion_level, is_expanded)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            RETURNING id
            """
            
            subtask_id = await db.pool.fetchval(
                query,
                subtask['project_id'], subtask['title'], subtask['description'],
                subtask['priority'], subtask['estimated_hours'], subtask['complexity'],
                subtask['category'], subtask['status'], subtask['parent_task_id'],
                subtask['expansion_level'], subtask['is_expanded']
            )
            
            subtask_ids.append(subtask_id)
        
        return subtask_ids

# Add expansion methods to database manager
async def update_task_expansion_status(self, task_id: int, is_expanded: bool):
    """Update task expansion status"""
    query = "UPDATE wastask_tasks SET is_expanded = $1 WHERE id = $2"
    async with self.pool.acquire() as conn:
        await conn.execute(query, is_expanded, task_id)

# Monkey patch the method to WasTaskDatabase
WasTaskDatabase.update_task_expansion_status = update_task_expansion_status