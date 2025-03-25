from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import os
from groq import Groq

app = FastAPI()

client = Groq(api_key=os.environ["GROQAPIKEY"])

@app.get("/", response_class=HTMLResponse)
async def generate_rizz(request: Request):
    # Extract topic from URL (e.g., ?love → "love")
    topic = list(request.query_params.keys())[0] if request.query_params else "random"
    
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f"Generate a {topic} pickup line. Keep it under 20 words.",
        }
    ],
    model="llama-3.3-70b-versatile",)
    
    rizz_line = chat_completion.choices[0].message.content

    # WhatsApp-friendly response
    return f"""
    <!DOCTYPE html>
    <html prefix="og: https://ogp.me/ns#">
    <head>
        <title>Rizz Generator</title>
        <meta property="og:title" content="{rizz_line.capitalize()} Rizz" />
        <meta property="og:description" content="{topic}" />
        <meta property="og:type" content="website" />
        
    </head>
    <body>
        <h1>{rizz_line}</h1>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
