STOP! READ THIS FIRST.

Here is your exact Step-by-Step checklist to run the new Crash-Proof System.
Complete these steps in order.

==================================================
PHASE 1: FIREBASE SETUP (Do this on the website)
==================================================

1. Go to https://console.firebase.google.com/
2. Click "Add Project" -> Name it "dsa-challenge-2024" (or similar).
3. Disable Google Analytics (simpler).
4. Once created, click "Build" on the left sidebar:
   a. Click "Firestore Database" -> "Create Database" -> select "Start in Test Mode" -> Choose a location close to you.
   b. Click "Authentication" -> "Get Started" -> "Sign-in method" -> Enable "Anonymous".

==================================================
PHASE 2: GET YOUR KEYS (Crucial)
==================================================

KEY #1: The Service Account (For worker.py)
1. In Firebase Console, click the "Gear" icon (Project Settings).
2. Go to "Service accounts" tab.
3. Click "Generate new private key".
4. A file will download. RENAME it to "serviceAccountKey.json".
5. MOVE this file into this folder: `c:\Users\DELL\OneDrive\Desktop\Problem Solving - Copy\dsa-challenge-app\`

KEY #2: The Web Config (For contest.html)
1. In Project Settings, scroll down to "Your apps".
2. Click the `</>` icon (Web).
3. Register app (name it "Contest App").
4. You will see a strict `const firebaseConfig = { ... };`.
5. COPY that minimal config object.
6. OPEN `templates/contest.html` in your editor.
7. PASTE it over the placeholder on Line 20-27.

==================================================
PHASE 3: INSTALL & INIT
==================================================

1. Open your terminal in the `dsa-challenge-app` folder.
2. Install the new requirements:
   pip install -r requirements.txt

3. Initialize the Database (Run this ONCE):
   python init_firestore.py
   (If it says "Database Initialized!", you are good).

==================================================
PHASE 4: RUN IT (The Swarm)
==================================================

Terminal 1 (The Website - Safe & Fast):
   python app.py
   -> This will show the UI. It will NEVER crash now.

Terminal 2 (The Grading Worker):
   python worker.py
   -> This is your "Judge". It connects to Firebase.
   -> "waiting for jobs..."

TEST IT:
1. Go to http://localhost:5000
2. Submit code.
3. Watch Terminal 2 say "claiming..." then "Processing...".
4. Watch Browser update automatically.

Done. You are ready for 250 students.
