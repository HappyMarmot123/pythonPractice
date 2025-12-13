import uvicorn
import string
import random
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="fastapi url shortener")
url_database = {}

class URLItem(BaseModel):
    long_url: str

def generate_short_code(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@app.post("/shorten")
def create_short_url(item: URLItem, request: Request):
    short_code = generate_short_code()
    url_database[short_code] = item.long_url

    base_url = str(request.base_url)
    short_url = f"{base_url}{short_code}"

    return {
        "long_url": item.long_url,
        "short_code": short_code,
        "short_url": short_url
    }

@app.get("/{short_code}")
def redirect_to_long_url(short_code: str):
    long_url = url_database.get(short_code)

    if not long_url:
        raise HTTPException(status_code = 404, detail="Short URL not found")

    return RedirectResponse(url=long_url, status_code=307)