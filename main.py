from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from src.graph import create_graph, Command, MemorySaver 
from src.tools import transfer, getAccountBalance
from pydantic import BaseModel
from typing import Union
import json
import httpx

from scipy.io import wavfile
import io

from src.database import db, Query
from src.utils import numpy_to_base64, base64_to_numpy

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

@app.post("/stream")
async def stream(request: StreamRequest):
    generator = graph_generator(graph, request.query, request.thread_id)
    return StreamingResponse(generator, media_type="text/event-stream")




@app.post('/set-voice-reference')
async def set_voice_reference(file: UploadFile = File(...)): # file is .wav format
    
    audio_buffer = io.BytesIO(await file.read())
    _, data = wavfile.read(audio_buffer) # data is np.darray


    # insert database 
    voice_reference = db.table('voice_reference')
    voice_reference.insert({
        'phone_number': '01012345678',
        'reference': [numpy_to_base64(data)]
    })



# voice id verification 
async def verify_voice_id(file: UploadFile) -> bool:

    audio_buffer = io.BytesIO(await file.read())
    _, data = wavfile.read(audio_buffer) # data is np.darray


    query = Query()

    voice_reference = db.table('voice_reference')
    reference = voice_reference.search(query.phone_number == '01012345678')[0]

    ref_array = base64_to_numpy(reference['reference'])

    print(reference['phone_number'])

    # reference + data verification logic ... [ ref_array, data ]
    return False

# 블록체인 프록시
EXPRESS_BASE_URL = 'http://localhost:3000'

@app.api_route("/express/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_express(request: Request, path: str):
    async with httpx.AsyncClient() as client:
        method = request.method
        url = f"{EXPRESS_BASE_URL}/{path}"
        headers = dict(request.headers)
        body = await request.body()
        response = await client.request(method, url, headers=headers, content=body)
        return response.text, response.status_code, response.headers.items()
