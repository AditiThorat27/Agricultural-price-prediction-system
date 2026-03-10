# Full-Stack Application Setup & Walkthrough

This document outlines the steps to connect this project to a GitHub repository, clone it, and run it locally.

## Prerequisite: Connecting to a GitHub Repository (Initial Setup)

If you are setting this up for the first time:

1. Create a new repository on your GitHub account.
2. Run the following commands:
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

## Cloning the Repository

To work on this project locally after the initial setup:

1. Clone the repository to your local machine:
   ```bash
   git clone <your-github-repo-url>
   cd PROJECT
   ```

2. Ensure you are on the main branch:
   ```bash
   git checkout main
   ```

## Running the Project Locally

The application uses an architecture consisting of a React frontend, Node.js backend, and a FastAPI model service. 

### Option 1: Using Docker Compose (Recommended)

Make sure you have Docker installed and running.

```bash
docker-compose up --build
```
This will containerize and run the entire stack at once.

### Option 2: Running Services Individually

If you prefer to run services manually for local development:

**1. Frontend (React/Vite)**
```bash
cd frontend
npm install
npm run dev
```

**2. Backend (Node.js)**
```bash
cd backend
npm install
npm run dev
```

**3. Model Service (Python/FastAPI)**
```bash
cd model_service
# Create and activate a Virtual Environment
python -m venv venv
venv\Scripts\activate # On Windows
# pip install -r requirements.txt
uvicorn main:app --reload
```

## Repository Structure

The base repository structure has been designed to securely separate system concerns:
- `backend/`: Node.js API that interfaces with the DB and Frontend.
- `db/`: Database configuration (e.g., PostgreSQL/Supabase scripts).
- `frontend/`: React components and UI code.
- `model_service/`: Standalone FastAPI service serving machine learning models.
- `models/`: Weights or serialization files for AI models.
