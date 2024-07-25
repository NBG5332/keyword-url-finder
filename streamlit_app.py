import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Function to find keywords in a webpage
def find_keywords(url, keywords):
    try:
        # Send a GET request to the URL with headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fetch the webpage content
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        html_content = soup.get_text().lower()

        # Find matches for each keyword using regular expressions
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

# Main function to run the Streamlit app
def main():
    # Title and description
    st.title("Keyword Finder in Web Pages")
    st.write("Enter a URL and a list of keywords to find out how often each keyword appears on the webpage.")

    # Input fields for URL and keywords
    url = st.text_input("Enter the URL to inspect:", "https://moegreens.treez.io/onlinemenu/category/flower/item/c59a8420-8771-47da-9de9-493aa302a82b?customerType=ALL")
    keywords_input = st.text_input("Enter keywords to search for (comma-separated):", "google-tag-manager")

    # Button to trigger the search
    if st.button("Search Keywords"):
        if url and keywords_input:
            keywords = [k.strip() for k in keywords_input.split(',')]
            results = find_keywords(url, keywords)

            # Display the results
            if results is not None:
                if results:
                    st.success("Keywords found:")
                    for keyword, count in results.items():
                        st.write(f"'{keyword}': {count} occurrences")

                    # Handle keywords not found
                    not_found = set(keywords) - set(results.keys())
                    if not_found:
                        st.info("Keywords not found:")
                        for keyword in not_found:
                            st.write(f"'{keyword}'")
                else:
                    st.warning("No keywords were found on the page.")
            else:
                st.error("Unable to process the page due to an error.")

# Run the main function
if __name__ == "__main__":
    main()
