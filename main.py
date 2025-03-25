from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from groq import Groq
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

app = FastAPI()
client = Groq(api_key=os.environ["GROQAPIKEY"])

def generate_image(text: str) -> str:
    """Generate meme-style image with text"""
    img = Image.new('RGB', (800, 400), color=(0, 0, 0))  # Black background
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw = ImageDraw.Draw(img)
    wrapped_text = textwrap.fill(text, width=30)
    
    # Center text
    text_width = draw.textlength(wrapped_text, font=font)
    x = (800 - text_width) / 2
    draw.text((x, 150), wrapped_text, font=font, fill=(255, 255, 255))  # White text
    
    image_path = "rizz.png"
    img.save(image_path)
    return image_path

@app.get("/", response_class=HTMLResponse)
async def generate_rizz(request: Request):
    topic = list(request.query_params.keys())[0] if request.query_params else "random"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Generate a {topic} pickup line. Keep it under 20 words.",
            }
        ],
        model="llama3-70b-8192",
    )
    
    rizz_line = chat_completion.choices[0].message.content
    image_path = generate_image(rizz_line)
    
    # Return HTML with only image in meta tags
    return f"""
    <!DOCTYPE html>
    <html prefix="og: https://ogp.me/ns#">
    <head>
        <meta property="og:title" content="Rizz Generator" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="{request.url}" />
        <meta property="og:image" content="{request.url_for('rizz_image')}?text={rizz_line}" />
        <meta property="og:image:width" content="800" />
        <meta property="og:image:height" content="400" />
    </head>
    <body style="margin:0">
        <img src="{request.url_for('rizz_image')}?text={rizz_line}" width="100%" />
    </body>
    </html>
    """

@app.get("/image")
async def rizz_image(text: str):
    image_path = generate_image(text)
    return FileResponse(image_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
