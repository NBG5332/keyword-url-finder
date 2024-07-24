import streamlit as st
import re
from playwright.sync_api import sync_playwright
import os

def setup_playwright():
    # This will be triggered to install browser binaries on first run
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # Install only if not already installed
        if not os.path.exists("/mnt/data/playwright"):
            p.chromium.install()

def find_keywords_playwright(url, keywords):
    try:
        # Launch the browser
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)

            # Get the page source
            html_content = page.content().lower()

            # Find matches for each keyword
            matches = {}
            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', html_content))
                if count > 0:
                    matches[keyword] = count

            browser.close()
            return matches
    except Exception as e:
        st.error(f"An error occurred while fetching the webpage: {e}")
        return None

def main():
    st.title("Keyword Finder in Web Pages")
    st.write("Enter a URL and a list of keywords to find out how often each keyword appears on the webpage.")

    # Button to setup Playwright browser binaries
    if st.sidebar.button("Setup Playwright"):
        setup_playwright()
        st.sidebar.success("Playwright setup completed!")

    url = st.text_input("Enter the URL to inspect:", "")
    keywords_input = st.text_input("Enter keywords to search for (comma-separated):", "")

    if st.button("Search Keywords"):
        if url and keywords_input:
            keywords = [k.strip() for k in keywords_input.split(',')]
            results = find_keywords_playwright(url, keywords)

            if results is not None:
                if results:
                    st.success("Keywords found:")
                    for keyword, count in results.items():
                        st.write(f"'{keyword}': {count} occurrences")

                    not_found = set(keywords) - set(results.keys())
                    if not_found:
                        st.info("Keywords not found:")
                        for keyword in not_found:
                            st.write(f"'{keyword}'")
                else:
                    st.warning("No keywords
