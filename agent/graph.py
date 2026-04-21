from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langgraph.graph import StateGraph
from langgraph.constants import END
from langgraph.prebuilt import create_react_agent

from .prompts import *
from .states import *
from .tools import write_file, read_file, list_files, get_current_directory, init_project_root

llm = ChatGroq(model='openai/gpt-oss-120b')


def planner_agent(state: dict) -> dict:
    parser = JsonOutputParser(pydantic_object=Plan)

    response = llm.invoke(
        f"{planner_prompt(state['user_prompt'])}\n\n{parser.get_format_instructions()}"
    )

    parsed = parser.parse(response.content)
    return {"plan": parsed}


def architect_agent(state: dict) -> dict:
    parser = JsonOutputParser(pydantic_object=TaskPlan)

    response = llm.invoke(
        f"{architect_prompt(state['plan'])}\n\n{parser.get_format_instructions()}"
    )

    parsed = parser.parse(response.content)
    return {"task_plan": parsed}


def coder_agent(state: dict) -> dict:
    coder_state = state.get("coder_state")

    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"])

    steps = coder_state.task_plan.implementation_steps

    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    task = steps[coder_state.current_step_idx]

    tools = [write_file, read_file, list_files, get_current_directory]
    agent = create_react_agent(llm, tools)

    agent.invoke({
        "messages": [
            {"role": "system", "content": coder_system_prompt()},
            {"role": "user", "content": f"Task: {task.task_description}\nFile: {task.filepath}"}
        ]
    })

    coder_state.current_step_idx += 1

    return {"coder_state": coder_state}


graph = StateGraph(dict)

graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")

graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)

graph.set_entry_point("planner")

agent = graph.compile()


if __name__ == "__main__":
    init_project_root()

    result = agent.invoke({
        "user_prompt": "Create a simple calculator web application"
    })

    print(result)