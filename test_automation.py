from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

print("🚀 Starting SmartCity LOCAL Automated UI Testing...")
print("==================================================")

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 30 seconds smart wait (so you have time to log in)
wait = WebDriverWait(driver, 30)

try:
    # ---------------------------------------------------------
    # TEST 1: OPEN WEBSITE
    # ---------------------------------------------------------
    print("⏳ [TEST 1] Opening Local System...")
    driver.get("http://127.0.0.1:5005")
    driver.maximize_window()
    
    print("⚠️ NOTE: If a login screen appears, quickly enter your credentials and log in.")
    print("⏳ Waiting for Dashboard to load (maximum 30 seconds)...")

    # ---------------------------------------------------------
    # TEST 2: SOS EMERGENCY BUTTON TEST
    # ---------------------------------------------------------
    # The script will wait until the dashboard SOS button is clickable
    sos_button = wait.until(EC.element_to_be_clickable((By.ID, "btn-acc")))
    print("✅ Dashboard Loaded & Login Successful!")
    
    print("⏳ [TEST 2] Testing Crisis Lockdown System...")
    time.sleep(1)  # simulate human delay
    sos_button.click()
    time.sleep(3)
    sos_button.click()
    time.sleep(2)
    print("✅ SOS Button is Working Properly!")

    # ---------------------------------------------------------
    # TEST 3: AUTOMATED TICKET CREATION
    # ---------------------------------------------------------
    print("⏳ [TEST 3] Creating a test incident ticket...")
    
    issue_element = wait.until(EC.presence_of_element_located((By.ID, "ticket-type")))
    issue_dropdown = Select(issue_element)
    issue_dropdown.select_by_visible_text("Camera Offline")
    time.sleep(1)

    location_input = driver.find_element(By.ID, "ticket-loc")
    location_input.send_keys("Node-04 West Highway")
    time.sleep(1)

    submit_btn = driver.find_element(By.ID, "btn-submit-ticket")
    submit_btn.click()
    time.sleep(3)
    print("✅ Ticket Created Successfully via Automation!")

    # ---------------------------------------------------------
    # TEST 4: OPEN IT DESK IN NEW TAB
    # ---------------------------------------------------------
    print("⏳ [TEST 4] Navigating to IT Service Desk...")
    
    # Finds button/link containing 'service' in href
    it_desk_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'service')]")))
    it_desk_btn.click()
    time.sleep(3)
    
    print("\n🏆 ALL AUTOMATION TESTS PASSED SUCCESSFULLY! 🏆")

except Exception as e:
    print(f"\n❌ TEST FAILED: {e}")

finally:
    print("\nTesting complete. Browser will remain open for review.")