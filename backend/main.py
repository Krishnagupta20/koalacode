from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from koala_runner import run_koala_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React frontend will work
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run")
async def run_code(request: Request):
    data = await request.json()
    code = data.get("code", "")
    output = run_koala_code(code)
    return {"output": output}
