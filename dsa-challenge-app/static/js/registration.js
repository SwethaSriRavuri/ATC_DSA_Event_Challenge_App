document.getElementById('registrationForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();

    if (!name) {
        alert('Please enter your name');
        return;
    }

    // Generate a simple ID locally or use auth
    // For simplicity, we create a random ID (or you could sign in anonymously first)
    // We will generate a User ID: 'user_' + random string
    const userId = 'user_' + Math.random().toString(36).substr(2, 9);

    try {
        // Check for duplicates first
        // Note: This requires a composite index if combining with other filters, but simple where() is fine.
        const existing = await db.collection('participants').where('email', '==', email).get();
        if (!existing.empty) {
            alert('This email is already registered. Please contact an organizer.');
            return;
        }

        // Direct Firestore Write (Serverless Scalability)
        const participantRef = db.collection('participants').doc(userId);

        // Check if exists (unlikely with random ID, but good practice)
        // With random ID we can just SET directly
        await participantRef.set({
            name: name,
            email: email,
            score: 0,
            solved: [],
            status: 'ACTIVE',
            violations: 0,
            start_time: firebase.firestore.FieldValue.serverTimestamp()
        });

        // Save ID to localStorage so contest page knows who we are
        localStorage.setItem('dsa_participant_id', userId);
        localStorage.setItem('dsa_participant_name', name);

        // Redirect
        window.location.href = '/contest';

    } catch (error) {
        console.error("Registration Error", error);
        alert('Registration failed: ' + error.message);
    }
});
