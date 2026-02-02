import pytest
from src.io.scraper import WebrescomScraper

@pytest.fixture
def sample_ui_text():
    return """
    Μήνας Ιανουάριος 2026
    Ωρομίσθιο για τη σύμβαση που επιλέξατε: 15,33 €
    
    ΠακέτοΕΕ3 Ανάπτυξη εννοιολογικού
    ΠαραδοτέοΠ3.1 - Έκθεση ερευνητικών
    
    ΠακέτοΕΕ4 Εργαλειοθήκη Τουρισμός
    ΠαραδοτέοΠ4.1 - Διαδικτυακή εφαρμογή
    ΠαραδοτέοΠ4.2 - Κόμβος Ψηφιακών
    """

def test_scraper_meta(sample_ui_text):
    scraper = WebrescomScraper(sample_ui_text)
    meta = scraper.get_project_metadata()
    assert meta['wage'] == 15.33
    assert meta['month_english'] == "JANUARY"
    assert "2026" in meta['month_str']

def test_scraper_structure(sample_ui_text):
    scraper = WebrescomScraper(sample_ui_text)
    hierarchy, descriptions = scraper.scrape_structure()
    
    # Use Greek ΕΕ as found in the portal
    assert "\u0395\u03953" in hierarchy
    assert "\u0395\u03954" in hierarchy
    assert "\u03a03.1" in hierarchy["\u0395\u03953"]
    assert "\u03a04.1" in hierarchy["\u0395\u03954"]
    assert "\u03a04.2" in hierarchy["\u0395\u03954"]
    assert "\u03a03.1" in descriptions
