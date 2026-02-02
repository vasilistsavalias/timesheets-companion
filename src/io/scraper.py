import re

class WebrescomScraper:
    def __init__(self, content):
        self.content = content
        self.month_map = {
            'ιανουάριος': 'JANUARY', 'φεβρουάριος': 'FEBRUARY', 'μάρτιος': 'MARCH',
            'απρίλιος': 'APRIL', 'μάιος': 'MAY', 'ιούνιος': 'JUNE',
            'ιούλιος': 'JULY', 'αύγουστος': 'AUGUST', 'σεπτέμβριος': 'SEPTEMBER',
            'οκτώβριος': 'OCTOBER', 'νοέμβριος': 'NOVEMBER', 'δεκεμβρίου': 'DECEMBER',
            'ιανουαρίου': 'JANUARY', 'φεβρουαρίου': 'FEBRUARY', 'μαρτίου': 'MARCH',
            'απριλίου': 'APRIL', 'μαΐου': 'MAY', 'ιουνίου': 'JUNE',
            'ιουλίου': 'JULY', 'αυγούστου': 'AUGUST', 'σεπτεμβρίου': 'SEPTEMBER',
            'οκτωβρίου': 'OCTOBER', 'νοεμβρίου': 'NOVEMBER', 'δεκεμβρίου': 'DECEMBER'
        }

    def get_project_metadata(self):
        """Extracts wage and month from the UI text."""
        # Wage extraction
        wage_match = re.search(r'Ωρομίσθιο.*?:.*?([\d,.]+)', self.content)
        wage = float(wage_match.group(1).replace(',', '.')) if wage_match else 15.33
        
        # Month extraction (e.g., Ιανουάριος 2026)
        month_match = re.search(r'Μήνας\s+([α-ωΑ-Ωίΐήήύΰέέόόώώ]+)\s+(\d{4})', self.content, re.IGNORECASE)
        if month_match:
            greek_month = month_match.group(1).lower()
            year = month_match.group(2)
            english_month = self.month_map.get(greek_month, "JANUARY")
            return {
                "wage": wage, 
                "month_greek": month_match.group(1),
                "month_english": english_month,
                "year": year,
                "month_str": f"{month_match.group(1)} {year}"
            }
        
        return {"wage": wage, "month_greek": "Ιανουάριος", "month_english": "JANUARY", "year": "2026", "month_str": "Ιανουάριος 2026"}

    def scrape_structure(self):
        """
        Dynamically builds the hierarchy of Packages and Deliverables.
        Handles cases like 'ΠακέτοΕΕ3' (no space).
        """
        hierarchy = {}
        descriptions = {}
        current_package = None
        
        lines = self.content.split('\n')
        for line in lines:
            line = line.strip()
            if not line: continue
            
            # 1. Identify Package (EE)
            pkg_match = re.search(r'Πακέτο\s*(ΕΕ\d+)', line, re.IGNORECASE)
            if pkg_match:
                current_package = pkg_match.group(1).upper()
                if current_package not in hierarchy:
                    hierarchy[current_package] = []
                continue
            
            # 2. Identify Deliverable (Π)
            if current_package:
                deliv_match = re.search(r'Παραδοτέο\s*(Π[\d\.]+)\s*[-–—]?\s*(.*)', line, re.IGNORECASE)
                if deliv_match:
                    code = deliv_match.group(1)
                    desc = deliv_match.group(2).strip()
                    
                    if code not in hierarchy[current_package]:
                        hierarchy[current_package].append(code)
                    
                    descriptions[code] = f"{desc} ({code})" if desc else f"Ερευνητική εργασία ({code})"
                    
        return hierarchy, descriptions