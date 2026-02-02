import streamlit as st
import pandas as pd
import json
import re
from src.services.llm_client import OpenRouterClient
from src.services.context_loader import ContextLoader
from src.io.excel_parser import ExcelParser
from src.io.exporter import GreekExcelExporter
from src.io.scraper import WebrescomScraper
from src.core.engine import TimesheetEngine
import os
import io
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

    # --- SIDEBAR INPUTS ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📂 Project Files")
    uploaded_file = st.sidebar.file_uploader("1. Upload Budget Excel", type=['xlsx'])
    
    if st.sidebar.button("🔄 Reset Tool"):
        for k in list(st.session_state.keys()):
            if k not in ["authentication_status", "auth_user", "current_page", "system_prompt"]:
                del st.session_state[k]
        st.rerun()

    st.title("📊 Timesheet Dashboard")
    user = st.session_state.auth_user
    st.caption(f"Logged in as: **{user.name or user.username}**")

    # --- PHASE 1: INITIALIZATION ---
    if not st.session_state.get("setup_ready"):
        st.info("Paste the entire Webrescom page content below to begin.")
        ui_paste = st.text_area("Webrescom Content", height=200)
        
        if st.button("🚀 Analyze & Initialize") and uploaded_file and ui_paste:
            with st.spinner("Analyzing inputs..."):
                try:
                    # 1. Scrape UI
                    scraper = WebrescomScraper(ui_paste)
                    hierarchy, descriptions = scraper.scrape_structure()
                    ui_meta = scraper.get_project_metadata()
                    
                    # 2. Parse Excel (Stream)
                    excel_bytes = uploaded_file.getvalue()
                    excel_stream = io.BytesIO(excel_bytes)
                    parser = ExcelParser(excel_stream)
                    
                    # DYNAMIC METADATA EXTRACTION
                    financial_meta = parser.get_project_metadata()
                    real_wage = financial_meta['wage']
                    real_cap = financial_meta['cap']
                    
                    # 3. Parse Monthly Targets
                    raw_ee_targets = parser.get_monthly_targets(ui_meta['month_english'])
                    
                    # 4. Logic Calculation
                    final_targets = {}
                    ee_totals = {}
                    for ee, money in raw_ee_targets.items():
                        ee_id = "".join(filter(str.isdigit, ee))
                        match = next((h for h in hierarchy.keys() if ee_id == "".join(filter(str.isdigit, h))), None)
                        if match:
                            delivs = hierarchy[match]
                            money_per = money / len(delivs)
                            ee_totals[match] = round((money / real_wage) * 2) / 2
                            for d in delivs: final_targets[d] = money_per

                    st.session_state.update({
                        "excel_bytes": excel_bytes, "excel_name": uploaded_file.name,
                        "hierarchy": hierarchy, "descriptions": descriptions,
                        "project_meta": ui_meta, "financial_meta": financial_meta,
                        "final_targets": final_targets, "ee_totals": ee_totals, 
                        "setup_ready": True
                    })
                    
                    summary_prompt = (
                        f"DATA LOADED:\n"
                        f"- Month: {ui_meta['month_str']}\n"
                        f"- Dynamic Wage (from Excel): {real_wage}€/h\n"
                        f"- Dynamic Cap (from Excel): {real_cap}€\n"
                        f"- Targets: {json.dumps(raw_ee_targets, ensure_ascii=False)}\n"
                        f"- Deliverables: {list(final_targets.keys())}\n"
                        f"INSTRUCTION: Summarize the split and mention the Dynamic Wage and Cap from the excel. Ask for YES to generate."
                    )
                    
                    client = OpenRouterClient(api_key)
                    response = client.chat([{"role": "system", "content": st.session_state.system_prompt}, 
                                          {"role": "user", "content": summary_prompt}])
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
                except Exception as e:
                    st.error(f"Setup Error: {e}")
                    logger.error(e)

    # --- PHASE 2: CHAT & GENERATION ---
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
                            fin_meta = st.session_state.financial_meta
                            month_num = MONTH_NAME_TO_NUM.get(meta['month_english'].upper(), 1)
                            
                            # Use dynamic wage from excel
                            engine = TimesheetEngine(wage=fin_meta['wage'], year=int(meta['year']), month=month_num)
                            schedule = engine.generate_distribution(st.session_state.final_targets)
                            
                            for entry in schedule:
                                entry['Description'] = st.session_state.descriptions.get(entry['Deliverable'], "Ερευνητική εργασία")
                                entry['Date'] = entry['Date'].strftime('%d/%m/%Y')

                            exporter = GreekExcelExporter(schedule)
                            detailed_stream = exporter.export_excel_stream()
                            
                            original_stream = io.BytesIO(st.session_state.excel_bytes)
                            updated_stream = exporter.update_budget_excel_stream(
                                original_stream, 
                                meta['month_english'], 
                                st.session_state.ee_totals,
                                schedule
                            )
                            
                            st.success("✨ **Files Generated!** (In-Memory)")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.download_button("📥 Detailed Log", detailed_stream, file_name=f"Detailed_{meta['month_english']}.xlsx")
                            with col2:
                                st.download_button("📥 Updated Budget", updated_stream, file_name=f"Updated_{st.session_state.excel_name}")
                                
                    except Exception as e:
                        st.error(f"Generation Failed: {e}")
                        logger.error(e)
                else:
                    client = OpenRouterClient(api_key)
                    response = client.chat(st.session_state.messages)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
