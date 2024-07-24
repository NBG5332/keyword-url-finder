import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib3.exceptions import InsecureRequestWarning
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def find_keywords(url, keywords):
    try:
        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Load the page
        driver.get(url)
        
        # Wait for the page to load (adjust the timeout and condition as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Get the rendered HTML content
        html_content = driver.page_source.lower()
        
        # Find matches for each keyword
        matches = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', html_content))
            if count > 0:
                matches[keyword] = count
        
        driver.quit()
        return matches
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# ... (rest of the Streamlit code remains the same)
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
