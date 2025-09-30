"""
Low Memory Configuration for VOS Tool
Optimizes the application for free tier cloud instances with limited RAM
"""

import os
import streamlit as st

def configure_low_memory_mode():
    """Configure app for low memory environments (512MB - 1GB RAM)"""
    
    # Set environment variables for memory optimization
    os.environ['STREAMLIT_SERVER_MAX_UPLOAD_SIZE'] = '200'  # 200MB max upload
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    os.environ['STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION'] = 'false'
    
    # Configure Streamlit for low memory
    if 'low_memory_configured' not in st.session_state:
        st.set_page_config(
            layout="wide",
            page_title="VOS Tool - Professional Call Auditor",
            initial_sidebar_state="collapsed"  # Save memory
        )
        st.session_state.low_memory_configured = True

def get_memory_info():
    """Get system memory information"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        return {
            'total_gb': round(memory.total / (1024**3), 1),
            'available_gb': round(memory.available / (1024**3), 1),
            'percent_used': memory.percent
        }
    except ImportError:
        return None

def show_memory_warning():
    """Show memory warning for low-memory systems"""
    memory_info = get_memory_info()
    
    if memory_info and memory_info['total_gb'] < 1.5:
        st.warning(f"""
        ⚠️ **Low Memory System Detected** ({memory_info['total_gb']}GB RAM)
        
        **Recommendations:**
        - Process smaller batches (5-10 files at a time)
        - Avoid uploading files larger than 20MB
        - Close other browser tabs while using this tool
        - Consider upgrading to a larger instance if performance is slow
        """)

def optimize_batch_size(file_count, available_memory_gb=1.0):
    """Optimize batch size based on available memory"""
    if available_memory_gb < 1.0:
        # Very low memory: process 3-5 files at a time
        return min(file_count, 3)
    elif available_memory_gb < 2.0:
        # Low memory: process 5-10 files at a time
        return min(file_count, 8)
    else:
        # Normal memory: process up to 20 files at a time
        return min(file_count, 20)

# Auto-configure if running in low memory environment
def auto_configure():
    """Automatically configure based on detected environment"""
    memory_info = get_memory_info()
    
    if memory_info and memory_info['total_gb'] <= 1.5:
        configure_low_memory_mode()
        return True
    return False

# Check for free tier indicators
def is_free_tier_environment():
    """Detect if running on free tier cloud instance"""
    memory_info = get_memory_info()
    
    # Common free tier memory sizes
    free_tier_indicators = [
        memory_info and memory_info['total_gb'] <= 1.0,  # Oracle/GCP free tier
        'f1-micro' in os.getenv('HOSTNAME', ''),  # GCP
        't2.micro' in os.getenv('HOSTNAME', ''),  # AWS
        os.getenv('ORACLE_CLOUD_FREE') == 'true'
    ]
    
    return any(free_tier_indicators)
