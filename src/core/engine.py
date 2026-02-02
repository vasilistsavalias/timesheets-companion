from datetime import date
import calendar
from src.core.calendar_utils import is_workday

class TimesheetEngine:
    def __init__(self, wage=15.33, year=2026, month=1):
        self.wage = wage
        self.year = year
        self.month = month
        self.workdays = self._get_workdays()

    def _get_workdays(self):
        days = []
        _, num_days = calendar.monthrange(self.year, self.month)
        for d in range(1, num_days + 1):
            dt = date(self.year, self.month, d)
            if is_workday(dt):
                days.append(dt)
        return days

    def generate_distribution(self, targets):
        """
        targets: dict e.g. {'Π3.1': 100.0, 'Π4.1': 400.0, 'Π4.2': 400.0}
        Logic: Greedy 7h blocks, Sequential per Deliverable.
        """
        schedule = []
        # Convert money to total hours per deliverable (rounded to 0.5)
        # Note: We round at the end of each deliverable to minimize error
        deliv_hours = {k: round((v / self.wage) * 2) / 2 for k, v in targets.items()}
        
        available_days = list(self.workdays)
        current_day_idx = 0
        
        # Process deliverables in order (Π3.1, Π4.1, etc.)
        for deliverable in sorted(deliv_hours.keys()):
            remaining = deliv_hours[deliverable]
            
            while remaining > 0:
                if current_day_idx >= len(available_days):
                    # Fallback if too many hours for the month (rare with 7h blocks)
                    current_day_idx = 0 
                
                dt = available_days[current_day_idx]
                
                # USER RULE: Always choose 7h if possible, otherwise use remaining.
                # Max 7h per day as per user preference to keep entries minimal.
                chunk = min(remaining, 7.0)
                
                # Check if we should round the chunk if it's the last bit
                # remaining is already a multiple of 0.5
                
                schedule.append({
                    'Date': dt,
                    'Deliverable': deliverable,
                    'Hours': chunk
                })
                
                remaining -= chunk
                current_day_idx += 1
                
        return sorted(schedule, key=lambda x: x['Date'])
