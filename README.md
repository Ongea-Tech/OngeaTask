# Ongea Task

**Ongea Task** is a simple To-Do List web application created by young developers from **Ongea Tech**  as a learning project to practice full-stack development.

The app allows users to add, view, and manage tasks in a clean and minimal interface — while learning how to build scalable web applications using modern technologies.

---

**Tech Stack**

- **Frontend**: HTML, CSS, Vanilla JavaScript  
- **Framework**: Flask (Python)  
- **Database**: MySQL  
- **Hosting**: Render

---

**Getting Started**

Follow these instructions to set up the project on your local machine for development and testing.

1. **Create a project folder and virtual environment (before cloning)**

```bash
mkdir OngeaTask
cd OngeaTask
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

2. **Clone the repository**
```bash
git clone https://github.com/Ongea-Tech/OngeaTask.git 
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a .env file in the root folder and add:
```bash
FLASK_APP=run.py
FLASK_ENV=development
```

5. **Run the application**
```bash
flask run
```
The app will be running at http://127.0.0.1:5000

**Start date:** May 4th, 2025