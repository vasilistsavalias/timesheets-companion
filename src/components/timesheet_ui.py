import streamlit as st
import pandas as pd
from src.services.llm_client import OpenRouterClient
from src.services.context_loader import ContextLoader
from src.io.excel_parser import ExcelParser
from src.io.exporter import GreekExcelExporter
from src.io.scraper import WebrescomScraper
from src.core.engine import TimesheetEngine
import os
import json
import io
import re
from loguru import logger

def render_timesheet_tool():
    # Helper to load API key securely
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        st.error("🚨 Configuration Error: Missing API Key.")
        return

    # Internal Config
    MODEL = "meta-llama/llama-3.3-70b-instruct:free"
    MONTH_NAME_TO_NUM = {
        'ΙΑΝΟΥΑΡΙΟΣ': 1, 'ΦΕΒΡΟΥΑΡΙΟΣ': 2, 'ΜΑΡΤΙΟΣ': 3, 'ΑΠΡΙΛΙΟΣ': 4,
        'ΜΑΙΟΣ': 5, 'ΙΟΥΝΙΟΣ': 6, 'ΙΟΥΛΙΟΣ': 7, 'ΑΥΓΟΥΣΤΟΣ': 8,
        'ΣΕΠΤΕΜΒΡΙΟΣ': 9, 'ΟΚΤΩΒΡΙΟΣ': 10, 'ΝΟΕΜΒΡΙΟΣ': 11, 'ΔΕΚΕΜΒΡΙΟΣ': 12,
        'JANUARY': 1, 'FEBRUARY': 2, 'MARCH': 3, 'APRIL': 4,
        'MAY': 5, 'JUNE': 6, 'JULY': 7, 'AUGUST': 8,
        'SEPTEMBER': 9, 'OCTOBER': 10, 'NOVEMBER': 11, 'DECEMBER': 12
    }

    # Initialize State
    if "messages" not in st.session_state: st.session_state.messages = []
    if "system_prompt" not in st.session_state:
        with st.spinner("Loading Brain..."):
            loader = ContextLoader()
            st.session_state.system_prompt = loader.get_system_prompt()

    # --- SIDEBAR ---
    with st.sidebar:
        st.header("📂 Project Files")
        uploaded_file = st.file_uploader("1. Upload Niki's Excel", type=['xlsx'])
        if st.button("🔄 Reset Tool"):
            for k in list(st.session_state.keys()):
                if k not in ["authentication_status", "username", "name", "logout", "system_prompt"]:
                    del st.session_state[k]
            st.rerun()

    st.title("🤖 timesheets-companion")
    st.caption(f"Logged in as: **{st.session_state.get('name', 'User')}**")

    # --- PHASE 1: INITIALIZATION ---
    if not st.session_state.get("setup_ready"):
        st.info("Paste the entire Webrescom page content below to begin.")
        ui_paste = st.text_area("Webrescom Content", height=200)
        
        if st.button("🚀 Analyze & Initialize") and uploaded_file and ui_paste:
            with st.spinner("Analyzing inputs..."):
                try:
                    # Load Excel into Memory
                    excel_bytes = uploaded_file.getvalue()
                    temp_path = os.path.join("data", "temp_upload.xlsx") # Temp file for parser compat
                    with open(temp_path, "wb") as f: f.write(excel_bytes)
                    
                    # Scrape
                    scraper = WebrescomScraper(ui_paste)
                    hierarchy, descriptions = scraper.scrape_structure()
                    meta = scraper.get_project_metadata()
                    
                    # Parse Targets
                    parser = ExcelParser(temp_path)
                    raw_ee_targets = parser.get_monthly_targets(meta['month_english'])
                    
                    # Logic
                    final_targets = {}
                    ee_totals = {}
                    for ee, money in raw_ee_targets.items():
                        ee_id = "".join(filter(str.isdigit, ee))
                        match = next((h for h in hierarchy.keys() if ee_id == "".join(filter(str.isdigit, h))), None)
                        if match:
                            delivs = hierarchy[match]
                            money_per = money / len(delivs)
                            ee_totals[match] = round((money / meta['wage']) * 2) / 2
                            for d in delivs: final_targets[d] = money_per

                    st.session_state.update({
                        "excel_bytes": excel_bytes, "excel_name": uploaded_file.name,
                        "hierarchy": hierarchy, "descriptions": descriptions,
                        "project_meta": meta, "final_targets": final_targets, 
                        "ee_totals": ee_totals, "setup_ready": True
                    })
                    
                    # Cleanup Temp
                    if os.path.exists(temp_path): os.remove(temp_path)
                    
                    summary_prompt = (
                        f"DATA LOADED:\n- Month: {meta['month_str']}\n- Targets: {json.dumps(raw_ee_targets, ensure_ascii=False)}\n"
                        f"- Deliverables: {list(final_targets.keys())}\n"
                        f"INSTRUCTION: Summarize and ask for YES to generate."
                    )
                    
                    client = OpenRouterClient(api_key)
                    response = client.chat([{"role": "system", "content": st.session_state.system_prompt}, 
                                          {"role": "user", "content": summary_prompt}])
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"Setup Error: {e}")
                    logger.error(e)

    # --- PHASE 2: GENERATION ---
    if st.session_state.get("setup_ready"):
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        if prompt := st.chat_input("Say YES to generate"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                if any(x in prompt.upper() for x in ["YES", "OK", "PROCEED", "GENERATE"]) and st.session_state.get('setup_ready'):
                    try:
                        with st.spinner("Generating files in memory..."):
                            meta = st.session_state.project_meta
                            month_num = MONTH_NAME_TO_NUM.get(meta['month_english'].upper(), 1)
                            
                            engine = TimesheetEngine(wage=meta['wage'], year=int(meta['year']), month=month_num)
                            schedule = engine.generate_distribution(st.session_state.final_targets)
                            
                            for entry in schedule:
                                entry['Description'] = st.session_state.descriptions.get(entry['Deliverable'], "Ερευνητική εργασία")
                                entry['Date'] = entry['Date'].strftime('%d/%m/%Y')

                            # Use Exporter
                            exporter = GreekExcelExporter(schedule) # No output_dir needed for streams
                            
                            # 1. Detailed Log Stream
                            detailed_stream = exporter.export_excel_stream()
                            
                            # 2. Updated Original Stream
                            original_stream = io.BytesIO(st.session_state.excel_bytes)
                            updated_stream = exporter.update_niki_excel_stream(
                                original_stream, 
                                meta['month_english'], 
                                st.session_state.ee_totals,
                                schedule
                            )
                            
                            st.success("✨ **Files Generated!** (Zero-Disk Persistence)")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button("📥 Detailed Log", detailed_stream, 
                                                 file_name=f"Detailed_{meta['month_english']}.xlsx")
                            with col2:
                                st.download_button("📥 Updated Budget", updated_stream, 
                                                 file_name=f"Updated_{st.session_state.excel_name}")
                                
                    except Exception as e:
                        st.error(f"Generation Failed: {e}")
                        logger.error(e)
                else:
                    client = OpenRouterClient(api_key)
                    response = client.chat(st.session_state.messages)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
