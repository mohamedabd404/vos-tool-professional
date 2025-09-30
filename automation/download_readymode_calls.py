import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

# Get username from environment or use default
import os
USERNAME = os.getenv("READYMODE_USER", "Auditor1")
PASSWORD = os.getenv("READYMODE_PASSWORD", "Auditor1@3510")

def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # DISABLED - Browser will be visible for debugging
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")  # Keep GPU enabled for visible mode
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Hide automation detection
    # chrome_options.add_argument("--log-level=3")  # Show console logs for debugging
    service = Service(executable_path=os.path.join(os.getcwd(), "chromedriver.exe"))
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def login_to_readymode(driver, wait, dialer_url):
    driver.get(dialer_url)
    wait.until(EC.presence_of_element_located((By.NAME, "login_account")))

    username_input = driver.find_element(By.NAME, "login_account")
    password_input = driver.find_element(By.NAME, "login_password")
    admin_checkbox = driver.find_element(By.ID, "login_as_admin")
    sign_in_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")

    username_input.clear()
    username_input.send_keys(USERNAME)
    password_input.clear()
    password_input.send_keys(PASSWORD)

    if not admin_checkbox.is_selected():
        driver.execute_script("arguments[0].click();", admin_checkbox)

    driver.execute_script("arguments[0].click();", sign_in_btn)

    try:
        continue_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input.button.primary.primary-l.sign-in[value='Continue']")))
        continue_btn.click()
    except:
        pass

    wait.until(lambda d: "login" not in d.current_url)

# Example function to save a downloaded file for a user

def save_downloaded_file(username, filename, file_bytes, record_type='Agent'):
    today = datetime.now().strftime('%Y-%m-%d')
    base_folder = f"Recordings/{record_type}/{username}/{today}"
    os.makedirs(base_folder, exist_ok=True)
    file_path = os.path.join(base_folder, filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path

def download_all_call_recordings(dialer_url, agent, update_callback=None,
                                  start_date=None, end_date=None,
                                  max_samples=50, campaign_name=None,
                                  disposition=None,
                                  min_duration=None, max_duration=None,
                                  username=None, keep_browser_open=False):
    subfolder = "Campaign" if campaign_name and start_date and end_date else "Agent"
    # Determine save path for Campaign or Agent
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Use provided username or fall back to default
    download_username = username if username else USERNAME
    
    if subfolder == "Campaign" and campaign_name:
        campaign_folder = f"{campaign_name}-{today}"
        DOWNLOAD_DIR = os.path.join(os.getcwd(), "Recordings", subfolder, download_username, campaign_folder)
    elif subfolder == "Agent" and agent:
        agent_folder = f"{agent}-{today}"
        DOWNLOAD_DIR = os.path.join(os.getcwd(), "Recordings", subfolder, download_username, agent_folder)
    else:
        DOWNLOAD_DIR = os.path.join(os.getcwd(), "Recordings", subfolder, download_username, today)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    driver = get_driver()
    wait = WebDriverWait(driver, 60)

    try:
        login_to_readymode(driver, wait, dialer_url)

        call_logs_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, '+CCS Reports/call_log')]")))
        driver.execute_script("arguments[0].click();", call_logs_link)
        print("✅ Clicked Call Logs")

        # Set Date Filters
        if start_date and end_date:
            start_str = start_date.strftime("%m/%d/%Y")
            end_str = end_date.strftime("%m/%d/%Y")

            start_input = wait.until(EC.presence_of_element_located((By.NAME, "report[time_from_d]")))
            start_input.clear()
            start_input.send_keys(start_str)
            start_input.send_keys(Keys.RETURN)

            end_input = wait.until(EC.presence_of_element_located((By.NAME, "report[time_to_d]")))
            end_input.clear()
            end_input.send_keys(end_str)
            end_input.send_keys(Keys.RETURN)

            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='.mp3']")))

        # Campaign Filter
        if campaign_name:
            try:
                camp_dropdown = wait.until(EC.presence_of_element_located((By.ID, "restrict_campaign")))
                Select(camp_dropdown).select_by_visible_text(campaign_name)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='.mp3']")))
                print(f"✅ Campaign: {campaign_name}")
            except:
                print(f"[!] Campaign '{campaign_name}' not found")

        # Agent Filter - Enhanced with multiple selection strategies
        if agent and agent.strip().lower() != "any":
            try:
                print(f"🔍 Attempting to select agent: '{agent}'")
                dropdown = wait.until(EC.presence_of_element_located((By.ID, "restrict_uid")))
                select = Select(dropdown)
                
                # Get all available options for debugging
                available_options = [opt.text.strip() for opt in select.options]
                print(f"📋 Available agents in dropdown: {available_options[:5]}...")  # Show first 5
                
                # Strategy 1: Try exact match (original method)
                try:
                    select.select_by_visible_text(agent.strip())
                    print(f"✅ Agent selected (exact match): {agent}")
                except:
                    print(f"⚠️ Exact match failed, trying partial match...")
                    
                    # Strategy 2: Try partial match (case-insensitive)
                    agent_lower = agent.strip().lower()
                    matched = False
                    for option in select.options:
                        if agent_lower in option.text.strip().lower():
                            select.select_by_visible_text(option.text.strip())
                            print(f"✅ Agent selected (partial match): {option.text.strip()}")
                            matched = True
                            break
                    
                    if not matched:
                        # Strategy 3: Try by value instead of text
                        try:
                            select.select_by_value(agent.strip())
                            print(f"✅ Agent selected (by value): {agent}")
                        except:
                            print(f"❌ Could not select agent '{agent}' - will download all agents")
                            print(f"💡 Available options: {', '.join(available_options[:10])}")
                
                # Wait for page to update after selection
                time.sleep(2)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='.mp3']")))
                
            except Exception as e:
                print(f"[!] Error selecting agent '{agent}': {str(e)}")
                print(f"⚠️ Continuing with all agents...")

        # Disposition Filter (HYBRID: UI interaction)
        if disposition:
            try:
                print(f"✅ Disposition: {disposition}")
                # 1. Open the dropdown
                dropdown_btn = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ui-multiselect"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_btn)
                driver.execute_script("arguments[0].click();", dropdown_btn)
                time.sleep(0.5)

                # 2. Click 'Uncheck all'
                uncheck_all = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.ui-multiselect-none"))
                )
                driver.execute_script("arguments[0].click();", uncheck_all)
                time.sleep(0.5)

                # 3. Check only the desired dispositions
                for dispo in disposition:
                    xpath = f"//ul[contains(@class, 'ui-multiselect-checkboxes')]//label[span[text()='{dispo}']]//input"
                    checkbox = driver.find_element(By.XPATH, xpath)
                    if not checkbox.is_selected():
                        driver.execute_script("arguments[0].click();", checkbox)
                    time.sleep(0.1)

                # 4. Click outside to close the menu (optional)
                from selenium.webdriver.common.action_chains import ActionChains
                ActionChains(driver).move_by_offset(10, 10).click().perform()
                time.sleep(0.2)
            except Exception as e:
                print(f"[!] Failed to apply disposition filter: {e}")

        # Duration Filter (NEW)
        if min_duration is not None or max_duration is not None:
            try:
                print(f"🔧 Setting duration filter: {min_duration}-{max_duration}")
                duration_dropdown = wait.until(EC.presence_of_element_located((By.ID, "duration_filter")))

                # Map min/max to dropdown value with better logic
                if min_duration is not None and max_duration is not None:
                    if min_duration == 30 and max_duration == 60:
                        Select(duration_dropdown).select_by_value("30-60")
                        print("✅ Set duration filter: 30-60 seconds")
                    elif min_duration == 60 and max_duration == 600:
                        Select(duration_dropdown).select_by_value("60-600")
                        print("✅ Set duration filter: 60-600 seconds")
                    else:
                        # For custom ranges, try to find closest match or use "custom"
                        print(f"⚠️ Custom duration range {min_duration}-{max_duration}, trying to set in UI")
                        # Try 30-60 first as default
                        try:
                            Select(duration_dropdown).select_by_value("30-60")
                            print("✅ Used 30-60 as closest match for custom range")
                        except:
                            print("⚠️ Could not set duration filter in UI, will filter after download")
                elif max_duration is not None:
                    if max_duration == 30:
                        Select(duration_dropdown).select_by_value("0-30")
                        print("✅ Set duration filter: 0-30 seconds")
                    else:
                        Select(duration_dropdown).select_by_value("less")
                        print(f"✅ Set duration filter: Less than {max_duration} seconds")
                elif min_duration is not None:
                    Select(duration_dropdown).select_by_value("greater")
                    print(f"✅ Set duration filter: Greater than {min_duration} seconds")

                # Wait for filter to apply
                time.sleep(2)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='.mp3']")))
                print("✅ Duration filter applied successfully")
            except Exception as e:
                print(f"[!] Failed to set duration filter in UI: {e}")
                print("⚠️ Will rely on post-download duration filtering")

        # Begin downloading
        session = requests.Session()
        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        headers = {"User-Agent": "Mozilla/5.0"}

        if agent and agent.strip().lower() == "all users":
            downloaded = 0
            attempted = 0
            page_number = 1
            seen_links = set()
            max_attempts = max_samples * 3  # Allow up to 3x attempts to account for filtered files
            start_time = datetime.now()
            max_duration_minutes = 30  # Maximum 30 minutes for download

            while downloaded < max_samples and attempted < max_attempts:
                # Check timeout
                if datetime.now() - start_time > timedelta(minutes=max_duration_minutes):
                    print(f"⏰ Timeout reached after {max_duration_minutes} minutes")
                    break

                print(f"\n📄 Page {page_number} (Downloaded: {downloaded}/{max_samples}, Attempted: {attempted})")
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='.mp3']")))

                blocks = driver.find_elements(By.XPATH, "//div[.//a[contains(@href, '.mp3')]]")
                calls = []
                for block in blocks:
                    try:
                        file_text = block.find_element(By.CSS_SELECTOR, "span[repvar='File']").text
                        agent_text = block.find_element(By.CSS_SELECTOR, "span[repvar='User']").text.strip().replace(" ", "")
                        href = block.find_element(By.CSS_SELECTOR, "a[href*='.mp3']").get_attribute("href")
                        if not href.startswith("http"):
                            href = dialer_url.rstrip("/") + "/" + href.lstrip("/")
                        calls.append((agent_text, file_text, href))
                    except:
                        continue

                print(f"🔍 Found {len(calls)} calls on page")

                for agent_name, file_text, href in calls:
                    if downloaded >= max_samples or attempted >= max_attempts:
                        break
                    if href in seen_links:
                        continue
                    seen_links.add(href)
                    attempted += 1

                    phone_match = re.search(r"\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}", file_text)
                    phone_number = phone_match.group(0) if phone_match else f"unknown_{attempted}"
                    filename = f"{agent_name}_({phone_number}).mp3"
                    filepath = os.path.join(DOWNLOAD_DIR, filename)

                    print(f"⬇️ Attempting download {attempted}: {filename}")
                    try:
                        response = session.get(href, cookies=cookies, headers=headers)
                        print(f"📥 Status: {response.status_code}")
                        if response.status_code == 200:
                            # Save file directly to the correct DOWNLOAD_DIR
                            file_path = os.path.join(DOWNLOAD_DIR, filename)
                            with open(file_path, "wb") as f:
                                f.write(response.content)

                            # Duration filter after download
                            if min_duration is not None or max_duration is not None:
                                try:
                                    from pydub import AudioSegment
                                    audio = AudioSegment.from_file(file_path)
                                    dur = audio.duration_seconds
                                    print(f"📏 File duration: {dur:.1f} seconds")

                                    if (min_duration is not None and dur < min_duration) or (max_duration is not None and dur > max_duration):
                                        os.remove(file_path)
                                        print(f"⏩ Skipped {filename} (duration {dur:.1f}s not in range {min_duration}-{max_duration})")
                                        continue
                                    else:
                                        print(f"✅ Duration OK: {dur:.1f}s matches filter {min_duration}-{max_duration}")
                                except Exception as e:
                                    print(f"[!] Error checking duration for {filename}: {e}")
                                    os.remove(file_path)
                                    continue

                            downloaded += 1
                            print(f"✅ Successfully saved ({downloaded}/{max_samples})")
                            if update_callback:
                                update_callback(downloaded, max_samples)
                        else:
                            print(f"❌ Failed to download {filename}: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"[!] Error downloading {filename}: {e}")

                if downloaded >= max_samples:
                    print(f"✅ Reached target of {max_samples} files")
                    break

                try:
                    pagination = driver.find_element(By.ID, "ccs_cl_pagination")
                    current = pagination.find_element(By.CSS_SELECTOR, "li.page.selected")
                    next_page = current.find_element(By.XPATH, "following-sibling::li[@class='page']")
                    driver.execute_script("arguments[0].click();", next_page)
                    print(f"➡️ Next page ({page_number + 1})")
                    page_number += 1
                    time.sleep(2)
                except:
                    print("❌ No more pages or pagination not found.")
                    break

        else:
            # Single agent download logic
            downloaded = 0
            attempted = 0
            max_attempts = max_samples * 2  # Allow up to 2x attempts for single agent
            start_time = datetime.now()
            max_duration_minutes = 15  # Maximum 15 minutes for single agent

            while downloaded < max_samples and attempted < max_attempts:
                # Check timeout
                if datetime.now() - start_time > timedelta(minutes=max_duration_minutes):
                    print(f"⏰ Timeout reached after {max_duration_minutes} minutes")
                    break

                print(f"\n🔍 Looking for calls... (Downloaded: {downloaded}/{max_samples})")
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='.mp3']")))

                blocks = driver.find_elements(By.XPATH, "//div[.//a[contains(@href, '.mp3')]]")
                calls = []
                for block in blocks:
                    try:
                        file_text = block.find_element(By.CSS_SELECTOR, "span[repvar='File']").text
                        agent_text = block.find_element(By.CSS_SELECTOR, "span[repvar='User']").text.strip().replace(" ", "")
                        href = block.find_element(By.CSS_SELECTOR, "a[href*='.mp3']").get_attribute("href")
                        if not href.startswith("http"):
                            href = dialer_url.rstrip("/") + "/" + href.lstrip("/")
                        calls.append((agent_text, file_text, href))
                    except:
                        continue

                print(f"🔍 Found {len(calls)} calls")

                for agent_name, file_text, href in calls:
                    if downloaded >= max_samples or attempted >= max_attempts:
                        break

                    attempted += 1
                    print(f"⬇️ Attempting download {attempted}: {agent_name}")

                    phone_match = re.search(r"\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}", file_text)
                    phone_number = phone_match.group(0) if phone_match else f"unknown_{attempted}"
                    filename = f"{agent_name}_({phone_number}).mp3"
                    filepath = os.path.join(DOWNLOAD_DIR, filename)

                    try:
                        response = session.get(href, cookies=cookies, headers=headers)
                        print(f"📥 Status: {response.status_code}")
                        if response.status_code == 200:
                            file_path = os.path.join(DOWNLOAD_DIR, filename)
                            with open(file_path, "wb") as f:
                                f.write(response.content)

                            # Duration filter after download
                            if min_duration is not None or max_duration is not None:
                                try:
                                    from pydub import AudioSegment
                                    audio = AudioSegment.from_file(file_path)
                                    dur = audio.duration_seconds
                                    print(f"📏 File duration: {dur:.1f} seconds")

                                    if (min_duration is not None and dur < min_duration) or (max_duration is not None and dur > max_duration):
                                        os.remove(file_path)
                                        print(f"⏩ Skipped {filename} (duration {dur:.1f}s not in range)")
                                        continue
                                except Exception as e:
                                    print(f"[!] Error checking duration for {filename}: {e}")
                                    os.remove(file_path)
                                    continue

                            downloaded += 1
                            print(f"✅ Saved ({downloaded}/{max_samples})")
                            if update_callback:
                                update_callback(downloaded, max_samples)
                        else:
                            print(f"❌ Failed to download: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"[!] Error downloading: {e}")

                if downloaded >= max_samples:
                    break

                # Try to load more results - multiple strategies for single agent
                more_results = False
                try:
                    # Strategy 1: Look for specific pagination
                    pagination = driver.find_element(By.ID, "ccs_cl_pagination")
                    current = pagination.find_element(By.CSS_SELECTOR, "li.page.selected")
                    next_page = current.find_element(By.XPATH, "following-sibling::li[@class='page']")
                    if next_page:
                        driver.execute_script("arguments[0].click();", next_page)
                        print(f"➡️ Next page")
                        more_results = True
                        time.sleep(2)
                except:
                    try:
                        # Strategy 2: Look for "Load More" or "Show More" buttons
                        buttons = driver.find_elements(By.CSS_SELECTOR, "button, a, span")
                        for btn in buttons:
                            if ("load more" in btn.text.lower() or
                                "show more" in btn.text.lower() or
                                "next" in btn.text.lower()):
                                driver.execute_script("arguments[0].click();", btn)
                                print("🔄 Loading more results...")
                                more_results = True
                                time.sleep(3)
                                break
                    except:
                        pass

                if not more_results:
                    print("❌ No more results found for single agent.")
                    break

            print(f"📊 Single agent download complete: {downloaded}/{max_samples} files downloaded, {attempted} total attempts")

    finally:
        driver.quit()
        print("✅ Done. Browser closed.")















