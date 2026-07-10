import streamlit as st
import pandas as pd
import plotly.express as px
import zipfile
import tempfile
import shutil
import os
import pathlib
import json
from pathlib import Path

from core.orchestrator import BSPPipeline
from models.conflict_models import CandidateType

# Page Configuration
st.set_page_config(
    page_title="AI BSP Merge Copilot",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono&display=swap" rel="stylesheet">
    <style>
        /* Force Root Theme Variables */
        :root {
            --primary-color: #00f2fe !important;
            --background-color: #0c0e17 !important;
            --secondary-background-color: rgba(255, 255, 255, 0.03) !important;
            --text-color: #cbd5e0 !important;
        }

        /* Global Background & Font Override */
        .stApp {
            background: radial-gradient(circle at 50% 50%, #151932 0%, #0c0e17 100%) !important;
            font-family: 'Outfit', sans-serif;
        }
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }
        
        .stCodeBlock, code, pre {
            font-family: 'JetBrains Mono', monospace !important;
        }
        
        /* Headers with Neon Accents */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
            font-weight: 700 !important;
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.25) !important;
        }
        
        h3 {
            border-left: 4px solid #00f2fe;
            padding-left: 14px;
            margin-bottom: 20px;
            text-shadow: 0 0 8px rgba(0, 242, 254, 0.3) !important;
        }

        /* Top Header Strip & Decoration Override */
        header[data-testid="stHeader"], .stAppHeader {
            background: rgba(12, 14, 23, 0.9) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        }
        
        div[data-testid="stDecoration"] {
            background: linear-gradient(90deg, #00f2fe, #e100ff) !important;
            height: 4px !important;
        }
        
        /* Sidebar Glassmorphism */
        [data-testid="stSidebar"] {
            background: rgba(10, 12, 23, 0.9) !important;
            backdrop-filter: blur(15px) !important;
            -webkit-backdrop-filter: blur(15px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        }
        
        [data-testid="stSidebar"] h2 {
            text-shadow: 0 0 10px rgba(225, 0, 255, 0.3) !important;
        }
        
        /* Metric Card Styles with Glassmorphism & Neon Glow */
        .metric-card {
            background: rgba(255, 255, 255, 0.02) !important;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(0, 242, 254, 0.15) !important;
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35), inset 0 0 12px rgba(0, 242, 254, 0.05);
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        }
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: rgba(225, 0, 255, 0.45) !important;
            box-shadow: 0 12px 40px 0 rgba(225, 0, 255, 0.25), inset 0 0 12px rgba(225, 0, 255, 0.1);
        }
        .metric-value {
            font-size: 38px;
            font-weight: 700;
            margin-bottom: 6px;
            background: linear-gradient(90deg, #00f2fe, #4facfe, #e100ff) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            text-shadow: 0 0 20px rgba(0, 242, 254, 0.25);
        }
        .metric-label {
            font-size: 13px;
            font-weight: 600;
            color: #a0aec0 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }
        
        /* Glassmorphism Containers */
        .glass-panel {
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        }
        
        /* Custom Status Badges with Neon Glow */
        .status-badge {
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 700;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .badge-ai { 
            background-color: rgba(239, 68, 68, 0.12) !important; 
            color: #ff4d4d !important; 
            border: 1px solid rgba(239, 68, 68, 0.35) !important; 
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.2) !important;
        }
        .badge-auto { 
            background-color: rgba(16, 185, 129, 0.12) !important; 
            color: #10b981 !important; 
            border: 1px solid rgba(16, 185, 129, 0.35) !important; 
            box-shadow: 0 0 15px rgba(16, 185, 129, 0.2) !important;
        }
        .badge-no { 
            background-color: rgba(107, 114, 128, 0.12) !important; 
            color: #cbd5e0 !important; 
            border: 1px solid rgba(107, 114, 128, 0.35) !important; 
            box-shadow: 0 0 10px rgba(107, 114, 128, 0.15) !important;
        }

        /* Buttons Styling with Gradient & Glow */
        .stButton button {
            background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            padding: 12px 24px !important;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(225, 0, 255, 0.45) !important;
            background: linear-gradient(90deg, #00f2fe 0%, #e100ff 100%) !important;
        }

        /* Customize default Streamlit metrics & alerts */
        div[data-testid="stMetricValue"] {
            color: #00f2fe !important;
            font-size: 32px !important;
            font-weight: 700 !important;
            text-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
        }
        div[data-testid="stMetricLabel"] {
            color: #a0aec0 !important;
            font-size: 14px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.5px;
        }

        /* Force readable widget text colors for radio buttons in Light Theme */
        div[data-testid="stRadio"] label {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] p {
            color: #cbd5e0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Main Title & Subheader with premium styling
st.markdown("""
    <div style="text-align: center; margin-bottom: 40px; padding: 20px 0;">
        <h1 style="background: linear-gradient(90deg, #00f2fe, #4facfe, #e100ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 0 25px rgba(0, 242, 254, 0.15); margin-bottom: 12px; font-weight: 700; font-size: 3.2rem; letter-spacing: -0.5px;">AI BSP Merge Copilot 🚀</h1>
        <p style="color: #a0aec0; font-size: 1.2rem; font-weight: 400; max-width: 800px; margin: 0 auto; line-height: 1.6;">Automate three-way BSP analysis between <strong>Base</strong>, <strong>Silicon Vendor</strong>, and <strong>Customer</strong> codebases.</p>
    </div>
""", unsafe_allow_html=True)

# Project Root Resolution
PROJECT_ROOT = Path(__file__).resolve().parent

# Session state initialization
if "contexts" not in st.session_state:
    st.session_state.contexts = None
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = ""

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/nolan/128/artificial-intelligence.png", width=80)
st.sidebar.header("Migration Configuration")

source_option = st.sidebar.radio(
    "Select BSP Dataset Source:",
    ["Preloaded Dataset", "Upload Custom BSP (.zip)"]
)

dataset_path = None
temp_dir_obj = None

if source_option == "Preloaded Dataset":
    preloaded = st.sidebar.selectbox(
        "Choose a dataset:",
        ["complex", "sample", "large"]
    )
    dataset_path = str(PROJECT_ROOT / "datasets" / preloaded)
    st.session_state.dataset_name = f"Preloaded: {preloaded}"
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload BSP ZIP file (must contain base/, vendor/, customer/ directories):",
        type=["zip"]
    )
    if uploaded_file is not None:
        # Create temp folder inside project root datasets to avoid permission issues
        scratch_dir = PROJECT_ROOT / "datasets" / "temp_extracts"
        scratch_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file to a unique temp directory
        temp_dir = tempfile.mkdtemp(dir=str(scratch_dir))
        zip_path = os.path.join(temp_dir, "bsp_archive.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Extract ZIP
        extract_path = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_path, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
            
        # Verify base, vendor, customer subfolders
        # Sometimes ZIP archives wrap them under a single root folder, so let's find them
        valid_bsp_root = extract_path
        subdirs = [d for d in os.listdir(extract_path) if os.path.isdir(os.path.join(extract_path, d))]
        if len(subdirs) == 1 and not ({"base", "vendor", "customer"}.issubset(set(subdirs))):
            valid_bsp_root = os.path.join(extract_path, subdirs[0])
            
        if {"base", "vendor", "customer"}.issubset(set(os.listdir(valid_bsp_root))):
            st.sidebar.success("✅ Valid BSP ZIP Structure detected!")
            dataset_path = valid_bsp_root
            st.session_state.dataset_name = f"Uploaded: {uploaded_file.name}"
        else:
            st.sidebar.error("❌ ZIP must contain 'base/', 'vendor/', and 'customer/' subdirectories.")
            dataset_path = None

run_pipeline = st.sidebar.button("Run Merge Analysis", type="primary", width="stretch")

if run_pipeline:
    if dataset_path:
        with st.spinner("Processing BSP directories & executing AI Copilot agents..."):
            try:
                pipeline = BSPPipeline(dataset_path)
                st.session_state.contexts = pipeline.run()
                st.success("✅ Merge Analysis completed successfully!")
            except Exception as e:
                st.error(f"Error executing pipeline: {e}")
                st.session_state.contexts = None
    else:
        st.sidebar.warning("Please configure or upload a valid dataset first.")

# Check if we have results
if st.session_state.contexts is not None and len(st.session_state.contexts) > 0:
    contexts = st.session_state.contexts
    total_files = len(contexts)
    
    # Calculate Metrics
    ai_review_count = sum(1 for c in contexts if c.candidate.candidate_type == CandidateType.AI_REVIEW)
    auto_merge_count = sum(1 for c in contexts if c.candidate.candidate_type == CandidateType.AUTO_MERGE)
    no_change_count = sum(1 for c in contexts if c.candidate.candidate_type == CandidateType.NO_CHANGE)
    
    total_hours = sum(c.manager.estimated_hours for c in contexts if c.manager is not None)
    avg_confidence = sum(c.reviewer.confidence for c in contexts if c.reviewer is not None) / total_files if total_files > 0 else 0
    
    # 1. Executive Metrics row
    st.markdown("### Executive Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_files}</div><div class="metric-label">Total Files</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{ai_review_count}</div><div class="metric-label">AI Review Files</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{auto_merge_count}</div><div class="metric-label">Auto Merge Files</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_hours:.1f}h</div><div class="metric-label">Est. Dev Effort</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_confidence:.1f}%</div><div class="metric-label">Avg Confidence</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 2. Split Layout: Left side Table, Right side Charts/Download
    left_col, right_col = st.columns([3, 2])
    
    with left_col:
        st.markdown("### Files Directory & Status")
        
        # Prepare DataFrame
        table_data = []
        for ctx in contexts:
            mode = ctx.candidate.candidate_type.value
            risk = ctx.engineer.risk if ctx.engineer else "LOW"
            effort = ctx.manager.effort if ctx.manager else "LOW"
            priority = ctx.manager.priority if ctx.manager else "LOW"
            hours = ctx.manager.estimated_hours if ctx.manager else 0.0
            
            table_data.append({
                "Filename": ctx.bundle.filename,
                "Merge Class": mode,
                "Risk": risk,
                "Effort": effort,
                "Priority": priority,
                "Hours": hours
            })
            
        df = pd.DataFrame(table_data)
        st.dataframe(df, width="stretch")
        
        # File selector for inspector below
        selected_filename = st.selectbox(
            "Select a file to inspect details & AI recommendations:",
            df["Filename"].tolist()
        )
        
    with right_col:
        st.markdown("### Resource & Risk Profiling")
        
        # Draw charts
        conflict_only_df = df[df["Merge Class"] == "AI_REVIEW"]
        if not conflict_only_df.empty:
            # Chart 1: Effort hours by file
            fig_hours = px.bar(
                conflict_only_df,
                x="Filename",
                y="Hours",
                color="Priority",
                title="Estimated Developer-Hours by Conflict File",
                labels={"Hours": "Integration Hours", "Filename": ""},
                template="plotly_dark",
                color_discrete_map={"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}
            )
            st.plotly_chart(fig_hours, width="stretch")
            
            # Chart 2: Scatter plot Complexity vs Risk
            fig_risk = px.scatter(
                conflict_only_df,
                x="Hours",
                y="Risk",
                size="Hours",
                color="Priority",
                hover_name="Filename",
                title="Conflict Complexity Profile Matrix",
                labels={"Hours": "Estimated Integration Hours", "Risk": "Risk Rating"},
                template="plotly_dark",
                size_max=30
            )
            st.plotly_chart(fig_risk, width="stretch")
        else:
            st.info("No AI_REVIEW conflicts detected. All files are AUTO_MERGE or NO_CHANGE.")
            
        # Report Export
        st.markdown("### Export Reports")
        
        # Build Markdown report
        md_report = f"# BSP Migration Analysis Report\n"
        md_report += f"**Dataset name**: {st.session_state.dataset_name}\n\n"
        md_report += f"## Executive Summary\n"
        md_report += f"- Total Files: {total_files}\n"
        md_report += f"- AI Review Candidates: {ai_review_count}\n"
        md_report += f"- Auto Mergeable Files: {auto_merge_count}\n"
        md_report += f"- Total Estimated Integration Time: {total_hours:.1f} hours\n"
        md_report += f"- Average Pipeline Confidence Score: {avg_confidence:.1f}%\n\n"
        
        md_report += "## Conflict Details\n\n"
        for ctx in contexts:
            if ctx.candidate.candidate_type == CandidateType.AI_REVIEW:
                md_report += f"### File: {ctx.bundle.filename} ({ctx.bundle.relative_path})\n"
                md_report += f"- **Merge Recommendation**: {ctx.engineer.recommendation if ctx.engineer else 'N/A'}\n"
                md_report += f"- **Risk Level**: {ctx.engineer.risk if ctx.engineer else 'N/A'}\n"
                md_report += f"- **PM Effort**: {ctx.manager.effort if ctx.manager else 'N/A'} | **Priority**: {ctx.manager.priority if ctx.manager else 'N/A'}\n"
                md_report += f"- **Estimated Integration Hours**: {ctx.manager.estimated_hours if ctx.manager else 'N/A'} hours\n\n"
                md_report += f"#### Engineering Summary\n"
                md_report += f"{ctx.engineer.summary if ctx.engineer else 'N/A'}\n\n"
                md_report += f"#### Architecture Reviewer Validation\n"
                md_report += f"{ctx.reviewer.validation if ctx.reviewer else 'N/A'}\n\n"
                md_report += f"#### Business Impact\n"
                md_report += f"{ctx.manager.business_impact if ctx.manager else 'N/A'}\n\n"
                md_report += "---\n\n"
                
        st.download_button(
            label="Download Complete Markdown Report 📄",
            data=md_report,
            file_name="bsp_migration_report.md",
            mime="text/markdown",
            width="stretch"
        )

    # 3. File Inspector Panel
    if selected_filename:
        ctx = next(c for c in contexts if c.bundle.filename == selected_filename)
        
        st.markdown(f"### 🔍 Detailed Inspection: `{ctx.bundle.filename}`")
        
        # Display Status Badges
        c_mode = ctx.candidate.candidate_type
        if c_mode == CandidateType.AI_REVIEW:
            st.markdown('<span class="status-badge badge-ai">Requires AI Review & Manual Merging</span>', unsafe_allow_html=True)
        elif c_mode == CandidateType.AUTO_MERGE:
            st.markdown('<span class="status-badge badge-auto">Auto Mergeable</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge badge-no">No Changes Detected</span>', unsafe_allow_html=True)
            
        st.write("")
        
        tabs = st.tabs(["⚡ Changes Diff View", "👷 Engineering Analysis", "🛡 Architecture Validation", "💼 Business & PM Metrics"])
        
        with tabs[0]:
            st.markdown("#### Code Diff Explorer")
            col_v, col_c = st.columns(2)
            with col_v:
                st.markdown("**Base ➔ Silicon Vendor modifications**")
                if ctx.diff.vendor_diff:
                    st.code(ctx.diff.vendor_diff, language="diff")
                else:
                    st.info("No modifications made by vendor.")
            with col_c:
                st.markdown("**Base ➔ Customer modifications**")
                if ctx.diff.customer_diff:
                    st.code(ctx.diff.customer_diff, language="diff")
                else:
                    st.info("No modifications made by customer.")
                    
        with tabs[1]:
            st.markdown("#### Engineer Recommendation & Analysis")
            if ctx.engineer:
                st.markdown(f"**Status / Recommendation**")
                st.info(ctx.engineer.recommendation)
                
                st.markdown(f"**Analysis Summary**")
                st.markdown(ctx.engineer.summary)
                
                col_e1, col_e2 = st.columns(2)
                col_e1.metric("Risk Rating", ctx.engineer.risk)
                col_e2.metric("Confidence Score", f"{ctx.engineer.confidence}%")
            else:
                st.warning("No engineering analysis has been run for this file.")
                
        with tabs[2]:
            st.markdown("#### Architectural & Peer Code Review Validation")
            if ctx.reviewer:
                st.markdown(f"**Peer Validation Report**")
                st.success(ctx.reviewer.validation)
                
                col_r1, col_r2 = st.columns(2)
                col_r1.metric("Architecture Risk Assess", ctx.reviewer.risk)
                col_r2.metric("Reviewer Confidence", f"{ctx.reviewer.confidence}%")
            else:
                st.warning("No reviewer verification log has been run.")
                
        with tabs[3]:
            st.markdown("#### Project Management & Integration Metrics")
            if ctx.manager:
                st.markdown(f"**Business & System Impact**")
                st.warning(ctx.manager.business_impact)
                
                col_p1, col_p2, col_p3 = st.columns(3)
                col_p1.metric("Developer Hours Estimate", f"{ctx.manager.estimated_hours} Hours")
                col_p2.metric("Merge Effort Grade", ctx.manager.effort)
                col_p3.metric("Integration Priority", ctx.manager.priority)
            else:
                st.warning("No project management metrics have been run.")

else:
    st.info("👈 Configure the dataset and click 'Run Merge Analysis' in the sidebar to begin.")
