from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import re
import unicodedata
from collections import Counter

# List of article URLs to scrape
article_urls = [
    "https://www.rtvslo.si/sport/kolesarstvo/dirka-po-franciji/pogacar-z-epsko-predstavo-spisal-zgodovino-toura/536525"
    "https://www.rtvslo.si/sport/kolesarstvo/dirka-po-franciji/pogacar-po-tem-touru-je-primoz-se-vecji-zgled-zame/536656"
    # you can add more
]

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)

def extract_date_time(full_timestamp):
    """Extracts date (DD.MM.YYYY) and time (HH:MM) from the full timestamp."""
    match = re.search(r"(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4}),\s*(\d{1,2}):(\d{2})", full_timestamp)
    if match:
        day, month, year, hour, minute = match.groups()
        formatted_date = f"{day.zfill(2)}.{month.zfill(2)}.{year}"
        formatted_time = f"{hour.zfill(2)}:{minute}"
        return formatted_date, formatted_time
    return "Unknown", "Unknown"

def sanitize_filename(text):
    """Convert special characters to ASCII, replace spaces with hyphens, and limit to 10 characters."""
    text = text.lower()
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')  # Remove special chars
    text = re.sub(r'[^a-z0-9\s-]', '', text)  # Remove unwanted characters
    text = "-".join(text.split()[:4])  # Take first 4 words, join with dashes
    return text[:10]  # Limit filename length

def scrape_comments():
    """Extracts all comments from the currently loaded page."""
    data = []
    
    # Extract all comment containers
    all_comment_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'comment-container')]")

    for container in all_comment_containers:
        try:
            # If it's a "has-source" comment, find the reply block
            if "has-source" in container.get_attribute("class"):
                comment_block = container.find_element(By.XPATH, ".//div[@class='comment' and not(contains(@class, 'comment-source'))]")
            else:
                comment_block = container.find_element(By.XPATH, ".//div[@class='comment']")

            # Extract username
            username_element = comment_block.find_element(By.XPATH, ".//a[@class='profile-name']")
            username = username_element.text.strip() if username_element else "Unknown"

            # Extract timestamp (date & time)
            timestamp_elements = comment_block.find_elements(By.XPATH, ".//span[@class='publish-meta']")
            full_timestamp = timestamp_elements[-1].text.strip() if timestamp_elements else "Unknown"
            comment_date, comment_time = extract_date_time(full_timestamp)  # Extract date and time separately

            # Extract comment text
            comment_elements = comment_block.find_elements(By.XPATH, ".//p")
            comment_text = " ".join([el.text.strip() for el in comment_elements if el.text.strip()]) if comment_elements else "No comment text"

            # Store extracted data
            data.append({"User": username, "Date": comment_date, "Time": comment_time, "Comment": comment_text})

        except NoSuchElementException:
            print("Skipping a comment due to missing elements.")

    return data

for base_url in article_urls:
    try:
        driver.get(base_url)
        all_data = []

        # Extract the article title
        try:
            title_element = driver.find_element(By.XPATH, "//*[@id='main-container']/div[3]/div/header/h1")
            article_title = title_element.text.strip()
            sanitized_title = sanitize_filename(article_title)
        except NoSuchElementException:
            sanitized_title = "unknown-title"

        # Click "Prikaži komentarje" if available
        try:
            show_comments_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "link-show-comments"))
            )
            driver.execute_script("arguments[0].click();", show_comments_button)
            print(f"Clicked 'Prikaži komentarje' button for {article_title}.")
            time.sleep(3)  # Allow time for comments to load
        except TimeoutException:
            print(f"No 'Prikaži komentarje' button found for {article_title}.")
        
        while True:
            try:
                # Wait for comments to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'comment-container')]")
                ))
                print("Comments section is now visible.")
            except TimeoutException:
                print("Timeout while waiting for comments to load.")
                break
            
            # Scrape comments from the current page
            page_data = scrape_comments()
            all_data.extend(page_data)
            print("Scraped current page comments")

            # Check for "Next page" button and click it
            try:
                next_button = driver.find_element(By.XPATH, "//li[@class='page-item']/span[@class='page-link' and contains(text(), '»')]")
                driver.execute_script("arguments[0].click();", next_button)
                print("Clicked 'Next page' button.")
                time.sleep(5)  # Give time for the next batch of comments to load
            except NoSuchElementException:
                print("No more 'Next page' buttons found.")
                break

        # Convert to Pandas DataFrame
        df = pd.DataFrame(all_data)

        # Find the most frequent date in the comments
        if not df.empty:
            date_counts = Counter(df["Date"])
            most_frequent_date = date_counts.most_common(1)[0][0]  # Get most frequent date
            if most_frequent_date != "Unknown":
                day, month, _ = most_frequent_date.split(".")  # Extract DD.MM.YYYY
                filename_date = f"{day}-{month}"
            else:
                filename_date = "unknown-date"
        else:
            filename_date = "unknown-date"

        # Create the filename
        filename = f"{filename_date}-{sanitized_title}.csv"

        print(df.head())

        # Save to CSV
        df.to_csv(filename, index=False, encoding="utf-8")
        print(f"Saved {len(df)} comments to {filename}")

    except Exception as e:
        print(f"Error processing {base_url}: {e}")

# Close the browser after all URLs are processed
driver.quit()
