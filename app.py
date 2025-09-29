import io
import tempfile
from pathlib import Path
from datetime import date, datetime

import pandas as pd
import streamlit as st

from analyzer.simple_main import batch_analyze_folder, batch_analyze_folder_fast
from config import READYMODE_URL, USER_CREDENTIALS
import os

# Try to import ReadyMode automation, disable if not available (e.g., on Streamlit Cloud)
try:
    from automation.download_readymode_calls import download_all_call_recordings
    READYMODE_AVAILABLE = True
except ImportError as e:
    READYMODE_AVAILABLE = False
    st.warning("ReadyMode automation not available in this environment. Upload & Analyze functionality is still available.")

st.set_page_config(layout="wide", page_title="VOS Tool - Fast Call Auditor")

# Custom CSS for modern card-based UI
def load_custom_css():
    st.markdown("""
    <style>
    /* VOS Tool Platform Theme */
    .stApp {
        background: #0d1117;
        min-height: 100vh;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Platform Header */
    .platform-header {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #30363d;
        margin-bottom: 2rem;
    }
    
    .platform-title {
        color: #f0f6fc;
        font-size: 2.25rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    
    .platform-subtitle {
        color: #58a6ff;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 0;
    }
    
    .platform-badge {
        display: inline-block;
        background: #238636;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 0.5rem;
        vertical-align: middle;
    }
    
    /* Platform Modules */
    .platform-module {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
    }
    
    .module-header {
        color: #f0f6fc;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .module-description {
        color: #8b949e;
        text-align: center;
        margin-bottom: 2rem;
        line-height: 1.5;
    }
    
    /* Technical Input Styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div,
    .stDateInput > div > div > input,
    .stNumberInput > div > div > input {
        background: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #f0f6fc !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.875rem !important;
        font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > div:focus,
    .stMultiSelect > div > div > div:focus,
    .stDateInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #58a6ff !important;
        box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.2) !important;
        outline: none !important;
    }
    
    /* Platform Labels */
    .stTextInput > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stDateInput > label,
    .stNumberInput > label {
        color: #f0f6fc !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Platform Buttons */
    .stButton > button {
        background: #21262d !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: auto !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stButton > button:hover {
        background: #30363d !important;
        border-color: #484f58 !important;
        transform: translateY(-1px);
    }
    
    .stButton > button:disabled {
        background: #21262d !important;
        border-color: #30363d !important;
        color: #484f58 !important;
        cursor: not-allowed !important;
        transform: none !important;
    }
    
    /* Platform Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: #161b22;
        border-radius: 8px;
        padding: 4px;
        border: 1px solid #30363d;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 6px;
        color: #8b949e;
        padding: 0.75rem 1.5rem;
        border: none;
        font-weight: 500;
        transition: all 0.2s ease;
        flex: 1;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #1c6beb;
        color: #ffffff;
    }
    
    /* Technical Sections */
    .tech-section {
        margin: 1.5rem 0;
    }
    
    .section-label {
        color: #f0f6fc;
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        display: block;
    }
    
    .section-help {
        color: #8b949e;
        font-size: 0.75rem;
        margin-top: 0.25rem;
        font-style: italic;
    }
    
    /* Status Indicators */
    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.75rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 0.125rem;
    }
    
    .pill-success {
        background: rgba(63, 185, 80, 0.15);
        color: #3fb950;
        border: 1px solid rgba(63, 185, 80, 0.3);
    }
    
    .pill-warning {
        background: rgba(210, 153, 34, 0.15);
        color: #d29922;
        border: 1px solid rgba(210, 153, 34, 0.3);
    }
    
    .pill-error {
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.3);
    }
    
    .pill-info {
        background: rgba(88, 166, 255, 0.15);
        color: #58a6ff;
        border: 1px solid rgba(88, 166, 255, 0.3);
    }
    
    /* Platform Sidebar */
    .css-1d391kg {
        background: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }
    
    /* Sidebar logout button styling */
    .css-1d391kg .stButton > button {
        background: #21262d !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    .css-1d391kg .stButton > button:hover {
        background: #30363d !important;
        border-color: #484f58 !important;
        color: #ffffff !important;
    }
    
    .user-context {
        padding: 1rem;
        background: #0d1117;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #30363d;
    }
    
    .user-name {
        color: #f0f6fc;
        font-weight: 600;
        font-size: 0.875rem;
    }
    
    .user-role {
        color: #8b949e;
        font-size: 0.75rem;
    }
    
    /* Detection Matrix */
    .detection-matrix {
        background: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .matrix-item {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }
    
    .matrix-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.75rem;
        flex-shrink: 0;
    }
    
    .indicator-critical {
        background: #f85149;
    }
    
    .indicator-warning {
        background: #d29922;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: #161b22 !important;
        border: 2px dashed #30363d !important;
        border-radius: 8px !important;
        padding: 2rem !important;
        text-align: center !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }
    
    .stFileUploader > div:hover {
        border-color: #58a6ff !important;
        background: #1c2128 !important;
    }
    
    /* Success/error messages */
    .stSuccess {
        background: rgba(63, 185, 80, 0.15) !important;
        color: #3fb950 !important;
        border: 1px solid rgba(63, 185, 80, 0.3) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stError {
        background: rgba(248, 81, 73, 0.15) !important;
        color: #f85149 !important;
        border: 1px solid rgba(248, 81, 73, 0.3) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    .stInfo {
        background: rgba(88, 166, 255, 0.15) !important;
        color: #58a6ff !important;
        border: 1px solid rgba(88, 166, 255, 0.3) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: #58a6ff !important;
        border-radius: 4px !important;
    }
    
    /* Column spacing improvements */
    .row-widget.stHorizontal {
        gap: 1rem;
    }
    
    /* Text styling */
    .stMarkdown p {
        color: #8b949e !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    /* Hide default elements */
    .stDeployButton { display: none; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

def show_login_page():
    """Display the professional login page."""
    # Add login-specific CSS
    st.markdown("""
    <style>
    /* Login page specific styling */
    .login-header {
        background: linear-gradient(135deg, #161b22 0%, #1c2128 100%);
        padding: 2rem;
        border-bottom: 1px solid #30363d;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
    }
    
    .login-title {
        color: #f0f6fc;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .login-subtitle {
        color: #58a6ff;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 0;
    }
    
    .login-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 16px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 450px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Ensure form elements are styled within the card */
    .stForm {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 16px !important;
        padding: 3rem !important;
        margin: 2rem auto !important;
        max-width: 450px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
    }
    
    .login-card-title {
        color: #f0f6fc;
        font-size: 1.75rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 0.75rem;
    }
    
    .login-card-description {
        color: #8b949e;
        text-align: center;
        margin-bottom: 2.5rem;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Enhanced login button */
    .stForm .stButton > button {
        background: linear-gradient(135deg, #21262d 0%, #30363d 100%) !important;
        color: #f0f6fc !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 1rem 2rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        height: auto !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(33, 38, 45, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stForm .stButton > button:hover {
        background: linear-gradient(135deg, #30363d 0%, #484f58 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(48, 54, 61, 0.4) !important;
    }
    
    .login-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #0d1117;
        border-top: 1px solid #30363d;
        padding: 1rem;
        text-align: center;
        color: #8b949e;
        font-size: 0.75rem;
    }
    
    .login-footer a {
        color: #58a6ff;
        text-decoration: none;
    }
    
    .login-footer a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Login Header
    st.markdown("""
    <div class="login-header">
        <div class="login-title">
            VOS Tool
            <span class="platform-badge">v2.1</span>
        </div>
        <div class="login-subtitle">
            Python-Powered Call Auditing Platform
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create login form
        with st.form("login_form"):
            st.markdown('<div class="login-card-title">Authentication Required</div>', unsafe_allow_html=True)
            st.markdown('<div class="login-card-description">Please enter your credentials to access the enterprise call auditing platform</div>', unsafe_allow_html=True)
            
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            login_button = st.form_submit_button("Authenticate", use_container_width=True)
            
            if login_button:
                if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"Welcome, {username}! Redirecting to platform...")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please verify your username and password.")
    
    # Login Footer
    st.markdown("""
    <div class="login-footer">
        VOS Tool Enterprise Platform • Developed by Windsurf Engineering • Secure Authentication System
    </div>
    """, unsafe_allow_html=True)

def show_logout_button():
    """Display logout button in sidebar."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"**Logged in as:** {st.session_state.get('username', 'Unknown')}")
        if st.button("Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def check_authentication():
    """Check if user is authenticated."""
    return st.session_state.get('authenticated', False)

def _maybe_set_ffmpeg_converter() -> bool:
    """Set FFmpeg path if available."""
    try:
        from pydub import AudioSegment
        # Check for bundled ffmpeg
        ffmpeg_bin = Path(__file__).parent / "ffmpeg" / "bin" / "ffmpeg.exe"
        if ffmpeg_bin.exists():
            AudioSegment.converter = str(ffmpeg_bin)
            return True
        # Check system ffmpeg
        import shutil
        if shutil.which("ffmpeg"):
            return True
    except Exception:
        return False
    return False

def _to_excel(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Flagged Calls")
    return output.getvalue()

def main():
    load_custom_css()
    
    # Check authentication first
    if not check_authentication():
        show_login_page()
        return
    
    # Show logout button for authenticated users
    show_logout_button()
    
    ffmpeg_ok = _maybe_set_ffmpeg_converter()

    # Platform Header
    st.markdown("""
    <div class="platform-header">
        <div class="platform-title">
            VOS Tool
            <span class="platform-badge">v2.1</span>
        </div>
        <div class="platform-subtitle">
            Python-Powered Call Auditing Platform • Enterprise Ready
        </div>
    </div>
    """, unsafe_allow_html=True)
    

    # Progress tracker helper
    def _create_progress_tracker():
        status_text = st.empty()
        progress_bar = st.progress(0)
        def update_progress(downloaded, total):
            try:
                ratio = downloaded / total if total else 0
            except:
                ratio = float(downloaded)
            progress_bar.progress(min(max(ratio, 0.0), 1.0))
            if isinstance(downloaded, (int, float)) and isinstance(total, (int, float)) and total:
                status_text.text(f"Processing: {int(min(downloaded, total))}/{int(total)}")
        return status_text, progress_bar, update_progress

    tab_upload, tab_agent, tab_campaign = st.tabs(["Upload & Analyze", "Agent Audit", "Campaign Audit"])

    # --- Upload & Analyze Tab ---
    with tab_upload:
        # Module Header
        st.markdown('<div class="module-header">File Analysis Module</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-description">Batch processing of audio files with real-time detection algorithms</div>', unsafe_allow_html=True)
        
        # Detection Matrix
        st.markdown("""
        <div class="detection-matrix">
            <div class="section-label">Detection Algorithms</div>
            <div class="matrix-item">
                <div class="matrix-indicator indicator-critical"></div>
                <div>
                    <strong>Releasing Detection</strong>
                    <div class="section-help">Identifies calls where agent speech is completely absent</div>
                </div>
            </div>
            <div class="matrix-item">
                <div class="matrix-indicator indicator-warning"></div>
                <div>
                    <strong>Late Hello Detection</strong>
                    <div class="section-help">Flags calls with agent response time > 4 seconds</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # File Upload Section
        st.markdown('<div class="section-label">Audio File Input</div>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Select MP3/WAV files for processing",
            type=["mp3", "wav"],
            accept_multiple_files=True,
            help="Supported formats: MP3, WAV. Maximum batch size: 1000 files"
        )
        
        # File Processing Status
        if uploaded_files:
            st.markdown(f'<div class="status-pill pill-info">Files Queued: {len(uploaded_files)}</div>', unsafe_allow_html=True)
        
        # Processing Action
        analyze_button = st.button(
            "Execute Analysis", 
            disabled=not uploaded_files, 
            key="upload_analyze_btn", 
            use_container_width=True
        )

        if analyze_button:
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_path = Path(tmpdir)
                for f in uploaded_files:
                    (temp_path / f.name).write_bytes(f.getbuffer())

                with st.spinner(f"Analyzing {len(uploaded_files)} files..."):
                    df = batch_analyze_folder(str(temp_path))
                    st.session_state["upload_results"] = df

        if "upload_results" in st.session_state:
            df = st.session_state["upload_results"]
            if not df.empty:
                st.success(f"Found {len(df)} flagged calls!")
                st.dataframe(df, use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download CSV",
                        data=df.to_csv(index=False).encode("utf-8"),
                        file_name="flagged_calls.csv",
                        mime="text/csv",
                    )
                with col2:
                    st.download_button(
                        label="Download Excel",
                        data=_to_excel(df),
                        file_name="flagged_calls.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
            else:
                st.info("No issues detected in uploaded files.")

    # --- Agent Audit Tab ---
    with tab_agent:
        # Module Header
        st.markdown('<div class="module-header">Agent Performance Module</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-description">Comprehensive agent call analysis with advanced filtering</div>', unsafe_allow_html=True)
        
        # Configuration Sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-label">Agent Configuration</div>', unsafe_allow_html=True)
            ready_url = st.text_input("ReadyMode URL", value=READYMODE_URL, key="agent_url")
            agent_name = st.text_input("Agent Identifier", key="agent_name", placeholder="Enter exact agent name")
        
        with col2:
            st.markdown('<div class="section-label">Date Parameters</div>', unsafe_allow_html=True)
            start_date = st.date_input("Start Date", value=date.today(), key="agent_start")
            end_date = st.date_input("End Date", value=date.today(), key="agent_end")
        
        # Advanced Filters
        st.markdown('<div class="section-label">Advanced Filters</div>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            dispositions_options = [
                "Spanish Speaker", "DNC - Unknown", "Unknown", "Influencer", "Agent",
                "DNC - Decision Maker", "Decision Maker - Lead", "Callback", "Wrong Number",
                "Voicemail", "Decision Maker - NYI", "Dead Call", "Listed Property", "Prank Voicemail", "Not logged"
            ]
            selected_dispositions = st.multiselect("Call Dispositions", options=dispositions_options, key="agent_dispositions")
        
        with col4:
            duration_option = st.selectbox(
                "Duration Filter",
                [
                    "All durations",
                    "Less than 30 seconds",
                    "30 seconds - 1:00",
                    "1:00 to 10:00",
                    "Greater than...",
                    "Less than..."
                ],
                index=0,
                key="agent_duration_filter"
            )
        
        # Handle duration filter logic
        min_duration, max_duration = None, None
        if duration_option == "Less than 30 seconds":
            max_duration = 30
        elif duration_option == "30 seconds - 1:00":
            min_duration, max_duration = 30, 60
        elif duration_option == "1:00 to 10:00":
            min_duration, max_duration = 60, 600
        elif duration_option == "Greater than...":
            min_duration = st.number_input("Greater than (seconds)", min_value=0, value=60, key="agent_min_duration")
        elif duration_option == "Less than...":
            max_duration = st.number_input("Less than (seconds)", min_value=1, value=30, key="agent_max_duration")
        
        # Sample Configuration
        st.markdown('<div class="section-label">Processing Parameters</div>', unsafe_allow_html=True)
        num_recordings = st.number_input("Number of samples", min_value=1, max_value=1000, value=50, key="agent_num",
                                       help="Number of recordings to analyze for statistical significance")
        
        # Execution
        download_button = st.button("Execute Agent Audit", key="agent_download_btn", use_container_width=True)

        # Handle button click
        if download_button:
            if not agent_name:
                st.error("Please enter an agent name.")
            else:
                if not READYMODE_AVAILABLE:
                    st.error("ReadyMode automation is not available in this environment. Please use the Upload & Analyze tab to process local audio files.")
                else:
                    status_text, progress_bar, update_progress = _create_progress_tracker()
                    with st.spinner("Downloading and analyzing agent recordings..."):
                        try:
                            max_samples = int(num_recordings) if num_recordings else 50

                            download_all_call_recordings(
                                ready_url,
                                agent=agent_name,
                                start_date=start_date,
                                end_date=end_date,
                                max_samples=max_samples,
                                update_callback=update_progress,
                                disposition=selected_dispositions,
                                min_duration=min_duration,
                                max_duration=max_duration,
                                username=None,
                            )
                            progress_bar.empty()
                            status_text.empty()

                            # Analyze downloaded files - Fix path to match download location
                            today = datetime.now().strftime('%Y-%m-%d')
                            
                            # Import USERNAME from download module to match exact path
                            if READYMODE_AVAILABLE:
                                from automation.download_readymode_calls import USERNAME
                            else:
                                USERNAME = "default"
                            
                            # The download function creates: Recordings/Agent/{USERNAME}/{agent}-{today}/
                            expected_path = Path(f"Recordings/Agent/{USERNAME}/{agent_name}-{today}")
                        except Exception as e:
                            st.error(f"Error during download: {str(e)}")
                            return
                        
                        st.info(f" Looking for files in: {expected_path}")
                        
                        target_folder = None
                        files = []
                        
                        # Check the exact expected path first
                        if expected_path.exists():
                            files = list(expected_path.glob("*.mp3"))
                            if files:
                                target_folder = expected_path
                                st.success(f" Found {len(files)} files in expected location: {expected_path}")
                        
                        # If not found, try alternative paths
                        if not files:
                            alternative_paths = [
                                Path(f"Recordings/Agent/{agent_name}-{today}"),  # Legacy path
                                Path(f"Recordings/Agent/Auditor1/{agent_name}-{today}"),  # Hardcoded fallback
                                Path(f"Recordings/Agent/{USERNAME}/{today}"),  # Date-only folder
                            ]
                            
                            for path in alternative_paths:
                                if path.exists():
                                    path_files = list(path.glob("*.mp3"))
                                    if path_files:
                                        target_folder = path
                                        files = path_files
                                        st.info(f"[DIR] Found {len(files)} files in alternative location: {path}")
                                        break
                        
                        # Last resort: recursive search
                        if not files:
                            st.warning(" Searching recursively for any matching files...")
                            recordings_base = Path("Recordings")
                            if recordings_base.exists():
                                # Look for any MP3 files in any subdirectory
                                all_mp3s = list(recordings_base.rglob("*.mp3"))
                                if all_mp3s:
                                    # Filter by agent name if possible
                                    agent_files = [f for f in all_mp3s if agent_name.lower() in f.name.lower()]
                                    if agent_files:
                                        # Use the parent directory of the first matching file
                                        target_folder = agent_files[0].parent
                                        files = list(target_folder.glob("*.mp3"))
                                        st.info(f" Found {len(files)} files by recursive search in: {target_folder}")
                                    else:
                                        st.warning(f"No files matching agent '{agent_name}' found.")
                        
                        if not files:
                            st.error(f"No files found for agent '{agent_name}' on {today}")
                            st.info("Please check that the agent name is correct and files have been downloaded.")
                        else:
                            processing_status = st.empty()
                            processing_progress = st.progress(0)
                            def on_progress(done, total):
                                try:
                                    ratio = done/total if total else 0
                                    processing_progress.progress(ratio)
                                    processing_status.text(f"Analyzing: {done}/{total}")
                                except Exception as e:
                                    st.error(f"Progress callback error: {e}")
                                    st.text(f"Arguments received: done={done}, total={total}")
                            
                            try:
                                df = batch_analyze_folder_fast(str(target_folder), progress_callback=on_progress)
                            except Exception as e:
                                st.error(f"Agent analysis failed: {e}")
                                st.text(f"Target folder: {target_folder}")
                                # Try without progress callback as fallback
                                df = batch_analyze_folder_fast(str(target_folder), progress_callback=None)
                            
                            processing_progress.empty()
                            processing_status.empty()
                            
                            if not df.empty:
                                st.success(f"Found {len(df)} flagged calls!")
                                st.dataframe(df, use_container_width=True)
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label="Download CSV",
                                        data=df.to_csv(index=False).encode("utf-8"),
                                        file_name="agent_audit.csv",
                                        mime="text/csv",
                                    )
                                with col2:
                                    st.download_button(
                                        label="Download Excel",
                                        data=_to_excel(df),
                                        file_name="agent_audit.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    )
                            else:
                                st.info(" No Releasing or Late Hello detected.")

    # --- Campaign Audit Tab ---
    with tab_campaign:
        # Module Header
        st.markdown('<div class="module-header">Campaign Performance Module</div>', unsafe_allow_html=True)
        st.markdown('<div class="module-description">Configure audit parameters and download campaign call recordings</div>', unsafe_allow_html=True)
        
        # Configuration Sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-label">Campaign Configuration</div>', unsafe_allow_html=True)
            ready_url = st.text_input("ReadyMode URL", value=READYMODE_URL, key="camp_url")
            campaign_name = st.text_input("Campaign Name", key="camp_name", placeholder="Enter exact campaign name")
        
        with col2:
            st.markdown('<div class="section-label">Date Parameters</div>', unsafe_allow_html=True)
            start_date = st.date_input("Start Date", value=date.today(), key="camp_start")
            end_date = st.date_input("End Date", value=date.today(), key="camp_end")
        
        # Optional Agent Filter
        agent_name = st.text_input("Agent Name (optional)", key="camp_agent", placeholder="Leave blank for all agents")
        
        # Advanced Filters
        st.markdown('<div class="section-label">Advanced Filters</div>', unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            dispositions_options = [
                "Spanish Speaker", "DNC - Unknown", "Unknown", "Influencer", "Agent",
                "DNC - Decision Maker", "Decision Maker - Lead", "Callback", "Wrong Number",
                "Voicemail", "Decision Maker - NYI", "Dead Call", "Listed Property", "Prank Voicemail", "Not logged"
            ]
            selected_dispositions = st.multiselect("Call Dispositions", options=dispositions_options, key="camp_dispositions", placeholder="Choose all options")
        
        with col4:
            duration_option = st.selectbox(
                "Duration Filter",
                [
                    "All durations",
                    "Less than 30 seconds",
                    "30 seconds - 1:00",
                    "1:00 to 10:00",
                    "Greater than...",
                    "Less than..."
                ],
                index=0,
                key="camp_duration_filter"
            )
        
        # Handle duration filter logic
        min_duration, max_duration = None, None
        if duration_option == "Less than 30 seconds":
            max_duration = 30
        elif duration_option == "30 seconds - 1:00":
            min_duration, max_duration = 30, 60
        elif duration_option == "1:00 to 10:00":
            min_duration, max_duration = 60, 600
        elif duration_option == "Greater than...":
            min_duration = st.number_input("Greater than (seconds)", min_value=0, value=60, key="camp_min_duration")
        elif duration_option == "Less than...":
            max_duration = st.number_input("Less than (seconds)", min_value=1, value=30, key="camp_max_duration")

        # Sample Configuration
        st.markdown('<div class="section-label">Processing Parameters</div>', unsafe_allow_html=True)
        num_recordings = st.number_input("Number of samples", min_value=1, max_value=1000, value=50, key="camp_num",
                                       help="Number of recordings to analyze for statistical significance")

        # Execution
        campaign_button = st.button("Execute Campaign Audit", key="campaign_download_btn", use_container_width=True)

        if campaign_button:
            if not campaign_name:
                st.error("Please enter a campaign name.")
            else:
                if not READYMODE_AVAILABLE:
                    st.error("ReadyMode automation is not available in this environment. Please use the Upload & Analyze tab to process local audio files.")
                else:
                    status_text, progress_bar, update_progress = _create_progress_tracker()
                    with st.spinner("Downloading and analyzing campaign recordings..."):
                        try:
                            max_samples = int(num_recordings) if num_recordings else 50

                            download_all_call_recordings(
                                ready_url,
                                campaign_name=campaign_name,
                                agent=agent_name if agent_name else None,
                                start_date=start_date,
                                end_date=end_date,
                                max_samples=max_samples,
                                update_callback=update_progress,
                                disposition=selected_dispositions,
                                min_duration=min_duration,
                                max_duration=max_duration,
                            username=None,
                            )
                            progress_bar.empty()
                            status_text.empty()

                            # Analyze downloaded files - Fix path to match download location
                            today = datetime.now().strftime('%Y-%m-%d')
                            
                            # Import USERNAME from download module to match exact path
                            if READYMODE_AVAILABLE:
                                from automation.download_readymode_calls import USERNAME
                            else:
                                USERNAME = "default"
                            
                            # The download function creates: Recordings/Campaign/{USERNAME}/{campaign}-{today}/
                            expected_path = Path(f"Recordings/Campaign/{USERNAME}/{campaign_name}-{today}")
                        except Exception as e:
                            st.error(f"Error during download: {str(e)}")
                            return
                        
                        st.info(f" Looking for files in: {expected_path}")
                        
                        target_folder = None
                        files = []
                        
                        # Check the exact expected path first
                        if expected_path.exists():
                            files = list(expected_path.glob("*.mp3"))
                            if files:
                                target_folder = expected_path
                                st.success(f" Found {len(files)} files in expected location: {expected_path}")
                        
                        # If not found, try alternative paths
                        if not files:
                            alternative_paths = [
                                Path(f"Recordings/Campaign/{campaign_name}-{today}"),  # Legacy path
                                Path(f"Recordings/Campaign/Auditor1/{campaign_name}-{today}"),  # Hardcoded fallback
                                Path(f"Recordings/Campaign/{USERNAME}/{today}"),  # Date-only folder
                            ]
                            
                            for path in alternative_paths:
                                if path.exists():
                                    path_files = list(path.glob("*.mp3"))
                                    if path_files:
                                        target_folder = path
                                        files = path_files
                                        st.info(f"[DIR] Found {len(files)} files in alternative location: {path}")
                                        break
                        
                        # Last resort: recursive search
                        if not files:
                            st.warning(" Searching recursively for any matching files...")
                            recordings_base = Path("Recordings")
                            if recordings_base.exists():
                                # Look for any MP3 files in any subdirectory
                                all_mp3s = list(recordings_base.rglob("*.mp3"))
                                if all_mp3s:
                                    # Filter by campaign name if possible
                                    campaign_files = [f for f in all_mp3s if campaign_name.lower() in f.parent.name.lower()]
                                    if campaign_files:
                                        # Use the parent directory of the first matching file
                                        target_folder = campaign_files[0].parent
                                        files = list(target_folder.glob("*.mp3"))
                                        st.info(f" Found {len(files)} files by recursive search in: {target_folder}")
                                    else:
                                        st.warning(f"No files matching campaign '{campaign_name}' found.")
                        
                        if not files:
                            st.error(f"No files found for campaign '{campaign_name}' on {today}")
                            st.info("Please check that the campaign name is correct and files have been downloaded.")
                        else:
                            processing_status = st.empty()
                            processing_progress = st.progress(0)
                            def on_progress(done, total):
                                try:
                                    ratio = done/total if total else 0
                                    processing_progress.progress(ratio)
                                    processing_status.text(f"Analyzing: {done}/{total}")
                                except Exception as e:
                                    st.error(f"Progress callback error: {e}")
                                    st.text(f"Arguments received: done={done}, total={total}")
                            
                            try:
                                df = batch_analyze_folder_fast(str(target_folder), progress_callback=on_progress)
                            except Exception as e:
                                st.error(f"Campaign analysis failed: {e}")
                                st.text(f"Target folder: {target_folder}")
                                # Try without progress callback as fallback
                                df = batch_analyze_folder_fast(str(target_folder), progress_callback=None)
                            
                            processing_progress.empty()
                            processing_status.empty()
                            
                            if not df.empty:
                                st.success(f"Found {len(df)} flagged calls!")
                                st.dataframe(df, use_container_width=True)
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label="Download CSV",
                                        data=df.to_csv(index=False).encode("utf-8"),
                                        file_name="campaign_audit.csv",
                                        mime="text/csv",
                                    )
                                with col2:
                                    st.download_button(
                                        label="Download Excel",
                                        data=_to_excel(df),
                                        file_name="campaign_audit.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    )
                            else:
                                st.info(" No Releasing or Late Hello detected.")

if __name__ == "__main__":
    main()