### 📧 Personalized AI Email Assistant

## 🟠 Overview

The **AI Email Assistant** simplifies email management by automating the categorization, summarization, and prioritization of emails. 
It is designed for students and professionals who receive many emails daily, helping them stay organized and focused on important messages.

Leveraging **Generative AI** and **Retrieval-Augmented Generation (RAG)** techniques, this assistant personalizes email management based on user preferences, making it adaptable without manual effort.

---

## 🎯 Project Intent

Managing a cluttered inbox is a common challenge. This assistant addresses the issue by filtering, categorizing, and summarizing emails intelligently, allowing users to save time and reduce distractions.

Key benefits:
- Reduce inbox clutter
- Prioritize important emails
- Summarize content quickly
- Adapt to individual preferences

---

## ✅ Features

### Personalization
- Users can set preferences that guide email categorization and handling.
- AI learns from user feedback using advanced techniques.

### Email Organization
- Automatically categorizes emails into relevant groups.

### Email Summarization
- Uses AI models to summarize content for faster review.

### Email Filtering
- Filters out irrelevant messages using AI-powered algorithms.

---

## ⚙ How It Works

1. **Email Input**  
   Emails can be added manually, where they are processed and classified.

2. **AI Processing**  
   Emails are classified using AI models like **Gemini 1.5 Pro**.

3. **Data Storage**  
   Emails and their classifications are saved locally and can be reviewed in an organized format.

4. **Prioritization**  
   Based on classification, emails are marked and prioritized accordingly.

---

## 📂 Project Structure
Email_ai_assistant/
├── Backend/ # FastAPI backend
│ ├── main.py # API endpoints
│ ├── models.py # Pydantic data models
│ ├── database.py # Local database handler
│ ├── ai_classifier.py # AI-based classification logic
│ ├── gmail_fetcher.py # Gmail API client
│ ├── priority_queue.py # Email queue management
│ ├── .env # Environment variables
│ └── venv/ # Python virtual environment
├── frontend/ # React + Tailwind CSS frontend
│ ├── src/
│ │ ├── App.jsx
│ │ ├── index.css
│ │ ├── index.jsx
│ │ ├── pages/
│ │ │ └── Dashboard.jsx
│ │ └── components/
│ │ └── EmailCard.jsx
│ ├── .env # Environment variables
│ ├── tailwind.config.js # Tailwind configuration
│ └── vite.config.js # Vite configuration
├── README.md # Project documentation
└── requirements.txt # Python dependencies

## ⚙ Requirements

### Backend
- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- Google APIs (optional Gmail integration)

### Frontend
- Node.js 22.x+
- npm 10.x+
- Vite
- React
- Tailwind CSS

## install additional requirments
 - pip install -r requirements.txt

## Future Upgrades
In upcoming versions, the assistant will integrate with Gmail using the Gmail API and OAuth 2.0 for seamless email management.
Steps planned:
 - Create a project in the Google Cloud Console
 - Enable Gmail API for the project.

 - Create OAuth 2.0 credentials and download credentials.json.
 - Place credentials.json in the project directory for automated email access.
These upgrades will enable automatic email fetching, synchronization, and more advanced features.

## Future Features
 - Intuitive graphical user interface (GUI)
 - Spam and advertisement filtering
 - Multi-account support
 - Integration with other email services


## Screenshots
<img width="1920" height="1080" alt="Screenshot 2025-09-06 144446" src="https://github.com/user-attachments/assets/f8caf4bb-0420-4ad2-b685-ea43cdb8aa67" />
<img width="1053" height="865" alt="Screenshot 2025-09-06 144459" src="https://github.com/user-attachments/assets/36ce38a5-fb9a-4bde-8983-080e594db320" />
<img width="1920" height="719" alt="Screenshot 2025-09-06 144547" src="https://github.com/user-attachments/assets/06345e2b-8fcb-4018-8bd6-b58c572dd1c8" />
<img width="1920" height="792" alt="Screenshot 2025-09-06 144625" src="https://github.com/user-attachments/assets/2d58a733-9ef4-4534-87eb-430029ca9421" />



