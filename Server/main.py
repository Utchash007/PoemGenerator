from typing import Union
from inference.inference import *
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from docparsing.docparsing import recieve_file

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}



@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    topic: str = Form(...),
    lines: int = Form(8),
):
    context_text = recieve_file(file)
    if not isinstance(context_text, str) or not context_text.strip():
        raise HTTPException(status_code=400, detail="Unsupported file or empty text extracted")

    pr = await generate_duet_poem(topic=topic, lines=lines, context_text=context_text)
    judgment = judge_poem(pr, context_text=context_text)

    return {
        "topic": topic,
        "lines": pr.lines,
        "by_agent": pr.by_agent,
        "judge": judgment,
    }
