import re
import pandas as pd
from loguru import logger

class ExcelParser:
    def __init__(self, file_stream):
        self.stream = file_stream

    def get_project_metadata(self):
        """
        Scans the Excel for the Wage and Monthly Cap.
        """
        df = pd.read_excel(self.stream)
        wage = 15.33 
        cap = 4500.0 
        
        try:
            for r in range(len(df)):
                for c in range(min(15, len(df.columns))):
                    cell_val = str(df.iloc[r, c]).upper()
                    
                    if 'ΩΡΟΜ' in cell_val or 'OROM' in cell_val:
                        # 1. Find Wage
                        for offset in range(1, 4):
                            if c + offset < len(df.columns):
                                val = df.iloc[r, c+offset]
                                if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
                                    wage = float(val)
                                    logger.info(f"Wage found: {wage}")
                                    
                                    # 2. Find Cap (The largest number in the row above)
                                    if r - 1 >= 0:
                                        # Look at the whole row above near the wage column
                                        row_above = df.iloc[r-1, max(0, c-2):min(len(df.columns), c+5)]
                                        nums = [float(v) for v in row_above if pd.notna(v) and isinstance(v, (int, float)) and v > 1000]
                                        if nums:
                                            cap = max(nums) # Pick the highest (e.g. 4500 over 2200)
                                            logger.info(f"Cap found in row above: {cap}")
                        break
        except Exception as e:
            logger.warning(f"Metadata scan failed: {e}")
            
        return {"wage": wage, "cap": cap}

    def get_monthly_targets(self, month_column_name='JANUARY'):
        self.stream.seek(0)
        df = pd.read_excel(self.stream)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        target_col = next((c for c in df.columns if month_column_name.upper() in c), None)
        if not target_col:
            raise ValueError(f"Month column {month_column_name} not found.")

        def find_value_for_ee(ee_num):
            label_pattern = rf'[\u0395E][\u0395E]\s*{ee_num}'
            for row_idx in range(len(df)):
                for col_idx in range(min(5, len(df.columns))):
                    cell_val = str(df.iloc[row_idx, col_idx]).upper()
                    if re.search(label_pattern, cell_val):
                        # Find name row after label
                        for offset in range(1, 10):
                            if row_idx + offset < len(df):
                                val = df.at[row_idx + offset, target_col]
                                try:
                                    num = float(val)
                                    if not pd.isna(num) and 0 < num < 2000:
                                        return num
                                except:
                                    continue
            return 0.0

        targets = {"EE3": find_value_for_ee(3), "EE4": find_value_for_ee(4)}
        return {k: v for k, v in targets.items() if v > 0}