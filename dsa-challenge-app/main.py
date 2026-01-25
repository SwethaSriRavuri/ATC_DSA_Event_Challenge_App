import webview
import threading
import time
from app import app

from waitress import serve

def start_flask():
    """Start Flask server in background using Waitress for production readiness"""
    serve(app, host='0.0.0.0', port=5000, threads=6)

class Api:
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def set_fullscreen(self, enable):
        """Set fullscreen mode from JS"""
        if self._window:
            current = self._window.fullscreen
            if enable != current:
                self._window.toggle_fullscreen()

    def quit_app(self):
        """Quit the application"""
        if self._window:
            self._window.destroy()

    def end_contest_session(self):
        """Handle end contest sequence: exit fullscreen -> wait -> navigate"""
        def _restore_and_navigate():
            time.sleep(0.1)  # Allow JS API call to return first
            if self._window:
                if self._window.fullscreen:
                    self._window.toggle_fullscreen()
                    time.sleep(1.0)  # Wait longer for OS
                    # Force a resize to trigger frame redraw
                    self._window.resize(1400, 900)
                
            self._window.load_url('http://127.0.0.1:5000/completion')
        
        # Run in thread to avoid blocking JS return or killing context too early
        threading.Thread(target=_restore_and_navigate).start()

def main():
    """Main entry point - creates desktop window"""
    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to start
    time.sleep(2)
    
    api = Api()
    
    # Create desktop window with fullscreen
    window = webview.create_window(
        'DSA Coding Challenge',
        'http://127.0.0.1:5000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,  # Start windowed, will go fullscreen after registration
        frameless=False,
        js_api=api
    )
    
    api.set_window(window)
    webview.start(debug=False)

if __name__ == "__main__":
    main()
