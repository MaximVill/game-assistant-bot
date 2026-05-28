import os
import aiofiles
import traceback
from datetime import datetime

LOGS_DIR = "logs"

async def log_user_action(user_id: int, action: str, request: str, result: str, exception: Exception = None):
    log_file = os.path.join(LOGS_DIR, f"{user_id}.log")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    log_entry = f"[{timestamp}] Action: {action} | Request: {request} | Result: {result}\n"

    if exception:
        error_traceback = traceback.format_exc()
        log_entry += f"Exception: {str(exception)}\nTraceback:\n{error_traceback}\n"
        log_entry += "-" * 40 + "\n"

    try:
        async with aiofiles.open(log_file, mode="a", encoding="utf-8") as f:
            await f.write(log_entry)
    except Exception as e:
        print(f"Failed to write to log file {log_file}: {e}")