from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from openai import OpenAI
import os
from pathlib import Path
import datetime
from dotenv import load_dotenv
from auth import (
    authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES,
    User, fake_users_db
)
from datetime import timedelta

app = FastAPI(docs_url=None, redoc_url=None)

Path("static").mkdir(exist_ok=True)
Path("templates").mkdir(exist_ok=True)
briefs_dir = Path("./static/briefs")
briefs_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_briefs():
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
                    "pathname": f"/sciagi/{file}",
                    "date": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                })
                briefs.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%Y-%m-%d %H:%M"), reverse=True)
    return briefs

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/sciagi", response_class=HTMLResponse)
async def get_main(request: Request):
    briefs = generate_briefs()
    return templates.TemplateResponse("list.html", {"request": request, "briefs": briefs})

@app.get("/sciagi/{filename}", response_class=HTMLResponse)
async def get_brief(request: Request, filename: str):
    file_path = briefs_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# New login routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid username or password"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/panel", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=1800,  # 30 minutes
        expires=1800,
    )
    
    return response

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="access_token")
    return response

# Protected routes
@app.get("/panel", response_class=HTMLResponse)
async def get_panel(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    briefs = generate_briefs()
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "briefs": briefs, "user": user}
    )

@app.post("/create-brief", response_class=HTMLResponse)
async def create_brief(
    request: Request, 
    theme: str = Form(...), 
    desc: str = Form(...)
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
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

        nl = '\n'
        brief_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sciaga: {theme}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="/static/style.css">
            <link rel="apple-touch-icon" sizes="180x180" href="../static/images/favicon_io/apple-touch-icon.png">
            <link rel="icon" type="image/png" sizes="32x32" href="../static/images/favicon_io/favicon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="../static/images/favicon_io/favicon-16x16.png">
            <link rel="manifest" href="../static/images/favicon_io/site.webmanifest">
        </head>
        <body>
            <div class="content">
                {brief_content}
            </div>
            <p class="go_back"><a href="/sciagi">Back to index</a></p>
        </body>
        </html>
        """

        with open(file_path, "w") as f:
            f.write(brief_html)

        briefs = generate_briefs()

        return RedirectResponse(url="/panel", status_code=303)

    except Exception as e:
        print(f"Full error: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating brief: {str(e)}")