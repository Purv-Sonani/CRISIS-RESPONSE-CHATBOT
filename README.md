# 🚑 Crisis Response Chatbot

An automated emergency assistance chatbot designed to guide users through critical situations (Earthquakes, Floods, Fires) when human operators are unavailable. It uses **Rasa** for natural language understanding and **React** for a responsive, accessible frontend.

![Rasa](https://img.shields.io/badge/Rasa-3.x-purple) ![React](https://img.shields.io/badge/React-18-blue)

---

## 🏗️ Architecture

- **Backend:** Rasa Open Source (NLU & Core) + Rasa Action Server (Python)
- **Frontend:** React (Vite)
- **Deployment:**
  - **Backend:** Hugging Face Spaces (Dockerized)
  - **Frontend:** GitHub Pages

---

## 🚀 Quick Start (Docker)

The easiest way to run the entire system locally is using Docker Compose.

### Prerequisites

- Docker & Docker Compose installed.

### Steps

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/Purv-Sonani/CRISIS-RESPONSE-CHATBOT.git](https://github.com/Purv-Sonani/CRISIS-RESPONSE-CHATBOT.git)
    cd CRISIS-RESPONSE-CHATBOT
    ```

2.  **Run the application:**

    ```bash
    docker-compose up --build
    ```

3.  **Access the App:**
    - **Frontend:** `http://localhost:5173`
    - **Rasa Server:** `http://localhost:5005`
    - **Action Server:** `http://localhost:5055`

---

## 💻 Manual Setup (Local Development)

If you prefer running services individually without Docker.

### 1. Backend Setup (Rasa)

**Prerequisites:** Python 3.10

1.  Navigate to the backend:
    ```bash
    cd backend
    ```
2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install rasa==3.6.21
    ```
4.  Train the model:
    ```bash
    rasa train
    ```
5.  **Run the Action Server** (Terminal 1):
    ```bash
    rasa run actions
    ```
6.  **Run the Rasa Core Server** (Terminal 2):
    ```bash
    rasa run --enable-api --cors "*"
    ```

### 2. Frontend Setup (React)

**Prerequisites:** Node.js 18+

1.  Navigate to the frontend:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  **Configure API URL:**
    - Open `src/rasaApi.js`.
    - Ensure the URL points to localhost:
      ```javascript
      const RASA_URL = "http://localhost:5005/webhooks/rest/webhook";
      ```
4.  Run the development server:
    ```bash
    npm run dev
    ```
5.  Open `http://localhost:5173` in your browser.

---

## ☁️ Deployment

### Backend (Hugging Face Spaces)

The backend is deployed as a single Docker container running both Rasa Core and the Action Server.

1.  Create a **Docker** Space on Hugging Face.
2.  Push the backend code using Git Subtree:
    ```bash
    git remote add huggingface [https://huggingface.co/spaces/YOUR_HF_USERNAME/YOUR_SPACE_NAME](https://huggingface.co/spaces/YOUR_HF_USERNAME/YOUR_SPACE_NAME)
    git subtree push --prefix backend huggingface main
    ```
    _(Note: Requires a `README.md` with YAML metadata in the backend folder)_.

### Frontend (GitHub Pages)

The frontend is a static React site hosted on GitHub Pages.

1.  Update `frontend/src/rasaApi.js` to point to the live Hugging Face URL:
    ```javascript
    const RASA_URL = "[https://YOUR-SPACE-NAME.hf.space/webhooks/rest/webhook](https://YOUR-SPACE-NAME.hf.space/webhooks/rest/webhook)";
    ```
2.  Deploy via npm script:
    ```bash
    cd frontend
    npm run deploy
    ```

---

## 📁 Project Structure

```text
crisis-response-chatbot/
├── backend/                # Rasa Project
│   ├── actions/            # Custom Python Actions
│   ├── data/               # NLU training data & Stories
│   ├── domain.yml          # Chatbot domain configuration
│   ├── config.yml          # NLU pipeline config
│   ├── Dockerfile          # Backend Docker setup
│   ├── start_services.sh   # Script to run Core + Actions
│   └── README.md           # HF Space Metadata
│
├── frontend/               # React Project
│   ├── src/
│   │   ├── components/     # ChatWindow, Header, SheltersList
│   │   ├── rasaApi.js      # API Utility
│   │   └── App.jsx
│   └── vite.config.js
│
└── docker-compose.yml      # Orchestration for local run
```
