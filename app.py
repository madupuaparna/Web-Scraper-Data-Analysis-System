
import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

st.set_page_config(
    page_title="Web Scraper and Data Analysis",
    page_icon="🌐",
    layout="wide"
)

st.title("🌐 Web Scraper and Data Analysis System")
st.write("Extract, analyze and download information from public websites.")

def scrape_website(url, max_pages):
    results = []
    current_url = url
    visited = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; EducationalWebScraper/1.0)"
    }

    for page in range(max_pages):
        if not current_url or current_url in visited:
            break

        visited.add(current_url)

        response = requests.get(
            current_url,
            headers=headers,
            timeout=20
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract structured quote data when available
        quotes = soup.find_all("div", class_="quote")

        if quotes:
            for item in quotes:
                quote = item.find("span", class_="text")
                author = item.find("small", class_="author")

                tags = [
                    tag.get_text(strip=True)
                    for tag in item.find_all("a", class_="tag")
                ]

                results.append({
                    "Title": quote.get_text(strip=True) if quote else "",
                    "Description": author.get_text(strip=True) if author else "",
                    "Link": "",
                    "Tags": ", ".join(tags)
                })

            next_button = soup.find("li", class_="next")
            if next_button and next_button.find("a"):
                current_url = urljoin(
                    current_url,
                    next_button.find("a")["href"]
                )
            else:
                current_url = None

        else:
            # General webpage information
            page_title = soup.title.get_text(strip=True) if soup.title else ""

            for heading in soup.find_all(["h1", "h2", "h3"]):
                results.append({
                    "Title": heading.get_text(" ", strip=True),
                    "Description": page_title,
                    "Link": current_url,
                    "Tags": "Heading"
                })

            for paragraph in soup.find_all("p"):
                description = paragraph.get_text(" ", strip=True)

                if description:
                    results.append({
                        "Title": page_title,
                        "Description": description,
                        "Link": current_url,
                        "Tags": "Paragraph"
                    })

            current_url = None

    return pd.DataFrame(results)


url = st.text_input(
    "Enter a public website URL",
    value="https://quotes.toscrape.com/"
)

max_pages = st.slider(
    "Number of pages to scrape",
    min_value=1,
    max_value=10,
    value=3
)

if st.button("Start Scraping"):
    parsed = urlparse(url)

    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
        st.error("Please enter a valid HTTP or HTTPS URL.")

    else:
        try:
            with st.spinner("Extracting website information..."):
                df = scrape_website(url, max_pages)

            if df.empty:
                st.warning("No suitable information was found.")
            else:
                st.session_state["scraped_data"] = df
                st.success("Website scraping completed successfully!")

        except requests.RequestException as error:
            st.error(f"Website connection failed: {error}")
        except Exception as error:
            st.error(f"An error occurred: {error}")


if "scraped_data" in st.session_state:
    df = st.session_state["scraped_data"]

    st.subheader("📊 Scraped Website Data")

    col1, col2 = st.columns(2)

    col1.metric("Total Records", len(df))
    col2.metric("Total Columns", len(df.columns))

    st.dataframe(df, use_container_width=True)

    st.subheader("📈 Data Analysis")

    if "Tags" in df.columns:
        tag_counts = df["Tags"].value_counts()
        st.bar_chart(tag_counts)

    if "Description" in df.columns:
        st.write("Most frequently appearing descriptions/authors:")
        st.bar_chart(df["Description"].value_counts().head(10))

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Scraped Data as CSV",
        data=csv,
        file_name="scraped_website_data.csv",
        mime="text/csv"
    )

st.divider()
st.caption("Educational project | Python, BeautifulSoup, Requests, Pandas and Streamlit")
