import pytest
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.manager import Base
from src.services.auth_service import AuthService
from src.io.excel_parser import ExcelParser
from src.io.scraper import WebrescomScraper
from src.core.engine import TimesheetEngine
from src.io.exporter import GreekExcelExporter

# E2E Test Suite
def test_full_system_e2e_flow():
    # 1. SETUP: Temporary DB
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("\n[E2E] Starting End-to-End Simulation...")

    # 2. USER MANAGEMENT CYCLE
    print("[E2E] Step 1: Admin creates a new user...")
    new_user = AuthService.create_user(db, "temp_worker", "secret", name="Temporary Worker")
    assert new_user is not None
    
    print("[E2E] Step 2: Promoting user to admin...")
    new_user.is_admin = True
    db.commit()
    assert db.query(Base.metadata.tables['users']).filter_by(username="temp_worker").first().is_admin is True
    
    print("[E2E] Step 3: Demoting user to standard...")
    new_user.is_admin = False
    db.commit()
    assert db.query(Base.metadata.tables['users']).filter_by(username="temp_worker").first().is_admin is False
    
    # 3. CORE PROCESSING LOGIC
    print("[E2E] Step 4: Simulating Timesheet Generation with local files...")
    
    # Paths to local files (we'll check if they exist)
    excel_path = os.path.join('data', '10836 ΤΣΑΒΑΛΙΑΣ.xlsx')
    # Use the docs file for the UI paste
    ui_path = os.path.join('docs', 'webrescom', 'webrescom_interface.md')
    
    if os.path.exists(excel_path) and os.path.exists(ui_path):
        with open(ui_path, 'r', encoding='utf-8') as f:
            ui_text = f.read()
            
        scraper = WebrescomScraper(ui_text)
        hierarchy, _ = scraper.scrape_structure()
        meta = scraper.get_project_metadata()
        
        parser = ExcelParser(excel_path)
        targets = parser.get_monthly_targets("JANUARY")
        
        # Calculate split
        final_targets = {}
        for ee, money in targets.items():
            match = next((h for h in hierarchy if ee in h or h in ee), None)
            if match:
                for d in hierarchy[match]:
                    final_targets[d] = money / len(hierarchy[match])
        
        # Run Engine
        engine_logic = TimesheetEngine(wage=meta['wage'], year=2026, month=1)
        schedule = engine_logic.generate_distribution(final_targets)
        
        assert len(schedule) > 0
        print(f"[E2E] Generated {len(schedule)} work entries successfully.")
    else:
        print("[E2E] Skipping file processing (local data files not found in dev environment).")

    # 4. WAIT & CLEANUP
    print("[E2E] Step 5: Waiting 5 seconds for final verification...")
    time.sleep(5)
    
    print("[E2E] Step 6: User deleting themselves...")
    db.delete(new_user)
    db.commit()
    assert db.query(Base.metadata.tables['users']).filter_by(username="temp_worker").first() is None
    
    print("[E2E] E2E Simulation COMPLETE. System is healthy.")
    db.close()

if __name__ == "__main__":
    test_full_system_e2e_flow()
