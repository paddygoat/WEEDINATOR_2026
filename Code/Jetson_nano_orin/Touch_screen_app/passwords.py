import os

PASSWORD_PATH = "/home/nano/Documents/WEEDINATOR/Code/Jetson_nano/password.txt"
_CACHED_PASSWORD = None

def get_password() -> str:
    """
    Retrieves the password from memory.
    Reads from disk only once on the first function call.
    """
    global _CACHED_PASSWORD
    if _CACHED_PASSWORD is None:
        if os.path.exists(PASSWORD_PATH):
            try:
                with open(PASSWORD_PATH, "r", encoding="utf-8") as f:
                    _CACHED_PASSWORD = f.read().strip()
                print("[AUTH] Password loaded into memory successfully.")
            except Exception as e:
                print(f"[AUTH ERROR] Failed to read password file: {e}")
                _CACHED_PASSWORD = ""
        else:
            print(f"[AUTH ERROR] Password file not found at: {PASSWORD_PATH}")
            _CACHED_PASSWORD = ""
            
    return _CACHED_PASSWORD