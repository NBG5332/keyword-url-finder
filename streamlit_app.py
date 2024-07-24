import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def find_keywords(url, keywords):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        html_content = soup.get_text().lower()
        
        matches = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', html_content))
            if count > 0:
                matches[keyword] = count
        return matches
    except requests.RequestException as e:
        st.error(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

st.title("Keyword Finder")

url = st.text_input("Enter the URL to inspect:")
keywords_input = st.text_input("Enter keywords to search for (comma-separated):")

if st.button("Search"):
    if url and keywords_input:
        keywords = [k.strip() for k in keywords_input.replace(' ', '').split(',')]
        
        results = find_keywords(url, keywords)
        
        if results is not None:
            if results:
                st.subheader("Keywords found:")
                for keyword, count in results.items():
                    st.write(f"'{keyword}': {count} occurrences")
                
                not_found = set(keywords) - set(results.keys())
                if not_found:
                    st.subheader("Keywords not found:")
                    for keyword in not_found:
                        st.write(f"'{keyword}'")
            else:
                st.info("No keywords were found on the page.")
        
        st.subheader("Additional Information:")
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
            st.write(f"Status Code: {response.status_code}")
            st.write(f"Content Type: {response.headers.get('Content-Type', 'Not specified')}")
            st.write(f"Page Size: {len(response.text)} characters")
        except Exception as e:
            st.error(f"Failed to get additional information: {e}")
    else:
        st.warning("Please enter both URL and keywords.")
