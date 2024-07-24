import streamlit as st
import subprocess
import pandas as pd

def check_keyword(url, keyword):
    try:
        result = subprocess.run(['curl', '--silent', url], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            grep_result = subprocess.run(['grep', '-i', keyword], input=result.stdout, capture_output=True, text=True)
            return grep_result.stdout.strip() != ''
        else:
            st.error(f"Error fetching {url}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        st.error(f"Timeout while fetching {url}")
        return False
    except Exception as e:
        st.error(f"Unexpected error processing {url}: {e}")
        return False

st.title("Website Plugin Checker")

col1, col2 = st.columns(2)

with col1:
    st.header("List of URLs to Check")
    urls = st.text_area("Enter URLs (one per line)")

with col2:
    st.header("List of plugins to check for")
    default_plugins = "alpineIQ\ntreez\nGoogle-analytics\ngoogleanalytics\ngtag"
    plugins = st.text_area("Enter plugins (one per line)", value=default_plugins)

if st.button("Check Plugins"):
    if urls and plugins:
        url_list = [url.strip() for url in urls.split('\n') if url.strip()]
        plugin_list = [plugin.strip() for plugin in plugins.split('\n') if plugin.strip()]
        
        results = []
        for url in url_list:
            with st.spinner(f"Checking {url}..."):
                found_plugins = [plugin for plugin in plugin_list if check_keyword(url, plugin)]
                if found_plugins:
                    results.append({"URL": url, "Plugins Used": ', '.join(found_plugins)})
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df)
            
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download File in Excel/csv",
                data=csv,
                file_name="plugin_results.csv",
                mime="text/csv",
            )
        else:
            st.warning("No plugins were found on any of the pages.")
    else:
        st.warning("Please enter both URLs and plugins to check.")

st.markdown("""
    <style>
    .small-font {
        font-size:10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="small-font">This would be a big list of all the urls we put in. We might put in a few hundred and get results. The names of the plugins would be separate by commas though we cant display that in balsamiq. Maybe a later version we would have the different types of plugins categorized.</p>', unsafe_allow_html=True)
