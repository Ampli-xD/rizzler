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
        font = ImageFont.truetype("arial.ttf", 100)  # Increased font size to 60
    except:
        font = ImageFont.load_default()  # Fallback font

    draw = ImageDraw.Draw(img)
    wrapped_text = textwrap.fill(text, width=20)  # Adjust wrapping for larger text

    # Calculate text position for multiline text
    lines = wrapped_text.split('\n')
    total_height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)
    y = (400 - total_height) // 2  # Centering text vertically

    for line in lines:
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (800 - text_width) // 2  # Centering text horizontally
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += text_height + 5  # Adjust line spacing

    image_path = "rizz.png"
    img.save(image_path)
    return image_path

@app.get("/", response_class=HTMLResponse)
async def generate_rizz(request: Request):
    topic = request.query_params.get("topic", "random")  # Fix query param retrieval

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": f"Generate a {topic} pickup line. Keep it under 20 words. Say nothing more, nothing less—only the pickup line!"}],
            model="llama3-70b-8192",
        )
        
        rizz_line = chat_completion.choices[0].message.content if chat_completion.choices else "You're looking fine today! 😉"
    except Exception as e:
        print(f"Error fetching from Groq API: {e}")
        rizz_line = "You're looking fine today! 😉"  # Fallback text

    return f"""
    <!DOCTYPE html>
    <html prefix="og: https://ogp.me/ns#">
    <head>
        <meta property="og:title" content="Generated Rizz" />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="{request.url}" />
        <meta property="og:image" content="{request.url_for('rizz_image')}?text={rizz_line.replace(' ', '+')}" />
        <meta property="og:image:width" content="800" />
        <meta property="og:image:height" content="400" />
    </head>
    <body style="margin:0;background:#000">
        <img src="{request.url_for('rizz_image')}?text={rizz_line.replace(' ', '+')}" width="100%" />
    </body>
    </html>
    """

@app.get("/image")
async def rizz_image(text: str):
    decoded_text = text.replace('+', ' ')
    image_path = generate_image(decoded_text)
    
    return FileResponse(image_path, media_type="image/png")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
