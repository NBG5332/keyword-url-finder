import streamlit as st
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def find_keywords_selenium(url, keywords):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify the path to your ChromeDriver
    service = Service(executable_path='path/to/chromedriver')  # Update with your path

    try:
        # Initialize the driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)

        # Wait for the page to load (can be improved with WebDriverWait if necessary)
        driver.implicitly_wait(10)

        # Get the page source
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
        st.error(f"An error occurred while fetching the webpage: {e}")
        return None

def main():
    st.title("Keyword Finder in Web Pages")
    st.write("Enter a URL and a list of keywords to find out how often each keyword appears on the webpage.")

    url = st.text_input("Enter the URL to inspect:", "")
    keywords_input = st.text_input("Enter keywords to search for (comma-separated):", "")

    if st.button("Search Keywords"):
        if url and keywords_input:
            keywords = [k.strip() for k in keywords_input.split(',')]
            results = find_keywords_selenium(url, keywords)

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
                    st.warning("No keywords were found on the page.")
            else:
                st.error("Unable to process the page due to an error.")

if __name__ == "__main__":
    main()
