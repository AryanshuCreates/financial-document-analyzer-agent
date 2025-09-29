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

pip install -r requirements.txt
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

Usage
Register as Admin or Viewer.

Log in to the application.

Admin users: Can upload PDFs and view all documents.

Viewer users: Can only view dashboards and analyses.

Click View Results to see detailed analysis, including CrewAI output and local summary.

Folder Structure
bash
Copy code
financial-document-analyzer-agent/
├─ backend/         # FastAPI backend code
├─ frontend/        # React + Tailwind frontend
├─ README.md        # Project overview & setup
API Endpoints
Method	Endpoint	Description
POST	/register	Register a new user
POST	/login	Authenticate and receive JWT token
POST	/analyze	Upload PDF for analysis
GET	/documents	Get list of uploaded documents
GET	/analysis/{document_id}	Get analysis results
DELETE	/documents/{document_id}	Delete a document and analysis
GET	/health	Health check endpoint
```
