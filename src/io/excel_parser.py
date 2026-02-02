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
        Also looks for 'ΠΛΑΦΟΝ'.
        """
        df = pd.read_excel(self.stream)
        wage = 15.33 # Fallback
        cap = 4500.0 # Fallback
        
        try:
            # Flatten search: look for keywords anywhere in the first 10 columns
            for r in range(len(df)):
                for c in range(min(10, len(df.columns))):
                    cell_val = str(df.iloc[r, c]).upper()
                    
                    # 1. Look for Wage (ΩΡΟΜ)
                    if 'ΩΡΟΜ' in cell_val or 'OROM' in cell_val:
                        for offset in range(1, 4): # Check next 3 columns
                            if c + offset < len(df.columns):
                                val = df.iloc[r, c+offset]
                                if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
                                    wage = float(val)
                                    logger.info(f"Wage found: {wage}")
                                    break
                    
                    # 2. Look for Cap (ΠΛΑΦΟΝ)
                    if 'ΠΛΑΦΟΝ' in cell_val or 'PLAFON' in cell_val or 'ΠΟΣΟ' in cell_val:
                        for offset in range(1, 4):
                            if c + offset < len(df.columns):
                                val = df.iloc[r, c+offset]
                                if pd.notna(val) and isinstance(val, (int, float)) and val > 1000:
                                    cap = float(val)
                                    logger.info(f"Cap found: {cap}")
                                    break
            
            # Heuristic: if cap not found by label, look above the wage
            if cap == 4500.0: # If still default
                # Re-scan for wage to check cell above
                for r in range(len(df)):
                    for c in range(min(10, len(df.columns))):
                        if wage == df.iloc[r, c]:
                            if r - 1 >= 0:
                                val_above = df.iloc[r-1, c]
                                if pd.notna(val_above) and isinstance(val_above, (int, float)) and val_above > 1000:
                                    cap = float(val_above)
                                    logger.info(f"Cap found above wage: {cap}")
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
