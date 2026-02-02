import re
import pandas as pd
from loguru import logger

class ExcelParser:
    def __init__(self, file_stream):
        self.stream = file_stream

    def get_project_metadata(self):
        """
        Scans the Excel for the Wage and Monthly Cap.
        Pattern: Look for 'ΩΡΟΜ.', value to right is Wage, value above that is Cap.
        """
        df = pd.read_excel(self.stream)
        # We need the raw grid, not just headers
        
        wage = 15.33 # Default fallback
        cap = 4500.0 # Default fallback
        
        try:
            for r in range(len(df)):
                for c in range(len(df.columns)):
                    cell_val = str(df.iloc[r, c]).upper()
                    if 'ΩΡΟΜ' in cell_val or 'OROM' in cell_val:
                        # Wage is usually the next column
                        if c + 1 < len(df.columns):
                            found_wage = df.iloc[r, c+1]
                            if pd.notna(found_wage) and isinstance(found_wage, (int, float)):
                                wage = float(found_wage)
                                logger.info(f"Dynamic Wage found: {wage}")
                                
                                # Cap is usually directly above the wage
                                if r - 1 >= 0:
                                    found_cap = df.iloc[r-1, c+1]
                                    if pd.notna(found_cap) and isinstance(found_cap, (int, float)):
                                        cap = float(found_cap)
                                        logger.info(f"Dynamic Cap found: {cap}")
                        break
        except Exception as e:
            logger.warning(f"Metadata scan failed: {e}. Using defaults.")
            
        return {"wage": wage, "cap": cap}

    def get_monthly_targets(self, month_column_name='JANUARY'):
        self.stream.seek(0) # Reset stream for second read
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
                        # Look for name or numeric value in target_col
                        for offset in range(1, 10):
                            if row_idx + offset < len(df):
                                val = df.at[row_idx + offset, target_col]
                                try:
                                    num = float(val)
                                    # Skip years and large numbers
                                    if not pd.isna(num) and 0 < num < 2000:
                                        return num
                                except:
                                    continue
            return 0.0

        targets = {"EE3": find_value_for_ee(3), "EE4": find_value_for_ee(4)}
        return {k: v for k, v in targets.items() if v > 0}