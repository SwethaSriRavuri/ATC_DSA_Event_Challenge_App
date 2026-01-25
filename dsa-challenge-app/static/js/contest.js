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
    startBtn.addEventListener('click', () => {
        enableFullscreen();
        document.getElementById('startOverlay').style.display = 'none';
        startTimer();
        setupAntiCheating();

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
async function handleViolation() {
    try {
        const response = await fetch('/api/contest/violation', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            const count = result.violation_count;
            document.getElementById('topViolations').textContent = count;
            document.getElementById('violationCount').textContent = count;

            if (result.status === 'DISQUALIFIED') {
                // Disqualify
                fullscreenEnabled = false;
                document.getElementById('warningModal').style.display = 'none'; // Close warning if open
                document.getElementById('disqualifyModal').style.display = 'flex';

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
    runBtn.textContent = 'Running...';

    showResult('Running...', 'info');
    hideError();

    try {
        const response = await fetch('/api/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                problem_id: currentProblemId,
                code: code,
                language: language
            })
        });

        const result = await response.json();

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
    submitBtn.textContent = 'Judging...';

    showResult('Judging...', 'info');
    hideError();

    try {
        const response = await fetch('/api/submit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                problem_id: currentProblemId,
                code: code,
                language: language
            })
        });

        let result;
        try {
            result = await response.json();
        } catch (e) {
            throw new Error("Server Error: Check your code or try again.");
        }

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
    try {
        const response = await fetch('/api/results');
        const results = await response.json();

        if (results && results.total_score !== undefined) {
            document.getElementById('score').textContent = `Score: ${results.total_score}/100`;
        }
    } catch (error) {
        console.error('Error updating score:', error);
    }
}

// Timer
function startTimer() {
    timerInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/contest/status');
            const status = await response.json();

            if (status && status.is_active) {
                const remaining = status.remaining_time;
                const hours = Math.floor(remaining / 3600);
                const minutes = Math.floor((remaining % 3600) / 60);
                const seconds = remaining % 60;

                document.getElementById('timer').textContent =
                    `⏱ ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

                // Sync violations
                if (status.violation_count !== undefined) {
                    document.getElementById('topViolations').textContent = status.violation_count;
                }

                if (remaining <= 0) {
                    clearInterval(timerInterval);
                    fullscreenEnabled = false;
                    if (document.exitFullscreen) {
                        try { await document.exitFullscreen(); } catch (e) { }
                    }
                    showCompletionMessage();
                }
            } else if (status && status.status === 'DISQUALIFIED') {
                // Already disqualified
                clearInterval(timerInterval);
                fullscreenEnabled = false;
                document.getElementById('disqualifyModal').style.display = 'flex';
                setTimeout(() => showCompletionMessage(), 3000);
            } else {
                clearInterval(timerInterval);
                fullscreenEnabled = false;
                if (document.exitFullscreen) {
                    try { await document.exitFullscreen(); } catch (e) { }
                }
                showCompletionMessage();
            }
        } catch (error) {
            console.error('Error updating timer:', error);
        }
    }, 1000);
}

// Redirect to completion page
function showCompletionMessage() {
    // Navigate to completion page
    // We do not need special pywebview handling here for the cloud version
    window.location.href = '/completion';
}
