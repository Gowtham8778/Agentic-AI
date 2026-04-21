def planner_prompt(user_prompt: str) -> str:
    return f"""
You are the PLANNER agent.

Convert the user request into a structured project plan.

Return ONLY JSON:
{{
  "name": "Project name",
  "description": "Short description",
  "techstack": "Tech stack",
  "features": ["feature1", "feature2"],
  "files": [
    {{
      "path": "index.html",
      "purpose": "Main UI"
    }}
  ]
}}

User Request:
{user_prompt}
"""


def architect_prompt(plan: str) -> str:
    return f"""
You are the ARCHITECT agent.

Break this into implementation steps.

Return ONLY JSON:
{{
  "name": "Project name",
  "description": "Project description",
  "implementation_steps": [
    {{
      "filepath": "index.html",
      "task_description": "Create HTML structure"
    }}
  ]
}}

Plan:
{plan}
"""


def coder_system_prompt() -> str:
    return """
You are the CODER agent.

Rules:
- ALWAYS use write_file(path, content)
- ALWAYS write full file content
- NO explanations
"""