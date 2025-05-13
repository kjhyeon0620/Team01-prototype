from typing import Annotated
from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()




##### Langgraph Structure ######

def create_graph(memory, model='openai:gpt-4.1', tools=[]):

    class State(TypedDict):
        messages: Annotated[list, add_messages]


    llm = init_chat_model(model)
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    tool_node = ToolNode(tools=tools)

    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )

    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph = graph_builder.compile(checkpointer=memory)

    return graph




if __name__ == '__main__':

    memory = MemorySaver()
    graph = create_graph(memory, tools=[])
    