import streamlit as st
import requests
import re
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def find_keywords(url, keywords):
    try:
        # Send a GET request to the URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the full HTML content
        html_content = response.text.lower()
        
        # Find matches for each keyword
        matches = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            found = re.findall(r'(\S*' + re.escape(keyword_lower) + r'\S*)', html_content)
            count = len(found)
            if count > 0:
                matches[keyword] = found
        
        return matches
    except requests.RequestException as e:
        st.error(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def main():
    st.title("Keyword Finder in Web Pages")
    st.write("Enter a URL and a list of keywords to find out how often each keyword appears on the webpage.")
    
    url = st.text_input("Enter the URL to inspect:", "")
    keywords_input = st.text_input("Enter keywords to search for (comma-separated):", "")
    
    if st.button("Search Keywords"):
        if url and keywords_input:
            keywords = [k.strip() for k in keywords_input.split(',')]
            results = find_keywords(url, keywords)
            
            if results is not None:
                if results:
                    st.success("Keywords found:")
                    for keyword, matches in results.items():
                        st.write(f"'{keyword}': {len(matches)} occurrences")
                        st.write(f"Matches: {', '.join(matches)}")
                    
                    not_found = set(keywords) - set(results.keys())
                    if not_found:
                        st.info("Keywords not found:")
                        for keyword in not_found:
                            st.write(f"'{keyword}'")
                else:
                    st.warning("No keywords were found on the page.")
            else:
                st.error("Unable to process the page due to an error.")
            
            # Additional debugging information
            st.subheader("Additional Information:")
            try:
                response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10, verify=False)
                st.write(f"Status Code: {response.status_code}")
                st.write(f"Content Type: {response.headers.get('Content-Type', 'Not specified')}")
                st.write(f"Page Size: {len(response.text)} characters")
            except Exception as e:
                st.error(f"Failed to get additional information: {e}")

if __name__ == "__main__":
    main()
