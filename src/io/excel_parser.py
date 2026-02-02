import re
import pandas as pd
from loguru import logger

class ExcelParser:
    def __init__(self, file_stream):
        """
        file_stream: file-like object (BytesIO)
        """
        self.stream = file_stream

    def get_monthly_targets(self, month_column_name='JANUARY'):
        # Read from stream instead of path
        df = pd.read_excel(self.stream)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        target_col = next((c for c in df.columns if month_column_name.upper() in c), None)
        if not target_col:
            raise ValueError(f"Month column {month_column_name} not found.")

        def find_value_for_ee(ee_num):
            pattern = rf'[\u0395E][\u0395E]\s*{ee_num}'
            for row_idx in range(len(df)):
                for col_idx in range(min(5, len(df.columns))):
                    cell_val = str(df.iloc[row_idx, col_idx]).upper()
                    if re.search(pattern, cell_val):
                        # Look for name 'ΤΣΑΒΑΛΙΑΣ' or numeric value near it
                        # For a public repo, we'll make this generic: look for numeric value in target_col
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

        targets = {
            "EE3": find_value_for_ee(3),
            "EE4": find_value_for_ee(4)
        }
        return {k: v for k, v in targets.items() if v > 0}
