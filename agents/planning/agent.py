"""
WasTask Planning Agent - Specialized in project planning and task decomposition
"""
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:
    from google.adk import LlmAgent, FunctionTool
except ImportError:
    # Use mock implementation for development
    from wastask.mock_adk import LlmAgent, FunctionTool

from wastask.config.settings import settings, PromptTemplates
from wastask.core.models import Project, Task, TaskPriority, TaskStatus


logger = logging.getLogger(__name__)


class PlanningAgent:
    """
    Specialized agent for project planning, task decomposition, and timeline creation.
    Uses advanced prompt engineering techniques for optimal planning results.
    """
    
    def __init__(self, model: str = None):
        self.model = model or settings.adk_model_default
        self.agent = self._create_agent()
    
    def _create_agent(self) -> LlmAgent:
        """Create the planning agent with specialized tools"""
        tools = [
            FunctionTool(self.decompose_project_tool),
            FunctionTool(self.estimate_timeline_tool),
            FunctionTool(self.analyze_dependencies_tool),
            FunctionTool(self.create_milestone_plan_tool),
            FunctionTool(self.optimize_resource_allocation_tool),
            FunctionTool(self.assess_project_risks_tool),
        ]
        
        return LlmAgent(
            name="planning_agent",
            model=self.model,
            description="Expert project planning and task decomposition agent",
            instruction=self._get_planning_instruction(),
            tools=tools,
            temperature=0.1,  # Lower temperature for more consistent planning
            max_tokens=settings.adk_max_tokens,
        )
    
    def _get_planning_instruction(self) -> str:
        """Get the planning agent's system instruction"""
        return """
        You are an expert Project Planning Agent with deep expertise in:
        - Agile and traditional project management methodologies
        - Task decomposition using Work Breakdown Structure (WBS)
        - Timeline estimation and critical path analysis
        - Risk assessment and mitigation planning
        - Resource allocation and capacity planning
        
        Your planning approach:
        1. ANALYZE the project scope, objectives, and constraints
        2. DECOMPOSE complex requirements into manageable tasks
        3. ESTIMATE effort and duration realistically
        4. IDENTIFY dependencies and potential bottlenecks
        5. CREATE realistic timelines with buffer time
        6. PRIORITIZE tasks based on value and dependencies
        7. ASSESS risks and suggest mitigation strategies
        
        Always provide structured, actionable plans that teams can execute effectively.
        Consider both technical and business perspectives in your recommendations.
        
        When decomposing tasks:
        - Break down into tasks that can be completed in 1-8 hours
        - Ensure tasks have clear acceptance criteria
        - Identify required skills and roles
        - Consider testing and review time
        - Account for integration points
        
        Your outputs should be JSON-formatted for easy processing by other systems.
        """
    
    async def create_project_plan(
        self, 
        project_description: str, 
        constraints: Dict[str, Any] = None,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive project plan from a description.
        
        Args:
            project_description: Detailed description of the project
            constraints: Time, budget, resource constraints
            preferences: User preferences for methodology, tools, etc.
            
        Returns:
            Comprehensive project plan with tasks, timeline, and resources
        """
        try:
            # Prepare context
            context = {
                "description": project_description,
                "constraints": constraints or {},
                "preferences": preferences or {},
                "current_date": datetime.now(timezone.utc).isoformat()
            }
            
            # Generate plan using the agent
            plan_prompt = self._create_planning_prompt(context)
            response = await self.agent.run(plan_prompt)
            
            # Parse and structure the response
            plan = self._parse_planning_response(response.content)
            
            return {
                "status": "success",
                "plan": plan,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating project plan: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create project plan: {str(e)}"
            }
    
    def _create_planning_prompt(self, context: Dict[str, Any]) -> str:
        """Create a detailed planning prompt"""
        return f"""
        Create a comprehensive project plan for the following project:
        
        PROJECT DESCRIPTION:
        {context['description']}
        
        CONSTRAINTS:
        {json.dumps(context.get('constraints', {}), indent=2)}
        
        PREFERENCES:
        {json.dumps(context.get('preferences', {}), indent=2)}
        
        CURRENT DATE: {context['current_date']}
        
        Please provide a detailed plan following this structure:
        
        {{
            "project_summary": {{
                "title": "Project title",
                "description": "Brief project description",
                "objectives": ["List of key objectives"],
                "success_criteria": ["Measurable success criteria"],
                "scope": "What's included and excluded"
            }},
            "phases": [
                {{
                    "name": "Phase name",
                    "description": "Phase description",
                    "duration_days": 0,
                    "tasks": [
                        {{
                            "title": "Task title",
                            "description": "Detailed task description",
                            "estimated_hours": 0,
                            "priority": "high|medium|low",
                            "skills_required": ["List of required skills"],
                            "dependencies": ["Task IDs this depends on"],
                            "acceptance_criteria": ["Clear completion criteria"],
                            "risk_level": "high|medium|low"
                        }}
                    ]
                }}
            ],
            "timeline": {{
                "total_duration_days": 0,
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "milestones": [
                    {{
                        "name": "Milestone name",
                        "date": "YYYY-MM-DD",
                        "deliverables": ["List of deliverables"]
                    }}
                ]
            }},
            "resources": {{
                "roles_needed": ["List of required roles"],
                "estimated_team_size": 0,
                "budget_estimate": "If applicable",
                "tools_required": ["List of tools/technologies"]
            }},
            "risks": [
                {{
                    "risk": "Risk description",
                    "probability": "high|medium|low",
                    "impact": "high|medium|low",
                    "mitigation": "Mitigation strategy"
                }}
            ],
            "recommendations": ["List of key recommendations"]
        }}
        
        Ensure all estimates are realistic and account for:
        - Code review and testing time
        - Integration and deployment
        - Buffer time for unexpected issues
        - Knowledge transfer and documentation
        """
    
    def _parse_planning_response(self, response: str) -> Dict[str, Any]:
        """Parse and validate the planning response"""
        try:
            # Extract JSON from response if it contains other text
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                plan = json.loads(json_str)
                
                # Add generated IDs to tasks
                task_counter = 1
                for phase in plan.get("phases", []):
                    for task in phase.get("tasks", []):
                        if "id" not in task:
                            task["id"] = f"task_{task_counter:03d}"
                            task_counter += 1
                
                return plan
            else:
                # Fallback: create basic structure from text
                return self._create_fallback_plan(response)
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, creating fallback plan")
            return self._create_fallback_plan(response)
    
    def _create_fallback_plan(self, response: str) -> Dict[str, Any]:
        """Create a basic plan structure from unstructured response"""
        return {
            "project_summary": {
                "title": "Generated Project Plan",
                "description": "Plan generated from user requirements",
                "objectives": ["Complete project as specified"],
                "success_criteria": ["All requirements met"],
                "scope": "As defined in requirements"
            },
            "phases": [
                {
                    "name": "Planning",
                    "description": "Project planning and setup",
                    "duration_days": 5,
                    "tasks": [
                        {
                            "id": "task_001",
                            "title": "Detailed requirements analysis",
                            "description": response[:200] + "...",
                            "estimated_hours": 8,
                            "priority": "high",
                            "skills_required": ["Analysis"],
                            "dependencies": [],
                            "acceptance_criteria": ["Requirements documented"],
                            "risk_level": "low"
                        }
                    ]
                }
            ],
            "timeline": {
                "total_duration_days": 30,
                "start_date": datetime.now(timezone.utc).date().isoformat(),
                "end_date": (datetime.now(timezone.utc) + timedelta(days=30)).date().isoformat(),
                "milestones": []
            },
            "resources": {
                "roles_needed": ["Developer", "Designer"],
                "estimated_team_size": 2,
                "tools_required": ["Standard development tools"]
            },
            "risks": [],
            "recommendations": ["Review and refine this initial plan"]
        }
    
    # Tool implementations
    def decompose_project_tool(self, project_description: str, max_depth: int = 3) -> Dict[str, Any]:
        """Decompose a project into hierarchical tasks"""
        try:
            # Use the task decomposition prompt template
            prompt = PromptTemplates.TASK_DECOMPOSITION.format(input=project_description)
            
            # This would use the agent to process the decomposition
            # For now, return a structured example
            decomposition = {
                "project": project_description,
                "breakdown": {
                    "level_1": [
                        {
                            "id": "phase_1",
                            "name": "Planning & Design",
                            "description": "Initial project setup and design phase",
                            "estimated_days": 10,
                            "tasks": [
                                {
                                    "id": "task_001",
                                    "title": "Requirements gathering",
                                    "estimated_hours": 16,
                                    "priority": "high"
                                },
                                {
                                    "id": "task_002", 
                                    "title": "System design",
                                    "estimated_hours": 24,
                                    "priority": "high"
                                }
                            ]
                        },
                        {
                            "id": "phase_2",
                            "name": "Implementation",
                            "description": "Core development phase",
                            "estimated_days": 20,
                            "tasks": [
                                {
                                    "id": "task_003",
                                    "title": "Core feature development",
                                    "estimated_hours": 40,
                                    "priority": "high"
                                }
                            ]
                        }
                    ]
                }
            }
            
            return {
                "status": "success",
                "decomposition": decomposition
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to decompose project: {str(e)}"
            }
    
    def estimate_timeline_tool(self, tasks: List[Dict[str, Any]], team_size: int = 1) -> Dict[str, Any]:
        """Estimate project timeline based on tasks and team size"""
        try:
            total_hours = sum(task.get("estimated_hours", 8) for task in tasks)
            
            # Account for team efficiency, meetings, buffer time
            efficiency_factor = 0.75  # 75% productive time
            buffer_factor = 1.2  # 20% buffer
            
            effective_hours = total_hours * buffer_factor / efficiency_factor
            hours_per_day = 6  # Productive hours per day
            days_per_person = effective_hours / hours_per_day
            
            timeline_days = max(1, int(days_per_person / team_size))
            
            start_date = datetime.now(timezone.utc).date()
            end_date = start_date + timedelta(days=timeline_days)
            
            timeline = {
                "total_estimated_hours": total_hours,
                "effective_hours_needed": effective_hours,
                "timeline_days": timeline_days,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "team_size": team_size,
                "assumptions": {
                    "hours_per_day": hours_per_day,
                    "efficiency_factor": efficiency_factor,
                    "buffer_factor": buffer_factor
                }
            }
            
            return {
                "status": "success",
                "timeline": timeline
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to estimate timeline: {str(e)}"
            }
    
    def analyze_dependencies_tool(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze task dependencies and identify critical path"""
        try:
            # Simple dependency analysis
            dependencies = {}
            critical_path = []
            
            for task in tasks:
                task_id = task.get("id", task.get("title", "unknown"))
                task_deps = task.get("dependencies", [])
                dependencies[task_id] = {
                    "task": task,
                    "depends_on": task_deps,
                    "blocks": []
                }
            
            # Find what each task blocks
            for task_id, task_info in dependencies.items():
                for dep in task_info["depends_on"]:
                    if dep in dependencies:
                        dependencies[dep]["blocks"].append(task_id)
            
            # Simple critical path calculation (tasks with most blockers)
            critical_tasks = sorted(
                dependencies.items(),
                key=lambda x: len(x[1]["blocks"]),
                reverse=True
            )[:5]
            
            analysis = {
                "dependencies": dependencies,
                "critical_path": [task[0] for task in critical_tasks],
                "recommendations": [
                    "Focus on critical path tasks first",
                    "Parallelize independent tasks",
                    "Monitor dependency blockers closely"
                ]
            }
            
            return {
                "status": "success",
                "analysis": analysis
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze dependencies: {str(e)}"
            }
    
    def create_milestone_plan_tool(self, project_duration_days: int, phases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create milestone plan for the project"""
        try:
            start_date = datetime.now(timezone.utc).date()
            milestones = []
            
            current_date = start_date
            for i, phase in enumerate(phases):
                phase_duration = phase.get("duration_days", project_duration_days // len(phases))
                milestone_date = current_date + timedelta(days=phase_duration)
                
                milestones.append({
                    "id": f"milestone_{i+1}",
                    "name": f"{phase['name']} Complete",
                    "date": milestone_date.isoformat(),
                    "description": f"Completion of {phase['name']} phase",
                    "deliverables": phase.get("deliverables", [f"{phase['name']} completed"]),
                    "success_criteria": phase.get("success_criteria", ["All phase tasks completed"])
                })
                
                current_date = milestone_date
            
            return {
                "status": "success",
                "milestones": milestones
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create milestone plan: {str(e)}"
            }
    
    def optimize_resource_allocation_tool(self, tasks: List[Dict[str, Any]], available_resources: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize resource allocation across tasks"""
        try:
            # Simple resource optimization based on skills and availability
            resource_plan = {
                "assignments": [],
                "utilization": {},
                "recommendations": []
            }
            
            # Group tasks by required skills
            skill_groups = {}
            for task in tasks:
                skills = task.get("skills_required", ["general"])
                for skill in skills:
                    if skill not in skill_groups:
                        skill_groups[skill] = []
                    skill_groups[skill].append(task)
            
            # Create assignments
            for skill, skill_tasks in skill_groups.items():
                resource_plan["assignments"].append({
                    "skill": skill,
                    "tasks": [task.get("id", task.get("title")) for task in skill_tasks],
                    "total_hours": sum(task.get("estimated_hours", 8) for task in skill_tasks),
                    "recommended_resources": max(1, len(skill_tasks) // 3)
                })
            
            resource_plan["recommendations"] = [
                "Assign specialists to their expertise areas",
                "Cross-train team members to increase flexibility",
                "Plan for knowledge transfer sessions"
            ]
            
            return {
                "status": "success",
                "resource_plan": resource_plan
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Failed to optimize resource allocation: {str(e)}"
            }
    
    def assess_project_risks_tool(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess project risks and suggest mitigation strategies"""
        try:
            risks = []
            
            # Common project risks assessment
            duration = project_data.get("timeline", {}).get("timeline_days", 30)
            team_size = project_data.get("resources", {}).get("estimated_team_size", 1)
            complexity = len(project_data.get("phases", []))
            
            # Duration risk
            if duration > 90:
                risks.append({
                    "risk": "Long project duration",
                    "probability": "medium",
                    "impact": "high",
                    "mitigation": "Break into smaller releases, implement iterative approach"
                })
            
            # Team size risk
            if team_size == 1:
                risks.append({
                    "risk": "Single point of failure",
                    "probability": "high",
                    "impact": "high",
                    "mitigation": "Document all work, establish backup plans, cross-train"
                })
            
            # Complexity risk
            if complexity > 5:
                risks.append({
                    "risk": "High complexity",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "Simplify scope, use proven technologies, increase buffer time"
                })
            
            # Always include common risks
            risks.extend([
                {
                    "risk": "Scope creep",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "Clear requirements documentation, change control process"
                },
                {
                    "risk": "Technical challenges",
                    "probability": "medium",
                    "impact": "medium",
                    "mitigation": "Proof of concepts, technical spikes, expert consultation"
                }
            ])
            
            return {
                "status": "success",
                "risk_assessment": {
                    "risks": risks,
                    "overall_risk_level": "medium",
                    "key_recommendations": [
                        "Regular risk review meetings",
                        "Maintain risk register",
                        "Implement early warning systems"
                    ]
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to assess risks: {str(e)}"
            }


# Global planning agent instance
planning_agent = PlanningAgent()