"""
Locust Performance Testing Script - CA3
Load testing for Calculator Flask Application
Student: X00203402 - Roko Skugor

Usage:
  Local testing:
    locust -f locustfile.py --host http://localhost:5000
  
  Headless mode (CI/CD):
    locust -f locustfile.py --headless --users 10 --spawn-rate 2 \
           --run-time 30s --host http://localhost:5000
"""

from locust import HttpUser, task, between
import random


class CalculatorUser(HttpUser):
    """
    Simulates a user interacting with the Calculator application.
    
    This class defines user behavior patterns for load testing:
    - Wait time between requests: 1-3 seconds (simulates real user think time)
    - Multiple tasks with different weights (priorities)
    - Tests both web UI and REST API endpoints
    """
    
    # Wait between 1 and 3 seconds between tasks
    # Simulates real user "think time"
    wait_time = between(1, 3)
    
    def on_start(self):
        """
        Called when a simulated user starts.
        Used for setup tasks like login (not needed for this app).
        """
        # Verify the application is running
        response = self.client.get("/health")
        if response.status_code != 200:
            print(f"WARNING: Health check failed with status {response.status_code}")
    
    @task(10)
    def health_check(self):
        """
        Test the health endpoint.
        Weight: 10 (runs 10x more often than weight=1 tasks)
        
        This endpoint is critical for:
        - Azure health probes
        - Load balancer health checks
        - Monitoring systems
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response_json = response.json()
                if response_json.get('status') == 'healthy':
                    response.success()
                else:
                    response.failure(f"Health check returned unhealthy status: {response_json}")
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    @task(5)
    def home_page(self):
        """
        Test the home page load.
        Weight: 5 (medium priority)
        
        Tests the web UI rendering performance.
        """
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                if "Calculator App" in response.text:
                    response.success()
                else:
                    response.failure("Home page doesn't contain expected content")
            else:
                response.failure(f"Home page failed with status {response.status_code}")
    
    @task(3)
    def api_add(self):
        """
        Test the addition API endpoint.
        Weight: 3
        """
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        expected_result = num1 + num2
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "add", "num1": num1, "num2": num2},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                if result == expected_result:
                    response.success()
                else:
                    response.failure(f"Addition failed: {num1} + {num2} = {result}, expected {expected_result}")
            else:
                response.failure(f"API add failed with status {response.status_code}")
    
    @task(3)
    def api_subtract(self):
        """
        Test the subtraction API endpoint.
        Weight: 3
        """
        num1 = random.randint(50, 150)
        num2 = random.randint(1, 50)
        expected_result = num1 - num2
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "subtract", "num1": num1, "num2": num2},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                if result == expected_result:
                    response.success()
                else:
                    response.failure(f"Subtraction failed: {num1} - {num2} = {result}, expected {expected_result}")
            else:
                response.failure(f"API subtract failed with status {response.status_code}")
    
    @task(3)
    def api_multiply(self):
        """
        Test the multiplication API endpoint.
        Weight: 3
        """
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 20)
        expected_result = num1 * num2
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "multiply", "num1": num1, "num2": num2},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                if result == expected_result:
                    response.success()
                else:
                    response.failure(f"Multiplication failed: {num1} * {num2} = {result}, expected {expected_result}")
            else:
                response.failure(f"API multiply failed with status {response.status_code}")
    
    @task(2)
    def api_divide(self):
        """
        Test the division API endpoint.
        Weight: 2
        """
        num1 = random.randint(10, 100)
        num2 = random.randint(1, 10)
        expected_result = num1 / num2
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "divide", "num1": num1, "num2": num2},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                # Use approximate comparison for floating point
                if abs(result - expected_result) < 0.0001:
                    response.success()
                else:
                    response.failure(f"Division failed: {num1} / {num2} = {result}, expected {expected_result}")
            else:
                response.failure(f"API divide failed with status {response.status_code}")
    
    @task(2)
    def api_power(self):
        """
        Test the power API endpoint.
        Weight: 2
        """
        num1 = random.randint(2, 10)
        num2 = random.randint(2, 5)  # Keep exponents small to avoid huge numbers
        expected_result = num1 ** num2
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "power", "num1": num1, "num2": num2},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                if result == expected_result:
                    response.success()
                else:
                    response.failure(f"Power failed: {num1} ^ {num2} = {result}, expected {expected_result}")
            else:
                response.failure(f"API power failed with status {response.status_code}")
    
    @task(2)
    def api_square_root(self):
        """
        Test the square root API endpoint.
        Weight: 2
        """
        num1 = random.randint(1, 100)
        expected_result = num1 ** 0.5
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "square_root", "num1": num1},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                # Use approximate comparison for floating point
                if abs(result - expected_result) < 0.0001:
                    response.success()
                else:
                    response.failure(f"Square root failed: √{num1} = {result}, expected {expected_result}")
            else:
                response.failure(f"API square_root failed with status {response.status_code}")
    
    @task(1)
    def api_modulo(self):
        """
        Test the modulo API endpoint.
        Weight: 1 (lowest priority)
        """
        num1 = random.randint(10, 100)
        num2 = random.randint(3, 10)
        expected_result = num1 % num2
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "modulo", "num1": num1, "num2": num2},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                if result == expected_result:
                    response.success()
                else:
                    response.failure(f"Modulo failed: {num1} % {num2} = {result}, expected {expected_result}")
            else:
                response.failure(f"API modulo failed with status {response.status_code}")
    
    @task(1)
    def api_percentage(self):
        """
        Test the percentage API endpoint.
        Weight: 1
        """
        num1 = random.randint(100, 1000)
        num2 = random.randint(5, 50)
        expected_result = (num1 * num2) / 100
        
        with self.client.post(
            "/api/calculate",
            json={"operation": "percentage", "num1": num1, "num2": num2},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json().get('result')
                if abs(result - expected_result) < 0.01:
                    response.success()
                else:
                    response.failure(f"Percentage failed: {num2}% of {num1} = {result}, expected {expected_result}")
            else:
                response.failure(f"API percentage failed with status {response.status_code}")
    
    @task(1)
    def api_error_handling_divide_by_zero(self):
        """
        Test error handling for division by zero.
        Weight: 1
        
        This should return a 400 error with proper error message.
        """
        with self.client.post(
            "/api/calculate",
            json={"operation": "divide", "num1": 10, "num2": 0},
            catch_response=True
        ) as response:
            if response.status_code == 400:
                error = response.json().get('error')
                if 'divide by zero' in error.lower() or 'cannot divide by zero' in error.lower():
                    response.success()
                else:
                    response.failure(f"Divide by zero error message unexpected: {error}")
            else:
                response.failure(f"Divide by zero should return 400, got {response.status_code}")