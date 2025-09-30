# Financial Document Analyzer

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CrewAI](https://img.shields.io/badge/CrewAI-v0.130.0-orange)

A full-stack application that allows users to upload financial documents (PDFs), analyzes them using **CrewAI**, and provides detailed insights. Includes authentication, role-based access, database integration, caching, and monitoring.

---

## Demo

You can view a demonstration of the application here:  
[YouTube Demo](https://youtu.be/zmgaCEhQMqY)

---

## Features

- **Full-stack solution**: React frontend + FastAPI backend
- **Authentication & Authorization**: Role-based access for Admin and Viewer
- **Document Upload & Analysis**: Upload financial PDFs and get automated summaries
- **Background Analysis**: Uses CrewAI for automated insights
- **Edge Case Handling**: Comprehensive validation and error handling
- **Production-Ready Features**: MongoDB integration, CORS, logging, and monitoring

---

## Tech Stack

- **Backend:** FastAPI, Pydantic v2, MongoDB, Motor, CrewAI
- **Frontend:** React, Vite, Tailwind CSS
- **Authentication:** JWT + HTTPBearer
- **Other Tools:** Python asyncio, aiofiles, dotenv

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

| Variable          | Description                                               |
| ----------------- | --------------------------------------------------------- |
| `MONGO_URI`       | MongoDB connection string                                 |
| `SECRET_KEY`      | JWT secret key for authentication                         |
| `UPLOAD_DIR`      | Directory to save uploaded PDFs                           |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed frontend origins for CORS |

---

## Installation & Setup

### Clone the repository

```bash
git clone https://github.com/AryanshuCreates/financial-document-analyzer-agent.git
cd financial-document-analyzer-agent
Backend setup
bash
Copy code
cd backend
python -m venv venv
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r newRequirements.txt
Frontend setup
bash
Copy code
cd ../frontend
npm install
npm run dev
Run the backend server
bash
Copy code
cd ../backend
uvicorn main:app --reload
Open the frontend at: http://localhost:5173

```

---

## Google Cloud Setup (Vertex AI)

To use CrewAI with Vertex AI for document analysis, you’ll need a Google Cloud project with the right permissions.

### 1. Create a GCP Project
- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Click **Create Project** and give it a name (e.g., `financial-doc-analyzer`).
- Note the **Project ID**.

### 2. Enable Vertex AI API
- In the Cloud Console, navigate to **APIs & Services > Library**.
- Search for **Vertex AI API** and click **Enable**.

### 3. Set Up Service Account
- Go to **IAM & Admin > Service Accounts**.
- Create a new service account (e.g., `vertexai-analyzer`).
- Assign the following roles:
  - `Vertex AI Administrator`
  - `Service Account User`
- Generate a JSON key and download it (this will be used for authentication).

### 4. Authenticate Locally
Set the environment variable to point to your service account key file:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```
### On Windows (PowerShell):
```
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\service-account.json"

```
Environment Variables (.env)

Create a .env file in the backend/ directory with the following:
``` env
MONGO_URI = mongodb://localhost:27017/financial_analyzer
DB_NAME=financial_analyzer
# Security
ACCESS_TOKEN_EXPIRE_SECONDS=86400
JWT_SECRET = 
GEMINI_API_KEY = 
GEMINI_MODEL=gemini-2.0-flash-exp
# Application
ALLOWED_ORIGINS=https://yourdomain.com
UPLOAD_DIR=data
MAX_FILE_SIZE_MB=10
# Logging
LOG_LEVEL=INFO
```


## Usage

1. **Register** as Admin or Viewer.
2. **Log in** to the application.
3. **Admin users**: Can upload PDFs and view all documents.
4. **Viewer users**: Can only view dashboards and analyses.
5. Click **View Results** to see detailed analysis, including CrewAI output and local summary.

---

## Folder Structure

```bash
financial-document-analyzer-agent/
├─ backend/         # FastAPI backend code
├─ frontend/        # React + Tailwind frontend
├─ README.md        # Project overview & setup
```

API Endpoints
Method	Endpoint	Description
POST	/register	Register a new user
POST	/login	Authenticate and receive JWT token
POST	/analyze	Upload PDF for analysis
GET	/documents	Get list of uploaded documents
GET	/analysis/{document_id}	Get analysis results
DELETE	/documents/{document_id}	Delete a document and analysis
GET	/health	Health check endpoint

