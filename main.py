from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from src.graph import create_graph, Command, MemorySaver 
from src.tools import transfer, getAccountBalance
from pydantic import BaseModel
from typing import Union
import json


## llm configuration 
memory = MemorySaver()
graph = create_graph(memory, tools=[transfer, getAccountBalance])



app = FastAPI()
app.mount("/assets", StaticFiles(directory="public/assets"), name="static")



## root
@app.get("/", response_class=FileResponse)
async def main():
    return "public/index.html"




## llm stream
class StreamRequest(BaseModel):
    query : Union[str, dict]
    thread_id : str


async def graph_generator(graph, query: Union[str, dict], thread_id: str):

    
    data = {'messages':[{'role': 'user', 'content': query}]} if isinstance(query, str) else Command(resume=query)
    async for event in graph.astream_events(data, config={"configurable": {"thread_id": thread_id}}, version="v2"):
        
      
        if event["event"] == "on_chat_model_stream":
            if event["data"]["chunk"].content:
                yield f"data: {event['data']['chunk'].content}\n\n"

        elif event["event"] == "on_tool_start":
            tool_name = event["name"]
            tool_parameters = event["data"]["input"]

            # APPROVAL_REQUIRED 도구 처리
            if tool_name in ['transfer']:
                yield f"data: [APPROVAL_REQUIRED]{tool_name}:{json.dumps(tool_parameters)}[/APPROVAL_REQUIRED]\n\n"
        
        elif event["event"] == "on_tool_end":
            tool_output = event["data"]["output"]
            yield f"data: [TOOL_END]{tool_output}[/TOOL_END]\n\n"
        
        elif event["event"] == "on_chain_end" and "output" in event["data"]:
            if "output" in event["data"]:
                yield f"data: [DONE]\n\n"

    print('--------')
@app.post("/stream")
async def stream(request: StreamRequest):
    generator = graph_generator(graph, request.query, request.thread_id)
    return StreamingResponse(generator, media_type="text/event-stream")



