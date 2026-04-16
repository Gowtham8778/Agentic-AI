from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.output_parsers import JsonOutputParser
from prompts import*
from states import*
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

    


graph = StateGraph(dict)
graph.add_node("planner",planner_agent)
graph.add_node("architect",architect_agent)
graph.add_edge("planner","architect")
graph.set_entry_point("planner")
agent = graph.compile()
user_prompt = "create a simple calculator web application"
result = agent.invoke({"user_prompt":user_prompt})
print(result)
print(result["task_plan"])