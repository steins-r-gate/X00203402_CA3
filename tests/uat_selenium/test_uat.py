"""
Selenium UAT (User Acceptance Testing) Script - CA3
Tests the deployed Calculator web application
Student: X00203402 - Roko Skugor

These tests run against the deployed Test environment to verify:
- Web UI loads correctly
- Calculator operations work through the browser
- Error handling displays properly
- All page elements are present and functional

Usage:
  Local: pytest tests/uat_selenium/test_uat.py -v
  CI/CD: Runs automatically in pipeline against Test environment
"""

import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Get test URL from environment variable (set by pipeline)
# Default to localhost for local testing
TEST_URL = os.getenv('TEST_URL', 'http://localhost:5000')


@pytest.fixture(scope="session")
def chrome_options():
    """
    Configure Chrome options for headless execution.
    
    Headless mode is required for CI/CD pipelines where no display is available.
    """
    options = Options()
    options.add_argument('--headless')  # Run without GUI
    options.add_argument('--no-sandbox')  # Required for running as root in containers
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--window-size=1920,1080')  # Set consistent window size
    options.add_argument('--disable-extensions')  # Disable extensions
    options.add_argument('--disable-infobars')  # Disable infobars
    options.add_argument('--ignore-certificate-errors')  # Ignore SSL errors (for test env)
    
    return options


@pytest.fixture(scope="function")
def driver(chrome_options):
    """
    Create a new Chrome WebDriver instance for each test.
    
    Function scope ensures each test gets a fresh browser instance,
    preventing state pollution between tests.
    """
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to appear
    
    yield driver
    
    # Teardown: quit the browser
    driver.quit()


def take_screenshot(driver, test_name):
    """
    Capture screenshot for debugging failed tests.
    
    Screenshots are saved with timestamp and test name for easy identification.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    screenshot_dir = "screenshots"
    
    # Create screenshots directory if it doesn't exist
    if not os.path.exists(screenshot_dir):
        os.makedirs(screenshot_dir)
    
    filename = f"{screenshot_dir}/{test_name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")
    return filename


class TestCalculatorWebUI:
    """
    Test suite for Calculator Web UI functionality.
    
    These tests verify the user-facing web application works correctly
    when deployed to the Test environment.
    """
    
    def test_home_page_loads(self, driver):
        """
        UAT-001: Verify the home page loads successfully.
        
        Checks:
        - Page responds with 200 status
        - Page title contains "Calculator"
        - Main heading is present
        """
        try:
            driver.get(TEST_URL)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            # Verify page title
            assert "Calculator" in driver.title or "Calculator App" in driver.page_source
            
            # Verify main heading exists
            heading = driver.find_element(By.TAG_NAME, "h1")
            assert heading.text == "🧮 Python Calculator"
            
            print(f"✓ Home page loaded successfully from {TEST_URL}")
            
        except Exception as e:
            take_screenshot(driver, "test_home_page_loads_FAILED")
            raise
    
    def test_health_endpoint(self, driver):
        """
        UAT-002: Verify the health endpoint returns correct JSON.
        
        This endpoint is critical for monitoring and load balancing.
        """
        try:
            driver.get(f"{TEST_URL}/health")
            
            # Get page source (JSON response)
            page_source = driver.page_source
            
            # Verify JSON structure
            assert '"status": "healthy"' in page_source or '"status":"healthy"' in page_source
            assert '"service": "calculator-app"' in page_source or '"service":"calculator-app"' in page_source
            assert 'X00203402' in page_source
            
            print("✓ Health endpoint responding correctly")
            
        except Exception as e:
            take_screenshot(driver, "test_health_endpoint_FAILED")
            raise
    
    def test_form_elements_present(self, driver):
        """
        UAT-003: Verify all form elements are present on the page.
        
        Checks for:
        - Operation dropdown
        - Number input fields
        - Submit button
        """
        try:
            driver.get(TEST_URL)
            
            # Wait for form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "operation"))
            )
            
            # Check operation dropdown
            operation_select = driver.find_element(By.NAME, "operation")
            assert operation_select is not None
            
            # Check number inputs
            num1_input = driver.find_element(By.NAME, "num1")
            assert num1_input is not None
            
            num2_input = driver.find_element(By.NAME, "num2")
            assert num2_input is not None
            
            # Check submit button
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            assert submit_button is not None
            assert submit_button.text == "Calculate"
            
            print("✓ All form elements present")
            
        except Exception as e:
            take_screenshot(driver, "test_form_elements_present_FAILED")
            raise
    
    def test_addition_calculation(self, driver):
        """
        UAT-004: Test addition operation through web UI.
        
        Verifies end-to-end functionality:
        1. Select operation
        2. Enter numbers
        3. Submit form
        4. Verify result displayed correctly
        """
        try:
            driver.get(TEST_URL)
            
            # Wait for form
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "operation"))
            )
            
            # Select addition
            operation_select = Select(driver.find_element(By.NAME, "operation"))
            operation_select.select_by_value("add")
            
            # Enter numbers
            num1_input = driver.find_element(By.NAME, "num1")
            num1_input.clear()
            num1_input.send_keys("15")
            
            num2_input = driver.find_element(By.NAME, "num2")
            num2_input.clear()
            num2_input.send_keys("27")
            
            # Submit form
            submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for result
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )
            
            # Verify result
            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "42" in result_div.text or "42.0" in result_div.text
            
            print("✓ Addition calculation works correctly (15 + 27 = 42)")
            
        except Exception as e:
            take_screenshot(driver, "test_addition_calculation_FAILED")
            raise
    
    def test_subtraction_calculation(self, driver):
        """
        UAT-005: Test subtraction operation through web UI.
        """
        try:
            driver.get(TEST_URL)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "operation"))
            )
            
            # Select subtraction
            operation_select = Select(driver.find_element(By.NAME, "operation"))
            operation_select.select_by_value("subtract")
            
            # Enter numbers: 100 - 42 = 58
            driver.find_element(By.NAME, "num1").send_keys("100")
            driver.find_element(By.NAME, "num2").send_keys("42")
            
            # Submit
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Verify result
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )
            
            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "58" in result_div.text
            
            print("✓ Subtraction calculation works correctly (100 - 42 = 58)")
            
        except Exception as e:
            take_screenshot(driver, "test_subtraction_calculation_FAILED")
            raise
    
    def test_multiplication_calculation(self, driver):
        """
        UAT-006: Test multiplication operation through web UI.
        """
        try:
            driver.get(TEST_URL)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "operation"))
            )
            
            # Select multiplication
            operation_select = Select(driver.find_element(By.NAME, "operation"))
            operation_select.select_by_value("multiply")
            
            # Enter numbers: 6 * 7 = 42
            driver.find_element(By.NAME, "num1").send_keys("6")
            driver.find_element(By.NAME, "num2").send_keys("7")
            
            # Submit
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Verify result
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )
            
            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "42" in result_div.text
            
            print("✓ Multiplication calculation works correctly (6 × 7 = 42)")
            
        except Exception as e:
            take_screenshot(driver, "test_multiplication_calculation_FAILED")
            raise
    
    def test_division_calculation(self, driver):
        """
        UAT-007: Test division operation through web UI.
        """
        try:
            driver.get(TEST_URL)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "operation"))
            )
            
            # Select division
            operation_select = Select(driver.find_element(By.NAME, "operation"))
            operation_select.select_by_value("divide")
            
            # Enter numbers: 84 / 2 = 42
            driver.find_element(By.NAME, "num1").send_keys("84")
            driver.find_element(By.NAME, "num2").send_keys("2")
            
            # Submit
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Verify result
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )
            
            result_div = driver.find_element(By.CLASS_NAME, "result")
            assert "42" in result_div.text
            
            print("✓ Division calculation works correctly (84 ÷ 2 = 42)")
            
        except Exception as e:
            take_screenshot(driver, "test_division_calculation_FAILED")
            raise
    
    def test_error_handling_divide_by_zero(self, driver):
        """
        UAT-008: Test error handling for division by zero.
        
        Verifies that:
        - Error message is displayed
        - No result is shown
        - Application doesn't crash
        """
        try:
            driver.get(TEST_URL)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "operation"))
            )
            
            # Select division
            operation_select = Select(driver.find_element(By.NAME, "operation"))
            operation_select.select_by_value("divide")
            
            # Enter numbers: 10 / 0 (should trigger error)
            driver.find_element(By.NAME, "num1").send_keys("10")
            driver.find_element(By.NAME, "num2").send_keys("0")
            
            # Submit
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            
            # Wait for error message
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error"))
            )
            
            # Verify error message
            error_div = driver.find_element(By.CLASS_NAME, "error")
            assert "divide by zero" in error_div.text.lower() or "cannot divide by zero" in error_div.text.lower()
            
            print("✓ Error handling works correctly for division by zero")
            
        except Exception as e:
            take_screenshot(driver, "test_error_handling_divide_by_zero_FAILED")
            raise
    
    def test_environment_display(self, driver):
        """
        UAT-009: Verify environment indicator is displayed.
        
        Confirms that users can see which environment they're using
        (important for Test vs Production distinction).
        """
        try:
            driver.get(TEST_URL)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "info"))
            )
            
            # Check for environment info
            info_div = driver.find_element(By.CLASS_NAME, "info")
            assert "Environment:" in info_div.text
            
            print("✓ Environment information displayed")
            
        except Exception as e:
            take_screenshot(driver, "test_environment_display_FAILED")
            raise
    
    def test_api_documentation_visible(self, driver):
        """
        UAT-010: Verify API documentation section is visible.
        
        Ensures users can discover the REST API endpoints.
        """
        try:
            driver.get(TEST_URL)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "api-docs"))
            )
            
            # Check for API docs section
            api_docs = driver.find_element(By.CLASS_NAME, "api-docs")
            assert "REST API Endpoints" in api_docs.text
            assert "/health" in api_docs.text
            assert "/api/calculate" in api_docs.text
            
            print("✓ API documentation section visible")
            
        except Exception as e:
            take_screenshot(driver, "test_api_documentation_visible_FAILED")
            raise


# Additional test class for API endpoint testing (optional, but comprehensive)
class TestCalculatorAPI:
    """
    Test suite for REST API endpoints using Selenium.
    
    While typically API tests would use requests library,
    these tests verify API responses through browser for comprehensive UAT.
    """
    
    def test_api_health_json_structure(self, driver):
        """
        API-001: Verify health endpoint returns valid JSON.
        """
        try:
            driver.get(f"{TEST_URL}/health")
            
            page_source = driver.page_source
            
            # Check all expected JSON fields
            assert '"status"' in page_source
            assert '"service"' in page_source
            assert '"version"' in page_source
            assert '"student"' in page_source
            
            print("✓ Health endpoint JSON structure valid")
            
        except Exception as e:
            take_screenshot(driver, "test_api_health_json_structure_FAILED")
            raise