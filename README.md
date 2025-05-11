# AutoSciagi
*Generate concise, AI-powered cheat sheets for any academic topic.*

---

## Table of Contents
1. [Features](#features)  
2. [Screenshots](#screenshots)  
3. [Installation](#installation)  
4. [Usage](#usage)  
5. [Project Structure](#project-structure)  
6. [Technology Stack](#technology-stack)  
7. [Requirements](#requirements)

---

## Features
- **AI-generated notes** — create detailed study briefs on any subject with OpenAI GPT models  
- **Cheat-sheet library** — view a list of all previously generated sheets  
- **Responsive design** — seamless experience on desktop and mobile  
- **Downloadable content** — save cheat sheets for offline study  
- **Modern UI** — smooth animations and a clean, purple-gradient theme  

---

## Screenshots
The application includes three primary views:

1. **Landing Page** — animated “SHROOM DEV” logo  
2. **List View** — browse existing cheat sheets  
3. **Control Panel** — generate new cheat sheets  
---

## Installation
1. **Clone the repository**  
   ```bash
   git clone https://github.com/PAtreju/AutoSciagi
   cd AutoSciagi
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python -m venv env
   source env/bin/activate      # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your OpenAI API key**  
   - Create a `.env` file in the project root  
   - Paste:  
     ```text
     OPENAI_API_KEY=your_openai_api_key_here
     ```

---

## Usage
1. **Start the server**  
   ```bash
   uvicorn main:app --reload
   ```

2. **Open your browser**  
   - `http://localhost:8000/` — Landing page  
   - `http://localhost:8000/panel` — Control panel (generate cheat sheets)  
   - `http://localhost:8000/sciagi` — List of cheat sheets  

3. **Generate a new cheat sheet**  
   - Go to **/panel**  
   - Enter a lesson theme (and optional description)  
   - Click **Generate Brief**  
   - After processing, your cheat sheet appears in the list  

---

## Project Structure
``` 
main.py              # FastAPI app with routes
templates/
├─ main.html         # Landing page
├─ index.html        # Control panel
└─ list.html         # Cheat-sheet list view
static/
├─ style.css         # Global styles
├─ style_main.css    # Landing styles
├─ style_sciaga.css  # List & panel styles
└─ images/           # SVG logo & favicons
``` 

---

## Technology Stack
- **FastAPI** — modern Python web framework  
- **Jinja2** — HTML templating  
- **OpenAI API** — content generation  
- **HTML / CSS** — responsive frontend  
- **python-dotenv** — environment variable management  

---

## Requirements
See `requirements.txt` for the complete list of Python dependencies.
