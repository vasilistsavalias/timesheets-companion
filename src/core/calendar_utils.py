from datetime import date
import holidays

def is_workday(dt: date) -> bool:
    # 1. Weekend check
    if dt.weekday() >= 5:
        return False
    
    # 2. Hard-coded Greek Holidays from ELKE manual
    # Jan 1 (New Year), Jan 6 (Theofania), Jan 30 (Three Hierarchs)
    hard_holidays = [
        (1, 1),   # New Year
        (1, 6),   # Epiphany
        (1, 30),  # Three Hierarchs
        (3, 25),  # Independence Day
        (10, 28), # Ohi Day
        (11, 17), # Polytechnic
    ]
    if (dt.month, dt.day) in hard_holidays:
        return False
        
    # 3. Dynamic Greek holidays (Easter, etc.)
    el_holidays = holidays.Greece()
    if dt in el_holidays:
        return False
        
    return True