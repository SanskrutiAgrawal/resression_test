import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin
from selenium.common.exceptions import TimeoutException, NoSuchElementException 
from translate_api import translate_text 
from helper_functions import download_image
import os
from collections import Counter
import re

BASE_URL = "https://elpais.com"


LOCATORS = {
    "BODY": (By.TAG_NAME, "body"),
    "COOKIE_BTN": (By.ID, "didomi-notice-agree-button"),

    "OPINION_LINK_DESKTOP": (By.XPATH, "//header//a[contains(@href, '/opinion/')]"),

    "MOBILE_MENU_BTN": (By.ID, "btn_open_hamburger"),

    "OPINION_LINK_IN_MENU": (By.CSS_SELECTOR, "#hamburger_container > nav > div:nth-child(1) > ul > li:nth-child(2) > a"),
    
    "ARTICLE_LINKS": (By.CSS_SELECTOR, "article h2 a"),
    "ARTICLE_TITLE": (By.TAG_NAME, "h1"),
    "ARTICLE_PARAS": (By.CSS_SELECTOR, "article p"),
    "COVER_IMAGE": (By.CSS_SELECTOR, "img._re.a_m-h"),
}

def analyze_repeated_words(titles: list):
    """Analyzes repeated words across all translated titles."""
    print("\nAnalyzing repeated words in translated titles...")
    
    all_text = " ".join(titles).lower()
 
    words = [w for w in re.split(r'\W+', all_text) if len(w) > 3]
    
    counts = Counter(words)

    repeated = [(w, c) for w, c in counts.items() if c > 2]

    if repeated:
        print("\nWords appearing more than twice:")
        for w, c in repeated:
            print(f"{w}: {c}")
    else:
        print("No words appear more than twice.")

def handle_intrusive_element(driver, locator, timeout=5, log_message=""):
    """
    Checks for and clicks a potential intrusive element (like a cookie banner) 
    if it appears. Uses standard Selenium click.
    """
    try:
        short_wait = WebDriverWait(driver, timeout)
        element_btn = short_wait.until(EC.element_to_be_clickable(locator))

        element_btn.click() 
        print(f"{log_message or 'Intrusive element'} handled.")
        short_wait.until(EC.invisibility_of_element_located(locator))
        
    except Exception:
        pass

class TestElPaisOpinionScraper:

    def test_scrape_and_analyze_articles(self, driver, legacy_caps=None):
        web_driver, driver_name,legacy_caps = driver 
        print(legacy_caps)
        is_mobile = legacy_caps.get("bstack:options", {}).get("deviceName") is not None
        print(is_mobile)
        
        wait = WebDriverWait(web_driver, 15) 

        web_driver.get(BASE_URL)
        wait.until(EC.presence_of_element_located(LOCATORS["BODY"]))

        handle_intrusive_element(
            web_driver, 
            LOCATORS["COOKIE_BTN"], 
            timeout=5, 
            log_message="Cookie consent accepted"
        )

        try:
            if is_mobile:
                time.sleep(3)
                print("Mode: MOBILE. Executing Hamburger Menu navigation.")

                menu_btn = wait.until(EC.element_to_be_clickable(LOCATORS["MOBILE_MENU_BTN"]), 
                                      message="Mobile menu button not clickable.")
                menu_btn.click()
                print("Clicked Mobile Hamburger Menu.")

                opinion_link = wait.until(EC.element_to_be_clickable(LOCATORS["OPINION_LINK_IN_MENU"]), 
                                         message="Opinion link in menu not clickable.")
                opinion_link.click()
                print("Navigated to Opinion section via Mobile Menu.")
                
            else:
                print("Mode: DESKTOP/LOCAL. Executing direct link navigation.")

                opinion_link = wait.until(EC.element_to_be_clickable(LOCATORS["OPINION_LINK_DESKTOP"]), 
                                         message="Desktop Opinion link not clickable.")
                opinion_link.click() 
                print("Navigated to Opinion section via direct link.")
            
            time.sleep(1) 

            handle_intrusive_element(
                web_driver, 
                LOCATORS["COOKIE_BTN"], 
                timeout=3, 
                log_message="Reappearing Cookie pop-up handled after Opinion navigation"
            )

            wait.until(EC.presence_of_all_elements_located(LOCATORS["ARTICLE_LINKS"]))
            print("Opinion articles content is visible and ready for scraping.")
            
        except Exception as err:
            pytest.fail(f"Error navigating to Opinion section or finding content: {err}")

        article_elements = web_driver.find_elements(*LOCATORS["ARTICLE_LINKS"])
        unique_links = []
        
        for link in article_elements:
            href = link.get_attribute("href")
            if href and href not in unique_links:
                unique_links.append(href)
            if len(unique_links) >= 5:
                break
        
        print(f"Found {len(unique_links)} article links\n")
        assert len(unique_links) == 5, f"Expected to find 5 unique articles, but found {len(unique_links)}"
        
        articles = []
        original_window = web_driver.current_window_handle

        for i, relative_url in enumerate(unique_links):
            url = urljoin(BASE_URL, relative_url)
            print(f"\nProcessing Article {i + 1}: {url}")

            web_driver.execute_script("window.open(arguments[0]);", url)
            web_driver.switch_to.window(web_driver.window_handles[-1])

            handle_intrusive_element(
                web_driver, 
                LOCATORS["COOKIE_BTN"], 
                timeout=5, 
                log_message=f"Reappearing Cookie pop-up handled for Article {i+1}"
            )
            
            wait.until(EC.presence_of_element_located(LOCATORS["ARTICLE_TITLE"]))

            title = "N/A"
            content = ""
            img_path = "N/A"

            img_dir_name = "images_parallel/el_pais_opinion" if driver_name == "bs_remote" else "images/el_pais_opinion"

            try:
                title = web_driver.find_element(*LOCATORS["ARTICLE_TITLE"]).text
                print(f"Title (ES): {title}")
            except:
                print("No title found")

            try:
                paras = web_driver.find_elements(*LOCATORS["ARTICLE_PARAS"])
                if not paras:
                    WebDriverWait(web_driver, 8).until(EC.presence_of_all_elements_located(LOCATORS["ARTICLE_PARAS"]))
                    paras = web_driver.find_elements(*LOCATORS["ARTICLE_PARAS"])
                    
                para_texts = [p.text for p in paras[:5]]
                content = " ".join(para_texts)
                print(f"Content preview: {content[:150]}...")
            except:
                print("No article content found")

            try:
                img = wait.until(EC.presence_of_element_located(LOCATORS["COVER_IMAGE"]))
                img_src = img.get_attribute("src")
                
                img_path = download_image(img_src, img_dir_name, i, driver_name)
                
            except Exception as err:
                print(f"Error finding/downloading image: {err}")

            articles.append({
                "title": title,
                "content": content,
                "imgPath": img_path,
                "url": url,
            })

            web_driver.close()
            web_driver.switch_to.window(original_window)

        titles_to_translate = [a["title"] for a in articles]
        translated_titles = translate_text(titles_to_translate)

        for i, a in enumerate(articles):
            a["translatedTitle"] = translated_titles[i]

        print("\nArticle Summary:")
        for i, a in enumerate(articles):
            print(f"\n#{i + 1}")
            print(f"Original: {a['title']}")
            print(f"Translated: {a['translatedTitle']}")
            print(f"Image: {a['imgPath'] or 'N/A'}")

        analyze_repeated_words([a["translatedTitle"] for a in articles])