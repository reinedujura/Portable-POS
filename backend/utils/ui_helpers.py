"""Streamlit UI utilities and helpers"""

import streamlit as st
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


def inject_pwa_setup() -> None:
    """Inject PWA (Progressive Web App) setup code into Streamlit"""
    pwa_code = """
    <script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('service-worker.js').then(function(registration) {
            console.log('Service Worker registered:', registration);
        }).catch(function(err) {
            console.log('Service Worker registration failed:', err);
        });
    }

    // Install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        // Show install button
        document.getElementById('install-btn')?.style.display = 'block';
    });

    document.getElementById('install-btn')?.addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            deferredPrompt = null;
        }
    });
    </script>
    """
    st.markdown(pwa_code, unsafe_allow_html=True)


def safe_markdown(text: str, **kwargs) -> None:
    """
    Safely render markdown with error handling.
    
    Args:
        text: Markdown text to render
        **kwargs: Additional arguments for st.markdown
    """
    try:
        if text and isinstance(text, str):
            st.markdown(text, **kwargs)
    except Exception as e:
        logger.error(f"Error rendering markdown: {e}")
        st.warning("Error rendering content")


def apply_global_theme() -> None:
    """Apply consistent theme across Streamlit app"""
    theme_config = """
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1f77b4;
        --background-color: #f0f2f6;
        --secondary-background-color: #ffffff;
        --text-color: #262730;
        --accent-color: #ff6b6b;
    }
    
    /* Streamlit specific styles */
    .stApp {
        background-color: var(--background-color);
    }
    
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #1558a0;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        background-color: var(--secondary-background-color);
        border: 1px solid #d0d3d9;
        border-radius: 4px 4px 0 0;
        margin-right: 2px;
    }
    
    .stTabs [data-baseweb="tab-list"] [aria-selected="true"] button {
        background-color: var(--primary-color);
        color: white;
    }
    
    .stMetric {
        background-color: var(--secondary-background-color);
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .stAlert {
        border-radius: 8px;
    }
    
    .stSuccess {
        background-color: #d1f2eb;
        border: 1px solid #40916c;
    }
    
    .stError {
        background-color: #ffe5e5;
        border: 1px solid #d32f2f;
    }
    
    .stWarning {
        background-color: #fff8dc;
        border: 1px solid #ffa500;
    }
    
    .stInfo {
        background-color: #e3f2fd;
        border: 1px solid #1976d2;
    }
    </style>
    """
    st.markdown(theme_config, unsafe_allow_html=True)


def show_loading_spinner(message: str = "Loading...") -> None:
    """
    Show a loading spinner with message.
    
    Args:
        message: Message to display during loading
    """
    with st.spinner(message):
        pass


def create_sidebar_navigation(menu_items: Dict[str, str]) -> Optional[str]:
    """
    Create a sidebar navigation menu.
    
    Args:
        menu_items: Dictionary of {display_name: page_name}
        
    Returns:
        Selected menu item name or None
    """
    with st.sidebar:
        st.title("Navigation")
        selection = st.radio("Select Page:", list(menu_items.keys()))
        return menu_items.get(selection)


def show_metric_cards(metrics: Dict[str, float], columns: int = 3) -> None:
    """
    Display metrics in card format.
    
    Args:
        metrics: Dictionary of {metric_name: value}
        columns: Number of columns to display
    """
    cols = st.columns(columns)
    for idx, (name, value) in enumerate(metrics.items()):
        with cols[idx % columns]:
            st.metric(name, f"{value:,.2f}" if isinstance(value, (int, float)) else value)


def show_error_message(message: str, title: str = "Error") -> None:
    """Show error message to user"""
    st.error(f"**{title}**: {message}")


def show_success_message(message: str, title: str = "Success") -> None:
    """Show success message to user"""
    st.success(f"**{title}**: {message}")


def show_warning_message(message: str, title: str = "Warning") -> None:
    """Show warning message to user"""
    st.warning(f"**{title}**: {message}")


def show_info_message(message: str, title: str = "Info") -> None:
    """Show info message to user"""
    st.info(f"**{title}**: {message}")


def create_collapsible_section(title: str, content_func, **kwargs) -> None:
    """
    Create a collapsible section in UI.
    
    Args:
        title: Section title
        content_func: Function to call to render content
        **kwargs: Additional arguments to pass to content_func
    """
    with st.expander(title):
        content_func(**kwargs)


def display_data_table(data: List[Dict], title: Optional[str] = None, key: Optional[str] = None) -> None:
    """
    Display data as a table.
    
    Args:
        data: List of dictionaries to display
        title: Optional table title
        key: Optional key for Streamlit component
    """
    if title:
        st.subheader(title)
    
    if data:
        st.dataframe(data, use_container_width=True, key=key)
    else:
        st.info("No data to display")
