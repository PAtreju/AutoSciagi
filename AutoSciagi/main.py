from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai import OpenAI
import os
from pathlib import Path
import datetime
from dotenv import load_dotenv

app = FastAPI()

Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)
briefs_dir = Path("./static/briefs")
briefs_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


briefs = []
files = os.listdir(briefs_dir)
for file in files:
    if file.endswith(".html"):
        file_path = briefs_dir / file
        with open(file_path, "r") as f:
            content = f.read()
            title_start = content.find("<title>") + len("<title>")
            title_end = content.find("</title>")
            title = content[title_start:title_end]
            briefs.append({
                "title": title,
                "filename": f"/static/briefs/{file}",
                "date": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
            briefs.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%Y-%m-%d %H:%M"), reverse=True)

@app.get("/", response_class=HTMLResponse)
async def get_main(request: Request):
    return templates.TemplateResponse("list.html", {"request": request, "briefs": briefs})

@app.get("/panel", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "briefs": briefs})
@app.post("/create-brief", response_class=HTMLResponse)
async def create_brief(request: Request, theme: str = Form(...), desc: str = Form(...)):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates cheat sheets. Content of your response will be put in html div so include html tags."},
                {"role": "user", "content": f"Napisz dokładną i rozwiniętą ściąge na temat: {theme}." + (f"Dodatkowe informajce: {desc}" if desc != "" else "")}
            ]

        )
        brief_content = response.choices[0].message.content

        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{theme.replace(' ', '_')}_{timestamp}"
        html_filename = f"{filename}.html"
        file_path = briefs_dir / html_filename

        nl ='\n'
        brief_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sciaga: {theme}</title>
            <link rel="stylesheet" href="/static/style.css">
        </head>
        <body>
            <div class="content">
                {brief_content}
            </div>
            <p><a href="/">Back to index</a></p>
        </body>
        </html>
        """

        with open(file_path, "w") as f:
            f.write(brief_html)

        briefs.append({
            "title": theme,
            "filename": f"/static/briefs/{html_filename}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        })


        return templates.TemplateResponse("index.html", {"request": request, "briefs": briefs})

    except Exception as e:
        print(f"Full error: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating brief: {str(e)}")
