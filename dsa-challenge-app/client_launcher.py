import webview
import sys
import threading
import time
import os

# --- EXPLANATION FOR THE USER ---
# This script is the "Client". It runs on the Participant's machine.
# It does NOT contain any game logic or database.
# It only knows how to:
# 1. Open a window.
# 2. Go to a URL (your backend).
# 3. Stay in Fullscreen (to prevent cheating).
# --------------------------------

# Configuration: Point this to your manually deployed backend IP/URL
# OPTION 3 (Cloud): After you deploy to Render/Heroku/AWS, they will give you a public URL.
# Paste that URL here.
# Example: 'https://dsa-contest-app.onrender.com'
BACKEND_URL = "https://atc-dsa-app.onrender.com"  # Production URL

class ClientApi:
    """
    This API class allows the web page (Javascript) to talk to this Python window.
    We use it for things that the browser can't do easily, like 'Close Window' 
    or 'Force Fullscreen'.
    """
    def __init__(self):
        self._window = None

    def set_window(self, window):
        self._window = window

    def quit_app(self):
        if self._window:
            self._window.destroy()
        os._exit(0)

    def set_fullscreen(self, enable):
        if self._window:
            current = self._window.fullscreen
            if enable != current:
                self._window.toggle_fullscreen()

def main():
    api = ClientApi()
    
    # Create the window
    # fullscreen=True enforces the anti-cheating environment immediately.
    window = webview.create_window(
        'DSA Contest Client',
        BACKEND_URL,
        width=1400,
        height=900,
        fullscreen=True, 
        frameless=True,
        on_top=True,       # Keep on top of other windows
        easy_drag=False,   # Disable dragging
        resizable=False,   # Disable resizing
        text_select=False, # Disable selecting text
        js_api=api
    )
    
    api.set_window(window)
    
    # Start the GUI loop
    webview.start(debug=False) 
    # debug=False prevents opening Developer Tools (F12), important for anti-cheat!

if __name__ == "__main__":
    main()
