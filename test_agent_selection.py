"""
Test script to debug agent selection issues
This will show you exactly what's happening when trying to select an agent
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import os

# Configuration
USERNAME = os.getenv("READYMODE_USER", "Auditor1")
PASSWORD = os.getenv("READYMODE_PASSWORD", "Auditor1@3510")
DIALER_URL = "https://your-dialer-url.com"  # UPDATE THIS
AGENT_TO_SELECT = "YourAgentName"  # UPDATE THIS

def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Comment out to see browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(executable_path=os.path.join(os.getcwd(), "chromedriver.exe"))
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def login(driver, wait):
    driver.get(DIALER_URL)
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
    print("✅ Logged in successfully")

def test_agent_selection():
    driver = get_driver()
    wait = WebDriverWait(driver, 60)
    
    try:
        # Login
        login(driver, wait)
        
        # Navigate to Call Logs
        call_logs_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href, '+CCS Reports/call_log')]")))
        driver.execute_script("arguments[0].click();", call_logs_link)
        print("✅ Navigated to Call Logs")
        time.sleep(2)
        
        # Find the agent dropdown
        print(f"\n{'='*60}")
        print(f"TESTING AGENT SELECTION: '{AGENT_TO_SELECT}'")
        print(f"{'='*60}\n")
        
        dropdown = wait.until(EC.presence_of_element_located((By.ID, "restrict_uid")))
        select = Select(dropdown)
        
        # Get all options
        print("📋 ALL AVAILABLE AGENTS IN DROPDOWN:")
        print("-" * 60)
        for i, option in enumerate(select.options, 1):
            value = option.get_attribute('value')
            text = option.text.strip()
            print(f"{i:3d}. Text: '{text}'")
            print(f"      Value: '{value}'")
            print()
        
        print(f"\n{'='*60}")
        print("TESTING SELECTION STRATEGIES")
        print(f"{'='*60}\n")
        
        # Test Strategy 1: Exact Match
        print("STRATEGY 1: Exact Match")
        print("-" * 40)
        try:
            select.select_by_visible_text(AGENT_TO_SELECT.strip())
            selected = select.first_selected_option.text
            print(f"✅ SUCCESS - Selected: '{selected}'")
        except Exception as e:
            print(f"❌ FAILED - {type(e).__name__}: {e}")
        
        # Test Strategy 2: Partial Match
        print("\nSTRATEGY 2: Partial Match (case-insensitive)")
        print("-" * 40)
        agent_lower = AGENT_TO_SELECT.strip().lower()
        matches = []
        for option in select.options:
            option_text = option.text.strip()
            if agent_lower in option_text.lower():
                matches.append(option_text)
        
        if matches:
            print(f"✅ Found {len(matches)} partial match(es):")
            for match in matches:
                print(f"   - '{match}'")
            
            # Try to select the first match
            try:
                select.select_by_visible_text(matches[0])
                selected = select.first_selected_option.text
                print(f"✅ Successfully selected: '{selected}'")
            except Exception as e:
                print(f"❌ Failed to select '{matches[0]}': {e}")
        else:
            print(f"❌ No partial matches found for '{agent_lower}'")
        
        # Test Strategy 3: By Value
        print("\nSTRATEGY 3: Select by Value")
        print("-" * 40)
        try:
            select.select_by_value(AGENT_TO_SELECT.strip())
            selected = select.first_selected_option.text
            print(f"✅ SUCCESS - Selected: '{selected}'")
        except Exception as e:
            print(f"❌ FAILED - {type(e).__name__}: {e}")
        
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}\n")
        
        # Provide recommendations
        exact_matches = [opt.text.strip() for opt in select.options if opt.text.strip() == AGENT_TO_SELECT.strip()]
        if exact_matches:
            print(f"✅ Use exact name: '{exact_matches[0]}'")
        elif matches:
            print(f"✅ Use partial match: '{matches[0]}'")
            print(f"   Or update your agent name to: '{matches[0]}'")
        else:
            print(f"❌ Agent '{AGENT_TO_SELECT}' not found in dropdown")
            print(f"💡 Check the list above and use one of the available agent names")
        
        # Keep browser open for inspection
        print("\n⏸️ Browser will stay open for 30 seconds for inspection...")
        time.sleep(30)
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()
        print("\n✅ Test complete. Browser closed.")

if __name__ == "__main__":
    print("🧪 Agent Selection Debug Test")
    print("=" * 60)
    print(f"Dialer URL: {DIALER_URL}")
    print(f"Username: {USERNAME}")
    print(f"Agent to select: {AGENT_TO_SELECT}")
    print("=" * 60)
    
    if DIALER_URL == "https://your-dialer-url.com":
        print("\n⚠️ WARNING: Please update DIALER_URL in the script!")
        print("⚠️ WARNING: Please update AGENT_TO_SELECT in the script!")
    else:
        test_agent_selection()
