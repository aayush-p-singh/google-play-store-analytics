from datetime import datetime
import pytz

def is_window_active(start_hour: int, end_hour: int) -> bool:
    """
    Checks if the current system time falls within a specific window in IST.
    """
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    current_hour = current_time.hour
    
    # Check if current hour falls strictly within the window
    return start_hour <= current_hour < end_hour