# 🚀 Deployment & Build Guide

Follow these steps to go live.

## Part 1: Deploy to Cloud (Render)

1.  **GitHub Setup**:
    *   Create a NEW repository on GitHub (e.g., `dsa-contest-2024`).
    *   Run these commands in your `dsa-challenge-app` terminal:
        ```bash
        git init
        git add .
        git commit -m "Final Deploy"
        git branch -M main
        git remote add origin https://github.com/YOUR_USERNAME/dsa-contest-2024.git
        git push -u origin main
        ```

2.  **Render Setup**:
    *   Go to [dashboard.render.com](https://dashboard.render.com).
    *   Click **New +** -> **Web Service**.
    *   Connect your new GitHub repo.
    *   Scroll down to settings:
        *   **Name**: `atc-dsa-app` (or similar)
        *   **Build Command**: `pip install -r requirements.txt`
        *   **Start Command**: `gunicorn app:app`
        *   **Plan**: Free
    *   Click **Create Web Service**.

3.  **Get URL**:
    *   Wait ~2 minutes. Render will show "Live".
    *   Copy the URL near the top (e.g., `https://atc-dsa-app.onrender.com`).

---

## Part 2: Build the Client App (EXE)

1.  **Update Config**:
    *   Open `client_launcher.py`.
    *   Paste your Render URL into line 20: `BACKEND_URL = '...'`
2.  **Build**:
    *   Run this command in terminal:
        ```bash
        pyinstaller --noconfirm --onefile --windowed --name "DSA_Contest_Client" --add-data "templates;templates" --add-data "static;static" client_launcher.py
        ```
3.  **Distribute**:
    *   Go to `dist` folder.
    *   Send `DSA_Contest_Client.exe` to students.
