import pytest
from datetime import date
from src.core.engine import TimesheetEngine

class TestTimesheetEngine:
    def test_workday_generation(self):
        # January 2026
        engine = TimesheetEngine(year=2026, month=1)
        workdays = engine._get_workdays()
        
        # Check known holidays/weekends
        assert date(2026, 1, 1) not in workdays # New Year
        assert date(2026, 1, 6) not in workdays # Epiphany
        assert date(2026, 1, 30) not in workdays # Three Hierarchs
        assert date(2026, 1, 3) not in workdays # Saturday
        assert date(2026, 1, 4) not in workdays # Sunday
        assert date(2026, 1, 2) in workdays # Friday

    def test_distribution_logic(self):
        engine = TimesheetEngine(wage=10.0, year=2026, month=1)
        targets = {
            "Task A": 100.0, # 10 hours
            "Task B": 50.0   # 5 hours
        }
        
        schedule = engine.generate_distribution(targets)
        
        # Verify total hours
        total_hours = sum(entry['Hours'] for entry in schedule)
        expected_hours = (100.0 / 10.0) + (50.0 / 10.0)
        assert total_hours == expected_hours
        
        # Verify increments
        for entry in schedule:
            assert entry['Hours'] % 0.5 == 0
            assert entry['Hours'] <= 7.0 # Max block constraint
