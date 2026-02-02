import pandas as pd
import io
from loguru import logger
from src.io.excel_parser import ExcelParser # Reusing your existing logic but wrapped cleaner
from src.io.exporter import GreekExcelExporter

class TimesheetService:
    @staticmethod
    def process_excel_upload(file_obj):
        """Reads uploaded Excel into a DataFrame safely."""
        try:
            return pd.read_excel(file_obj)
        except Exception as e:
            logger.error(f"Excel read error: {e}")
            return None

    @staticmethod
    def generate_final_files(schedule_data, original_excel_bytes, month_name, ee_totals):
        """Orchestrates the generation of the final artifacts."""
        exporter = GreekExcelExporter(schedule_data)
        
        # 1. Detailed Log Stream
        detailed_stream = exporter.export_excel_stream()
        
        # 2. Updated Original Stream
        original_stream = io.BytesIO(original_excel_bytes)
        updated_stream = exporter.update_budget_excel_stream(
            original_stream, 
            month_name, 
            ee_totals,
            schedule_data
        )
        return detailed_stream, updated_stream
