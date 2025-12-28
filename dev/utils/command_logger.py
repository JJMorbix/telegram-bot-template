import time

def log_command(user_id: int, username: str, command: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {username} (ID: {user_id}) eseguito il comando: {command}")