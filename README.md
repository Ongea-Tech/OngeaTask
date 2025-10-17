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

5. **Run the application (only the app)**
```bash
flask run
```
The app will be running at http://127.0.0.1:5000

---

#### Using Tailwind CSS & Running the app  (dev & prod)

#### 1) Install JS packages (once)
```bash
npm install
```

#### 2) Start development
Use two (optionally three) terminals.

#### Terminal 1: Tailwind watcher (builds CSS on save)

```bash
npm run dev:css
```

#### Terminal 2: Flask app (dev)

```bash
npm run flask
```

#### Terminal 3: Optional live reload proxy

```bash
npm run serve
```

#### 3) Build for production
Before deploying (Render), build once:

```bash
npm run build:css
```

---

**Branching Rules**

To keep the project organized and maintain clean code, please follow these branch rules when contributing:

- The **`main`** branch is the production-ready branch. Do not commit or push directly to `main`.
- All new features or bug fixes should be developed in a **feature branch** created from `main`.  
  Your branch name should start with **your first name**, followed by a short description.

- **Branch naming convention:**

   yourname/feature-short-description

   yourname/bugfix-short-description

   **Examples:**

   mike/feature-add-task-form

   molly/bugfix-fix-task-deletion

- After completing your changes, open a **Pull Request** into `main`.  
  Fill out the PR template. Make sure your code is tested and clean before submitting. 

- All Pull Requests must be **reviewed and approved** by at least one other contributor before merging into `main`.

- Regularly **pull from `main`** into your branch to stay up-to-date:

  ```bash
  git pull origin main
  ```
---


**Start date:** May 4th, 2025