from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.output_parsers import JsonOutputParser
from .prompts import*
from .states import*
from langgraph.graph import StateGraph
from langgraph.constants import END
llm = ChatGroq(model='openai/gpt-oss-120b')
user_prompt = "create a simple calculator web application"


def planner_agent(state : dict) ->dict:
    user_prompt = state["user_prompt"]
    parser = JsonOutputParser(pydantic_object=Plan)
    response = llm.invoke(
        f"{planner_prompt(user_prompt)}\n\nReturn output in JSON format:\n{parser.get_format_instructions()}"
    )
    parsed = parser.parse(response.content)
    if parsed is None:
        raise ValueError("Architect did not return a valid response")
    return {"plan" : parsed}
def architect_agent(state : dict) ->dict:
    plan : Plan = state["plan"]
    parser = JsonOutputParser(pydantic_object=Plan)  
    response = llm.invoke(
        f"{architect_prompt(plan)}\n\nReturn output in JSON format:\n{parser.get_format_instructions()}"
    )
    parsed = parser.parse(response.content)
    if parsed is None:
        raise ValueError("Architect did not return a valid response")
    
    return {"task_plan" : parsed}
def coder_agent(state :dict) -> dict:
    coder_state = state.get("coder_state")
    if coder_state is None :
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan_implementation_steps
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state":coder_state,"status" : "DONE"}
    
    current_task = steps[coder_state.current_step_idx]
    existing_content = read_file.run(current_task.filepath)
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes."
    )
    system_prompt = coder_system_prompt()
    response = llm.invoke(system_prompt + user_prompt)
    return {"code" , response.content}
    system_prompt = coder_system_prompt()
    coder_tools = [read_files,write_files,list_files,get_current_directory]
    react_agent = create_react_agent(llm,coder_tools)
    react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                     {"role": "user", "content": user_prompt}]})

    coder_state.current_step_idx += 1
    return {"coder_state", coder_state}


    


graph = StateGraph(dict)
graph.add_node("planner",planner_agent)
graph.add_node("architect",architect_agent)
graph.add_node("coder",coder_agent)

graph.add_edge("planner" , "architect")
graph.add_edge("architect","coder")
graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)
graph.set_entry_point("planner")
agent = graph.compile()
user_prompt = "create a simple calculator web application"
result = agent.invoke({"user_prompt":user_prompt})
print(result)
print(result["task_plan"])