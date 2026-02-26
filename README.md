# DSA Coding Challenge Application

An offline, desktop-based coding challenge application for conducting LeetCode-style DSA contests. Packaged as a standalone Windows `.exe` file.

## Features

- ✅ **Offline Operation**: No internet required
- ✅ **Dual Language Support**: Python and Java
- ✅ **10 DSA Problems**: Mix of Easy and Medium difficulty
- ✅ **Automated Judging**: Real-time code execution and verdict assignment
- ✅ **Performance Classification**: Gold/Silver/Bronze levels
- ✅ **Contest Timer**: Automatic time tracking and contest end
- ✅ **Standalone Executable**: No Python installation required

## System Requirements

### For Running the .exe
- **Operating System**: Windows 7 or later
- **For Java Support**: JDK 8 or later (optional, only if solving Java problems)
- **RAM**: 2GB minimum
- **Disk Space**: 200MB

### For Development
- Python 3.8 or later
- pip (Python package manager)
- JDK 8 or later (for Java problem support)

## Quick Start (Using .exe)

1. Download the `dist` folder containing `DSA_Challenge.exe`
2. Double-click `DSA_Challenge.exe` to launch
3. Register with your name, email, and select language (Python/Java)
4. Click "Start Contest" to begin
5. Solve problems and submit code
6. View results when contest ends

## Development Setup

### Installation

```bash
# Clone or download the project
cd dsa-challenge-app

# Install dependencies
pip install -r requirements.txt
```

### Running in Development Mode

```bash
# Run the application
python main.py
```

### Building the .exe

```bash
# Build executable
python build.py

# The .exe will be created in the dist/ folder
```

## Project Structure

```
dsa-challenge-app/
├── main.py                 # Application entry point
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── build.spec             # PyInstaller configuration
├── build.py               # Build script
├── backend/
│   ├── models.py          # Database models
│   ├── problem_loader.py  # Problem management
│   ├── executor.py        # Code execution engine
│   ├── judge.py           # Judging system
│   └── service.py         # Business logic
├── gui/
│   └── main_window.py     # GUI components
├── data/
│   ├── problems/          # Problem JSON files (1-10)
│   ├── contest.db         # SQLite database (created at runtime)
│   └── temp/              # Temporary execution files
└── tests/                 # Unit tests
```

## Usage Guide

### For Participants

1. **Registration**
   - Enter your name and email
   - Select programming language (Python or Java)
   - Click "Start Contest"

2. **Solving Problems**
   - Browse problems from the left panel
   - Read problem description
   - Write code in the editor
   - Click "Submit Code" to test

3. **Verdicts**
   - ✓ **Accepted**: All test cases passed (+10 marks)
   - ✗ **Wrong Answer**: Some test cases failed
   - ✗ **Compilation Error**: Code has syntax errors
   - ✗ **Runtime Error**: Code throws exception
   - ✗ **Time Limit Exceeded**: Code takes too long (>5 seconds)

4. **Ending Contest**
   - Contest auto-ends after 2 hours
   - Or click "End Contest" to finish early
   - View final score and performance level

### For Organizers

#### Adding New Problems

1. Create a new JSON file in `data/problems/` (e.g., `problem_11.json`)
2. Follow this structure:

```json
{
  "problem_id": 11,
  "title": "Problem Title",
  "difficulty": "Easy|Medium|Hard",
  "marks": 10,
  "description": "Problem description...",
  "function_signature": {
    "python": "def solution(params):",
    "java": "public ReturnType solution(ParamType params)"
  },
  "starter_code": {
    "python": "def solution(params):\n    pass",
    "java": "class Solution {\n    public ReturnType solution(ParamType params) {\n        return null;\n    }\n}"
  },
  "test_cases": [
    {
      "input": {"param": "value"},
      "expected_output": "expected_result"
    }
  ]
}
```

3. Update `config.py` to change `TOTAL_PROBLEMS` if needed
4. Rebuild the .exe: `python build.py`

#### Customizing Contest Settings

Edit `config.py`:

```python
CONTEST_DURATION = 7200  # Contest duration in seconds (2 hours)
EXECUTION_TIMEOUT = 5    # Code execution timeout (5 seconds)
GOLD_THRESHOLD = 80      # Minimum score for Gold level
SILVER_THRESHOLD = 50    # Minimum score for Silver level
```

## Troubleshooting

### Application won't start
- Ensure you're running on Windows 7 or later
- Check if port 5000 is available (used by backend)
- Try running as administrator

### Java problems not working
- Ensure JDK 8 or later is installed
- The app automatically detects JDK in standard paths (`C:\Program Files\Java\...`)
- If using a custom path, ensure `javac` is in your system PATH

### Code execution fails
- Check if code has syntax errors
- Ensure function name matches `solution`
- Verify input/output format matches problem requirements

### Database errors
- Delete `data/contest.db` and restart application
- Ensure `data` folder has write permissions

## Performance Levels

- **Gold**: Score ≥ 80 (8+ problems solved)
- **Silver**: Score 50-79 (5-7 problems solved)
- **Bronze**: Score < 50 (< 5 problems solved)

## Technical Details

### Architecture
- **Frontend**: HTML/CSS/JS (rendered via `pywebview`)
- **Backend**: Flask (Python)
- **Desktop Container**: PyWebview (Edge/Chromium engine)

### Code Execution
- Python code executed via `subprocess` with timeout
- Java code executed via `subprocess` with robust path detection
- In-place modification support for Java (`void` methods)
- All executions sandboxed with 5-second timeout

### Judging
- Function-based testing (similar to LeetCode)
- Hidden test cases not visible to participants
- Exact output matching with whitespace normalization
- Support for multiple arguments and distinct types

### Database
- SQLite for local data storage
- Tracks participants, submissions, and results
- Persists between application sessions

## License

This project is created for educational purposes for college coding contests.

## Support

For issues or questions, contact your club organizers.

---

**Built with**: Python, Flask, PyWebview, SQLAlchemy, PyInstaller
