let currentProblemId = null;
let timerInterval = null;
let fullscreenEnabled = false;
let violations = 0;
const MAX_VIOLATIONS = 3;

// Enable fullscreen and anti-cheating on page load
window.addEventListener('DOMContentLoaded', async () => {
    // Load data in background
    await loadProblems();

    // Setup overlay button
    const startBtn = document.getElementById('enterFullscreenBtn');

    // FIREBASE INIT PARTICIPANT
    if (typeof db !== 'undefined') {
        const pRef = db.collection('participants').doc(PARTICIPANT_ID);
        pRef.get().then(doc => {
            if (!doc.exists) {
                pRef.set({
                    name: PARTICIPANT_NAME,
                    email: PARTICIPANT_EMAIL,
                    score: 0,
                    time_taken: 0,
                    solved: []
                });
            }
        });

        // Listen for Score & Status Updates
        pRef.onSnapshot(doc => {
            const data = doc.data();
            if (data) {
                // Sync Score
                document.getElementById('score').textContent = `Score: ${data.score || 0}/145`;

                // Sync Violations
                if (data.violations !== undefined) {
                    violations = data.violations;
                    document.getElementById('topViolations').textContent = violations;
                    document.getElementById('violationCount').textContent = violations;
                }

                // Sync Status & Time
                if (data.status === 'DISQUALIFIED') {
                    if (fullscreenEnabled) {
                        fullscreenEnabled = false;
                        document.getElementById('disqualifyModal').style.display = 'flex';
                        setTimeout(() => showCompletionMessage(), 3000);
                    }
                } else if (data.status === 'COMPLETED') {
                    showCompletionMessage();
                }

                if (data.start_time) {
                    // Handle Firestore Timestamp
                    window.contestStartTime = data.start_time.toDate ? data.start_time.toDate() : new Date(data.start_time);
                }

                // Sync Solved Problems
                if (data.solved) {
                    data.solved.forEach(pid => {
                        const item = document.querySelector(`.problem-item:nth-child(${pid})`);
                        if (item && !item.classList.contains('solved')) {
                            item.classList.add('solved');
                            const infoDiv = item.querySelector('.problem-info');
                            if (infoDiv && !infoDiv.querySelector('.solved-icon')) {
                                const icon = document.createElement('span');
                                icon.className = 'solved-icon';
                                icon.textContent = '✓';
                                infoDiv.insertBefore(icon, infoDiv.firstChild);
                            }
                        }
                    });
                }
            }
        });
    }

    startBtn.addEventListener('click', () => {
        enableFullscreen();
        document.getElementById('startOverlay').style.display = 'none';
        startTimer();
        setupAntiCheating();

        // SYNC START TO FIRESTORE
        if (typeof db !== 'undefined') {
            // Only set start_time if it doesn't verify exist locally (synced from DB)
            // This prevents resetting the timer on page refresh
            if (!window.contestStartTime) {
                db.collection('participants').doc(PARTICIPANT_ID).update({
                    status: 'ACTIVE',
                    start_time: firebase.firestore.FieldValue.serverTimestamp()
                }).catch(e => console.error("FS Start Sync Error", e));
            } else {
                console.log("Resuming contest, preserving original start time.");
            }
        }

        // Start strict fullscreen check loop
        setInterval(checkFullscreenState, 500);
    });
});

// Strict check for blocking overlay
function checkFullscreenState() {
    // Only if contest is running and we are not disqualified
    const blocker = document.getElementById('fullscreenBlocker');
    if (!blocker) return;

    if (!document.fullscreenElement && fullscreenEnabled && document.getElementById('disqualifyModal').style.display === 'none') {
        blocker.style.display = 'flex';
    } else {
        blocker.style.display = 'none';
    }
}

// Enable fullscreen
function enableFullscreen() {
    if (document.documentElement.requestFullscreen) {
        document.documentElement.requestFullscreen().then(() => {
            fullscreenEnabled = true;
            console.log('Fullscreen enabled, anti-cheating active');
            // Force native window fullscreen if available
            if (window.pywebview) {
                window.pywebview.api.set_fullscreen(true);
            }
        }).catch(err => {
            console.log('Fullscreen request failed:', err);
            // Enable anti-cheating anyway
            fullscreenEnabled = true;
            // Try native fullscreen even if browser API failed
            if (window.pywebview) {
                window.pywebview.api.set_fullscreen(true);
            }
        });
    } else {
        // Browser doesn't support fullscreen, but enable anti-cheating anyway
        fullscreenEnabled = true;
        console.log('Fullscreen not supported, but anti-cheating enabled');
    }
}

// Anti-cheating system
function setupAntiCheating() {
    console.log('Setting up anti-cheating system');

    // Detect window blur (switching away)
    window.addEventListener('blur', () => {
        console.log('Window blur detected, fullscreenEnabled:', fullscreenEnabled);
        if (fullscreenEnabled) {
            handleViolation();
        }
    });

    // Detect fullscreen exit
    document.addEventListener('fullscreenchange', () => {
        console.log('Fullscreen change, element:', document.fullscreenElement, 'enabled:', fullscreenEnabled);
        if (!document.fullscreenElement && fullscreenEnabled) {
            if (!document.fullscreenElement && fullscreenEnabled) {
                handleViolation();
                // Don't auto-reenable here, let the blocking overlay handle it force user action
                // setTimeout(() => { enableFullscreen(); }, 100); 
            }
        }
    });

    // Prevent ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && fullscreenEnabled) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    });

    // Detect visibility change (tab switch)
    document.addEventListener('visibilitychange', () => {
        console.log('Visibility change, hidden:', document.hidden, 'enabled:', fullscreenEnabled);
        if (document.hidden && fullscreenEnabled) {
            handleViolation();
        }
    });
}

// Handle cheating violation
let processingViolation = false;
async function handleViolation() {
    if (processingViolation) return;
    processingViolation = true;

    // Reset flag after delay
    setTimeout(() => { processingViolation = false; }, 2000);

    // Local Logic (No Backend API needed)
    try {
        // Increment violations locally first
        violations++;

        // SYNC VIOLATION TO FIRESTORE (Serverless)
        if (typeof db !== 'undefined') {
            db.collection('participants').doc(PARTICIPANT_ID).update({
                violations: firebase.firestore.FieldValue.increment(1)
            }).catch(e => console.error("FS Violation Sync Error", e));
        }

        const count = violations;
        document.getElementById('topViolations').textContent = count;
        document.getElementById('violationCount').textContent = count;

        if (count >= MAX_VIOLATIONS) {
            // Cap display at Max
            document.getElementById('topViolations').textContent = MAX_VIOLATIONS;
            document.getElementById('violationCount').textContent = MAX_VIOLATIONS;

            // Disqualify
            fullscreenEnabled = false;
            document.getElementById('warningModal').style.display = 'none'; // Close warning if open
            document.getElementById('disqualifyModal').style.display = 'flex';

            // SYNC DISQUALIFIED TO FIRESTORE
            if (typeof db !== 'undefined') {
                db.collection('participants').doc(PARTICIPANT_ID).update({
                    status: 'DISQUALIFIED',
                    end_time: firebase.firestore.FieldValue.serverTimestamp()
                }).catch(e => console.error("FS Disqualify Sync Error", e));
            }

            // End contest locally slightly after
            setTimeout(async () => {
                if (document.exitFullscreen) {
                    try { await document.exitFullscreen(); } catch (e) { }
                }
                showCompletionMessage();
            }, 3000);
        } else {
            // Show warning
            const warningText = count === 1
                ? 'First warning: Do not switch away from the contest window!'
                : `Warning ${count}/${MAX_VIOLATIONS}: One more violation and you will be disqualified!`;

            document.getElementById('warningText').textContent = warningText;
            document.getElementById('warningModal').style.display = 'flex';
        }
    } catch (e) {
        console.error("Error recording violation", e);
    }
}

function closeWarning() {
    document.getElementById('warningModal').style.display = 'none';
    // Force focus back
    window.focus();
    if (!document.fullscreenElement) {
        enableFullscreen();
    }
}

// Load all problems
async function loadProblems() {
    try {
        const response = await fetch('/api/problems');
        const problems = await response.json();

        const problemList = document.getElementById('problemList');
        problemList.innerHTML = '';

        problems.forEach(problem => {
            const item = document.createElement('div');
            item.className = 'problem-item';

            // Create simplified difficulty class (lowercase)
            const difficultyClass = problem.difficulty ? problem.difficulty.toLowerCase() : 'easy';

            // Checkmark if solved
            const solvedIcon = problem.solved ? '<span class="solved-icon">✓</span>' : '';
            const solvedClass = problem.solved ? 'solved' : '';

            // Add HTML with badge
            item.innerHTML = `
                <div class="problem-info">
                    ${solvedIcon}
                    <span class="problem-name">${problem.problem_id}. ${problem.title}</span>
                </div>
                <span class="difficulty-badge ${difficultyClass}">${problem.difficulty}</span>
            `;

            if (problem.solved) {
                item.classList.add('solved');
            }

            item.onclick = () => loadProblem(problem.problem_id);
            problemList.appendChild(item);
        });

        if (problems.length > 0) {
            loadProblem(1);
        }
    } catch (error) {
        console.error('Error loading problems:', error);
    }
}

// Load specific problem
async function loadProblem(problemId) {
    currentProblemId = problemId;
    const language = document.getElementById('language').value;

    try {
        const response = await fetch(`/api/problem/${problemId}?language=${language}&t=${new Date().getTime()}`);
        const problem = await response.json();

        const desc = `Problem ${problem.problem_id}: ${problem.title}
${'='.repeat(80)}
Difficulty: ${problem.difficulty} | Marks: ${problem.marks}

${problem.description}`;

        document.getElementById('problemDescription').textContent = desc;
        document.getElementById('codeEditor').value = problem.starter_code;

        document.querySelectorAll('.problem-item').forEach((item, index) => {
            if (index + 1 === problemId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        showResult('', '');
        hideError();
    } catch (error) {
        console.error('Error loading problem:', error);
    }
}

// Language change handler
document.getElementById('language').addEventListener('change', () => {
    if (currentProblemId) {
        loadProblem(currentProblemId);
    }
});

// Enable Tab indentation in textarea
document.getElementById('codeEditor').addEventListener('keydown', function (e) {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = this.selectionStart;
        const end = this.selectionEnd;

        // Insert 4 spaces
        this.value = this.value.substring(0, start) +
            "    " + this.value.substring(end);

        // Put caret at right position
        this.selectionStart = this.selectionEnd = start + 4;
    }
});

// Show error in separate panel
function showError(errorMessage) {
    const errorPanel = document.getElementById('errorPanel');
    const errorContent = document.getElementById('errorContent');

    errorContent.textContent = errorMessage;
    errorPanel.style.display = 'block';
}

// Hide error panel
function hideError() {
    document.getElementById('errorPanel').style.display = 'none';
}

// Run code
// Helper to poll for results
async function pollForStatus(taskId, statusCallback) {
    const pollInterval = 1000; // 1 second

    while (true) {
        try {
            const response = await fetch(`/api/queue/status/${taskId}`);

            if (response.status === 404) {
                throw new Error("Task not found");
            }

            const data = await response.json();

            if (data.status === 'completed') {
                return data.result;
            } else if (data.status === 'failed') {
                throw new Error(data.error || "Task failed");
            } else {
                // 'pending' or 'processing'
                if (statusCallback) statusCallback(data.status);
                await new Promise(resolve => setTimeout(resolve, pollInterval));
            }
        } catch (e) {
            throw e;
        }
    }
}

// Run code
document.getElementById('runBtn').addEventListener('click', async () => {
    const code = document.getElementById('codeEditor').value.trim();
    const language = document.getElementById('language').value;
    const runBtn = document.getElementById('runBtn');
    const submitBtn = document.getElementById('submitBtn');

    if (!code) {
        showResult('Please write some code before running', 'error');
        return;
    }

    // Disable buttons
    runBtn.disabled = true;
    submitBtn.disabled = true;
    runBtn.textContent = 'Running...'; // Keep "Running..." text as requested

    showResult('Running...', 'info');
    hideError();

    try {
        // FIREBASE MODE
        if (db) {
            console.log("Using Firebase for Run...");

            // 1. Create a submission document directly
            const docRef = await db.collection('submissions').add({
                participant_id: PARTICIPANT_ID,
                name: PARTICIPANT_NAME,
                problem_id: currentProblemId,
                code: code,
                language: language,
                status: 'pending', // Queue it
                type: 'run',
                submitted_at: firebase.firestore.FieldValue.serverTimestamp()
            });

            const taskId = docRef.id;
            console.log(`Document created: ${taskId}`);

            // 2. Listen for changes (Polling replacement)
            const unsubscribe = docRef.onSnapshot((doc) => {
                const data = doc.data();
                if (!data) return;

                if (data.status === 'completed' || data.status === 'error') {
                    unsubscribe(); // Stop listening

                    if (data.status === 'error') {
                        showResult(`✗ System Error`, 'error');
                        showError(data.error_message || 'Unknown error');
                        runBtn.disabled = false;
                        submitBtn.disabled = false;
                        runBtn.textContent = 'Run Code';
                        return;
                    }

                    const result = data.result;
                    // Handle Result
                    if (result.success) {
                        if (result.passed) {
                            showResult(`✓ Sample Test Passed! (${result.time.toFixed(3)}s)`, 'success');
                            // If passed, we don't always have error output, but if we do (from custom executor), show it.
                            // Usually executor returns output in `actual`
                            // We construct the "Error" box content for details
                            // check if inputs are available in result (worker should send them)
                            // For 'run', the worker sends input/expected/actual
                            // But my worker.py currently sends generic result. I need to make sure worker.py sends details for 'run'
                            // Actually, let's just show what we have.
                            showError(`Output: ${result.actual || 'Correct'}`);
                        } else {
                            showResult(`✗ Sample Test Failed`, 'error');
                            // Worker needs to ensure these fields exist in result
                            const details = `Input: ${result.input || '?'}\nExpected: ${result.expected || '?'}\nYour Output: ${result.actual || '?'}`;
                            showError(details);
                        }
                    } else {
                        showResult(`✗ Execution Error`, 'error');
                        showError(result.error || 'Unknown error');
                    }

                    // Cleanup
                    runBtn.disabled = false;
                    submitBtn.disabled = false;
                    runBtn.textContent = 'Run Code';
                }
                else if (data.status === 'running') {
                    showResult('Running... (Worker Claimed)', 'info');
                }
            });

            return; // Stop here, don't do the fetch below
        }

        // FALLBACK TO OLD API (If Firebase fails)
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                problem_id: currentProblemId,
                code: code,
                language: language
            })
        });

        const initialResult = await response.json();

        if (initialResult.queued) {
            // Poll for result
            const result = await pollForStatus(initialResult.task_id);

            // Handle final result
            if (result.success) {
                if (result.passed) {
                    showResult(`✓ Sample Test Passed! (${result.time.toFixed(3)}s)`, 'success');
                    showError(`Input: ${JSON.stringify(result.input)}\nExpected: ${JSON.stringify(result.expected)}\nYour Output: ${JSON.stringify(result.actual)}`);
                } else {
                    showResult(`✗ Sample Test Failed`, 'error');
                    showError(`Input: ${JSON.stringify(result.input)}\nExpected: ${JSON.stringify(result.expected)}\nYour Output: ${JSON.stringify(result.actual)}`);
                }
            } else {
                showResult(`✗ ${result.error_type === 'execution' ? 'Execution Error' : 'System Error'}`, 'error');
                showError(result.error || 'Unknown error');
            }

        } else {
            // Fallback for immediate errors (shouldn't happen with queue)
            showResult(`✗ Error`, 'error');
            showError(initialResult.message || 'Unknown error');
        }

    } catch (error) {
        showResult(`✗ Error`, 'error');
        showError(error.message);
    } finally {
        // Re-enable buttons
        runBtn.disabled = false;
        submitBtn.disabled = false;
        runBtn.textContent = 'Run Code';
    }
});

// Submit code
// Submit code
document.getElementById('submitBtn').addEventListener('click', async () => {
    const code = document.getElementById('codeEditor').value.trim();
    const language = document.getElementById('language').value;
    const runBtn = document.getElementById('runBtn');
    const submitBtn = document.getElementById('submitBtn');

    if (!code) {
        showResult('Please write some code before submitting', 'error');
        return;
    }

    // Disable buttons
    runBtn.disabled = true;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Judging...'; // Keep "Judging..." text

    showResult('Judging...', 'info');
    hideError();

    try {
        // FIREBASE MODE
        if (db) {
            console.log("Using Firebase for Submit...");

            // 1. Create a submission document directly
            const docRef = await db.collection('submissions').add({
                participant_id: PARTICIPANT_ID,
                name: PARTICIPANT_NAME,
                problem_id: currentProblemId,
                code: code,
                language: language,
                status: 'pending', // Queue it
                type: 'submit',
                submitted_at: firebase.firestore.FieldValue.serverTimestamp()
            });

            const taskId = docRef.id;
            console.log(`Submission created: ${taskId}`);

            // 2. Listen for changes
            const unsubscribe = docRef.onSnapshot((doc) => {
                const data = doc.data();
                if (!data) return;

                if (data.status === 'completed' || data.status === 'error') {
                    unsubscribe();

                    if (data.status === 'error') {
                        showResult(`✗ System Error`, 'error');
                        showError(data.error_message || 'Unknown error');
                        runBtn.disabled = false;
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Submit Solution';
                        return;
                    }

                    const result = data.result;
                    // Handle Result
                    if (result.success) {
                        if (result.passed) {
                            showResult(`✓ Accepted (+${result.score || 10} marks)`, 'success');

                            // Mark solved
                            const currentItem = document.querySelector(`.problem-item:nth-child(${currentProblemId})`);
                            if (currentItem && !currentItem.classList.contains('solved')) {
                                currentItem.classList.add('solved');
                                // ... icon logic ...
                                const infoDiv = currentItem.querySelector('.problem-info');
                                if (infoDiv && !infoDiv.querySelector('.solved-icon')) {
                                    const icon = document.createElement('span');
                                    icon.className = 'solved-icon';
                                    icon.textContent = '✓';
                                    infoDiv.insertBefore(icon, infoDiv.firstChild);
                                }
                            }

                            // Update score (Listen to user doc ideal, but fetch for now to confirm)
                            updateScore(); // We should update this function to read from Firebase too eventually

                            setTimeout(() => {
                                const nextProblemId = currentProblemId + 1;
                                if (nextProblemId <= 10) loadProblem(nextProblemId);
                            }, 1500);

                        } else {
                            showResult(`✗ Wrong Answer`, 'error');
                            // Show details if available
                            if (result.details) showError(result.details);
                        }
                    } else {
                        showResult(`✗ Execution Error`, 'error');
                        showError(result.error || 'Unknown error');
                    }

                    // Cleanup
                    runBtn.disabled = false;
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Submit Solution';
                }
                else if (data.status === 'running') {
                    showResult('Judging... (Worker Claimed)', 'info');
                }
            });

            return; // Stop here
        }

        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                problem_id: currentProblemId,
                code: code,
                language: language
            })
        });

        let initialResult;
        try {
            const text = await response.text();
            try {
                initialResult = JSON.parse(text);
            } catch (e) {
                console.error("Failed to parse JSON:", text);
                if (text.includes("OutOfMemory") || text.includes("MemoryError")) {
                    throw new Error("Server Out of Memory. Please try again.");
                } else if (text.includes("504 Gateway Time-out")) {
                    throw new Error("Server Timeout. The operation took too long.");
                } else if (text.includes("502 Bad Gateway")) {
                    throw new Error("Server Bad Gateway. The backend might be restarting.");
                } else if (response.status !== 200) {
                    throw new Error(`Server Error (${response.status}): ${text.substring(0, 50)}...`);
                }
                throw new Error("Invalid Server Response: " + text.substring(0, 100));
            }
        } catch (e) {
            throw e;
        }

        if (initialResult.queued) {
            const result = await pollForStatus(initialResult.task_id);

            if (result.success) {
                if (result.verdict === 'Accepted') {
                    const marksMsg = result.already_solved ? '(Already Solved)' : `(+${result.score} marks)`;
                    const statusType = result.already_solved ? 'info' : 'success';

                    showResult(`✓ ${result.verdict} ${marksMsg}`, statusType);
                    if (!result.already_solved) {
                        updateScore();
                    }

                    // Mark current problem as solved in sidebar
                    const currentItem = document.querySelector(`.problem-item:nth-child(${currentProblemId})`);
                    if (currentItem && !currentItem.classList.contains('solved')) {
                        currentItem.classList.add('solved');
                        const infoDiv = currentItem.querySelector('.problem-info');
                        if (infoDiv && !infoDiv.querySelector('.solved-icon')) {
                            const icon = document.createElement('span');
                            icon.className = 'solved-icon';
                            icon.textContent = '✓';
                            infoDiv.insertBefore(icon, infoDiv.firstChild);
                        }
                    }

                    // Auto-advance to next problem
                    setTimeout(() => {
                        const nextProblemId = currentProblemId + 1;
                        if (nextProblemId <= 10) {
                            loadProblem(nextProblemId);
                        }
                    }, 1500);
                } else {
                    showResult(`✗ ${result.verdict}`, 'error');
                    if (result.details) {
                        showError(result.details);
                    }
                }
            } else {
                showResult(`Error: ${result.message}`, 'error');
            }
        } else {
            showResult(`Error: ${initialResult.message || 'Unknown error'}`, 'error');
        }

    } catch (error) {
        showResult(`✗ Error`, 'error');
        showError(error.message);
    } finally {
        // Re-enable buttons
        runBtn.disabled = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Solution';
    }
});

// End contest
// End contest - Show confirmation modal
document.getElementById('endBtn').addEventListener('click', () => {
    document.getElementById('endContestModal').style.display = 'flex';
});

// Cancel end contest
function cancelEndContest() {
    document.getElementById('endContestModal').style.display = 'none';
}

// Confirm end contest
async function confirmEndContest() {
    document.getElementById('endContestModal').style.display = 'none';
    fullscreenEnabled = false;

    try {
        // End contest on backend
        await fetch('/api/contest/end', { method: 'POST' });

        // Exit fullscreen if active
        if (document.fullscreenElement) {
            try {
                await document.exitFullscreen();
            } catch (e) {
                console.log('Fullscreen exit error:', e);
            }
        }

        // Small delay to ensure fullscreen exit completes
        setTimeout(() => {
            // SYNC END TO FIRESTORE
            if (typeof db !== 'undefined') {
                db.collection('participants').doc(PARTICIPANT_ID).update({
                    status: 'COMPLETED',
                    end_time: firebase.firestore.FieldValue.serverTimestamp()
                }).catch(e => console.error("FS End Sync Error", e));
            }
            showCompletionMessage();
        }, 100);
    } catch (error) {
        console.error('Error ending contest:', error);
        // Still show completion even if there's an error
        showCompletionMessage();
    }
}

// Show result message
function showResult(message, type) {
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = message;
    resultDiv.className = 'result-message ' + type;
}

// Update score
async function updateScore() {
    // If using Firebase, the onSnapshot listener handles this automatically
    if (typeof db !== 'undefined') return;

    try {
        const response = await fetch('/api/results');
        const results = await response.json();

        if (results && results.total_score !== undefined) {
            document.getElementById('score').textContent = `Score: ${results.total_score}/145`;
        }
    } catch (error) {
        console.error('Error updating score:', error);
    }
}

// Timer
// Timer
function startTimer() {
    // If we just clicked start, set local time immediately to avoid delay
    if (!window.contestStartTime) window.contestStartTime = new Date();

    timerInterval = setInterval(() => {
        try {
            if (!window.contestStartTime) return;

            const now = new Date();
            const elapsed = Math.floor((now - window.contestStartTime) / 1000);
            const duration = 2 * 60 * 60; // 2 Hours in seconds
            const remaining = duration - elapsed;

            if (remaining >= 0) {
                const hours = Math.floor(remaining / 3600);
                const minutes = Math.floor((remaining % 3600) / 60);
                const seconds = remaining % 60;

                document.getElementById('timer').textContent =
                    `⏱ ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            } else {
                // Time up
                clearInterval(timerInterval);
                fullscreenEnabled = false;
                if (document.exitFullscreen) {
                    try { document.exitFullscreen(); } catch (e) { }
                }

                // Update specific message or just end
                if (typeof db !== 'undefined') {
                    db.collection('participants').doc(PARTICIPANT_ID).update({
                        status: 'COMPLETED',
                        end_time: firebase.firestore.FieldValue.serverTimestamp()
                    });
                }
                showCompletionMessage();
            }
        } catch (error) {
            console.error('Timer error:', error);
        }
    }, 1000);
}

// Redirect to completion page
function showCompletionMessage() {
    // Navigate to completion page
    // We do not need special pywebview handling here for the cloud version
    window.location.href = '/completion';
}
