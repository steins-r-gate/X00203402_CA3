"""
Selenium UAT (User Acceptance Testing) Script - CA3
Tests the deployed Calculator web application
Student: X00203402 - Roko Skugor
"""

import os
import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Get test URL from environment variable (set by pipeline)
# Default to localhost for local testing
TEST_URL = os.getenv("TEST_URL", "http://localhost:5000").rstrip("/")


@pytest.fixture(scope="session")
def chrome_options():
    """
    Configure Chrome options for headless execution.

    The extra flags help avoid GPU/virtualization errors and reduce log noise in CI.
    """
    options = Options()

    # Prefer modern headless (Chrome 109+). If your Chrome is older, switch to "--headless".
    options.add_argument("--headless=new")

    # CI stability flags
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # GPU/virtualization noise reduction (common Windows/VM fix)
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--use-angle=swiftshader")
    options.add_argument("--ignore-certificate-errors")

    # Reduce “DevTools listening…” and extra Chrome logs
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_experimental_option("useAutomationExtension", False)

    # Fix for some Chrome/Chromedriver combos in CI
    options.add_argument("--remote-allow-origins=*")

    return options


@pytest.fixture(scope="function")
def driver(chrome_options):
    """
    Create a new Chrome WebDriver instance for each test.
    """
    # Silence chromedriver logs
    service = Service(log_output=os.devnull)

    drv = webdriver.Chrome(service=service, options=chrome_options)
    drv.implicitly_wait(2)  # keep small; rely on explicit waits

    yield drv

    drv.quit()


def take_screenshot(driver, test_name):
    """
    Capture screenshot for debugging failed tests.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot_dir = "screenshots"

    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)

    filename = f"{screenshot_dir}/{test_name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")
    return filename


def wait_for_form(driver, timeout=10):
    """Wait until the calculator form is present."""
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.NAME, "operation"))
    )
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.NAME, "num1"))
    )


class TestCalculatorWebUI:
    def test_home_page_loads(self, driver):
        try:
            driver.get(TEST_URL)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )

            assert "Calculator" in driver.title or "Calculator App" in driver.page_source

            heading = driver.find_element(By.TAG_NAME, "h1")
            assert heading.text == "🧮 Python Calculator"

            print(f"✓ Home page loaded successfully from {TEST_URL}")

        except Exception:
            take_screenshot(driver, "test_home_page_loads_FAILED")
            raise

    def test_health_endpoint(self, driver):
        try:
            driver.get(f"{TEST_URL}/health")

            page_source = driver.page_source

            assert '"status": "healthy"' in page_source or '"status":"healthy"' in page_source
            assert '"service": "calculator-app"' in page_source or '"service":"calculator-app"' in page_source
            assert "X00203402" in page_source

            print("✓ Health endpoint responding correctly")

        except Exception:
            take_screenshot(driver, "test_health_endpoint_FAILED")
            raise

    def test_form_elements_present(self, driver):
        try:
            driver.get(TEST_URL)
            wait_for_form(driver)

            assert driver.find_element(By.NAME, "operation") is not None
            assert driver.find_element(By.NAME, "num1") is not None
            assert driver.find_element(By.NAME, "num2") is not None

            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            assert submit_button.text == "Calculate"

            print("✓ All form elements present")

        except Exception:
            take_screenshot(driver, "test_form_elements_present_FAILED")
            raise

    def test_addition_calculation(self, driver):
        try:
            driver.get(TEST_URL)
            wait_for_form(driver)

            Select(driver.find_element(By.NAME, "operation")).select_by_value("add")

            num1 = driver.find_element(By.NAME, "num1")
            num2 = driver.find_element(By.NAME, "num2")
            num1.clear()
            num2.clear()
            num1.send_keys("15")
            num2.send_keys("27")

            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )

            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "42" in result_div.text or "42.0" in result_div.text

            print("✓ Addition calculation works correctly (15 + 27 = 42)")

        except Exception:
            take_screenshot(driver, "test_addition_calculation_FAILED")
            raise

    def test_subtraction_calculation(self, driver):
        try:
            driver.get(TEST_URL)
            wait_for_form(driver)

            Select(driver.find_element(By.NAME, "operation")).select_by_value("subtract")

            num1 = driver.find_element(By.NAME, "num1")
            num2 = driver.find_element(By.NAME, "num2")
            num1.clear()
            num2.clear()
            num1.send_keys("100")
            num2.send_keys("42")

            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )

            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "58" in result_div.text

            print("✓ Subtraction calculation works correctly (100 - 42 = 58)")

        except Exception:
            take_screenshot(driver, "test_subtraction_calculation_FAILED")
            raise

    def test_multiplication_calculation(self, driver):
        try:
            driver.get(TEST_URL)
            wait_for_form(driver)

            Select(driver.find_element(By.NAME, "operation")).select_by_value("multiply")

            num1 = driver.find_element(By.NAME, "num1")
            num2 = driver.find_element(By.NAME, "num2")
            num1.clear()
            num2.clear()
            num1.send_keys("6")
            num2.send_keys("7")

            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )

            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "42" in result_div.text

            print("✓ Multiplication calculation works correctly (6 × 7 = 42)")

        except Exception:
            take_screenshot(driver, "test_multiplication_calculation_FAILED")
            raise

    def test_division_calculation(self, driver):
        try:
            driver.get(TEST_URL)
            wait_for_form(driver)

            Select(driver.find_element(By.NAME, "operation")).select_by_value("divide")

            num1 = driver.find_element(By.NAME, "num1")
            num2 = driver.find_element(By.NAME, "num2")
            num1.clear()
            num2.clear()
            num1.send_keys("84")
            num2.send_keys("2")

            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )

            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "42" in result_div.text

            print("✓ Division calculation works correctly (84 ÷ 2 = 42)")

        except Exception:
            take_screenshot(driver, "test_division_calculation_FAILED")
            raise

    def test_error_handling_divide_by_zero(self, driver):
        try:
            driver.get(TEST_URL)
            wait_for_form(driver)

            Select(driver.find_element(By.NAME, "operation")).select_by_value("divide")

            num1 = driver.find_element(By.NAME, "num1")
            num2 = driver.find_element(By.NAME, "num2")
            num1.clear()
            num2.clear()
            num1.send_keys("10")
            num2.send_keys("0")

            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error"))
            )

            error_div = driver.find_element(By.CLASS_NAME, "error")
            msg = error_div.text.lower()
            assert "divide by zero" in msg or "cannot divide by zero" in msg

            print("✓ Error handling works correctly for division by zero")

        except Exception:
            take_screenshot(driver, "test_error_handling_divide_by_zero_FAILED")
            raise

    def test_environment_display(self, driver):
        try:
            driver.get(TEST_URL)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "info"))
            )

            info_div = driver.find_element(By.CLASS_NAME, "info")
            assert "Environment:" in info_div.text

            print("✓ Environment information displayed")

        except Exception:
            take_screenshot(driver, "test_environment_display_FAILED")
            raise

    def test_api_documentation_visible(self, driver):
        try:
            driver.get(TEST_URL)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "api-docs"))
            )

            api_docs = driver.find_element(By.CLASS_NAME, "api-docs")
            assert "REST API Endpoints" in api_docs.text
            assert "/health" in api_docs.text
            assert "/api/calculate" in api_docs.text

            print("✓ API documentation section visible")

        except Exception:
            take_screenshot(driver, "test_api_documentation_visible_FAILED")
            raise


class TestCalculatorAPI:
    def test_api_health_json_structure(self, driver):
        try:
            driver.get(f"{TEST_URL}/health")

            page_source = driver.page_source
            assert '"status"' in page_source
            assert '"service"' in page_source
            assert '"version"' in page_source
            assert '"student"' in page_source

            print("✓ Health endpoint JSON structure valid")

        except Exception:
            take_screenshot(driver, "test_api_health_json_structure_FAILED")
            raise
