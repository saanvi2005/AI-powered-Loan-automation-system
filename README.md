# NexusBank AI Loan Processing System

## Project Overview
NexusBank AI is an intelligent loan application system powered by AI and machine learning. It provides a seamless experience for customers to apply for loans through an AI-driven chat assistant. The system efficiently collects customer information, performs real-time underwriting, and supports document verification to accelerate loan processing.

## Features
- AI-powered conversational agent for collecting loan application data.
- Real-time underwriting analysis to determine eligibility.
- Secure document upload and verification (Aadhaar, PAN, Salary Slip).
- Multi-step progress tracking from application to approval.
- Responsive and user-friendly frontend interface.
- Built using FastAPI backend and a Local LLM integration.

## Technology Stack
- **Backend:** FastAPI, Python
- **Frontend:** HTML, CSS, JavaScript
- **AI Language Model:** Local LLM (llama3.2:3b)
- **OCR & Document Processing:** pytesseract, easyocr, opencv-python-headless
- **Other Libraries:** langchain, sqlalchemy, pydantic, uvicorn

## Backend Overview
The backend is built with FastAPI and provides the following key API routes:

- `/sales_agent/message` (POST): Main conversational endpoint for continuous interaction with the AI sales agent. Collects customer data such as name, age, salary, credit score, loan amount, and employment type.
- `/underwriter/analyze` (POST): Endpoint for underwriting logic (handled via agent integration).
- `/documents/verify` (POST): Handles document uploads and performs OCR/verification on Aadhaar, PAN, and Salary Slip documents.

The backend uses a custom LocalLLM wrapper over a local language model (llama3.2:3b) to generate agent responses based on user input. The system maintains session memory to track application progress and user data collection.

## Frontend Overview
The frontend is a single-page application built with HTML, CSS, and JavaScript, featuring:

- A landing page introducing NexusBank AI's premium loan processing.
- A chat interface integrated with the backend sales agent API for conversational loan applications.
- Sidebar navigation for accessing the chat, user profile, document uploads, and application status.
- Multi-step progress bar visualizing stages: Information collection, Underwriting, Documents, and Approval.
- Document upload panels supporting Aadhaar, PAN, and Salary Slip with verification feedback.
- Notifications and real-time status updates throughout the application process.

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js (for any frontend package management if needed, though current frontend is static)
- Access to GPU/CPU for running local LLM model (`llama3.2:3b`)

### Backend

1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate    # Linux/MacOS
   .\venv\Scripts\activate     # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI backend server with uvicorn:
   ```bash
   uvicorn backend.main:app --reload
   ```

### Frontend

- The frontend is served as static files by the FastAPI backend from the `/frontend` directory.
- Open a browser and navigate to `http://localhost:8000` after starting the backend server.
- Start your loan application through the friendly chat assistant.

## Usage & Workflow

1. Start at the landing page and initiate the loan application chat.
2. Provide loan application details step-by-step as guided by the AI assistant.
3. After completing information collection, receive underwriting eligibility feedback.
4. Upload required documents for verification with real-time status.
5. Submit all documents for final approval.
6. Receive final application status and next steps.

## Folder Structure

```
/
├── backend/                  # FastAPI backend application
│   ├── api/                  # API route definitions (sales agent, underwriter, documents)
│   ├── agents/               # AI agent logic (sales, underwriting)
│   ├── models/               # Data models and local LLM wrapper
│   ├── main.py               # FastAPI app entry point with routes setup
│   ├── memory.py             # Session memory module for tracking user data
│   ├── test.py               # Test scripts (if any)
│   └── __init__.py
├── frontend/                 # Frontend static files (HTML, CSS, JS)
│   ├── index.html
│   ├── style.css
│   └── script.js
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Notes
- The backend uses a local LLM for the conversational agent, ensure your machine meets requirements for running the model.
- Document verification uses OCR libraries (pytesseract, easyocr) to validate uploaded identity and salary documents.
- The system is designed to be extensible for real-world loan application workflows.



