"""
Flask Web Application for Calculator - CA3
Provides web interface and REST API for the Calculator class
Student: X00203402 - Roko Skugor
"""
import os
import sys

from flask import Flask, jsonify, render_template_string, request

# Ensure project root is on Python path (fixes Azure App Service imports)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.calculator import Calculator  # noqa: E402  (import after sys.path fix)

app = Flask(__name__)
calc = Calculator()

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculator App - X00203402</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .calculator-form {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }
        input, select {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #5568d3;
        }
        .result {
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #4caf50;
        }
        .error {
            background: #ffebee;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            border-left: 4px solid #f44336;
        }
        .info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
        }
        .api-docs {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .api-docs h2 {
            color: #667eea;
            margin-bottom: 15px;
        }
        .endpoint {
            background: white;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧮 Python Calculator</h1>
        <p class="subtitle">DevOps CI/CD Project - CA3</p>

        <div class="calculator-form">
            <form method="POST" action="/">
                <div class="form-group">
                    <label for="operation">Operation:</label>
                    <select name="operation" id="operation" required>
                        <option value="add">Addition (+)</option>
                        <option value="subtract">Subtraction (-)</option>
                        <option value="multiply">Multiplication (×)</option>
                        <option value="divide">Division (÷)</option>
                        <option value="power">Power (x^y)</option>
                        <option value="square_root">Square Root (√x)</option>
                        <option value="modulo">Modulo (%)</option>
                        <option value="percentage">Percentage</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="num1">First Number:</label>
                    <input type="number" step="any" name="num1" id="num1" required>
                </div>

                <div class="form-group" id="num2-group">
                    <label for="num2">Second Number:</label>
                    <input type="number" step="any" name="num2" id="num2">
                </div>

                <button type="submit">Calculate</button>
            </form>
        </div>

        {% if result is not none %}
        <div class="result">
            <strong>Result:</strong> {{ result }}
        </div>
        {% endif %}

        {% if error %}
        <div class="error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% endif %}

        <div class="info">
            <p><strong>Environment:</strong> {{ environment }}</p>
            <p><strong>Version:</strong> 2.0 (CA3)</p>
        </div>

        <div class="api-docs">
            <h2>📡 REST API Endpoints</h2>
            <p>This calculator also provides REST API endpoints:</p>
            <div class="endpoint">GET /health - Health check endpoint</div>
            <div class="endpoint">POST /api/calculate - Calculate with JSON payload</div>
            <p style="margin-top: 15px; font-size: 14px; color: #666;">
                Example: POST /api/calculate with body:
                {"operation": "add", "num1": 5, "num2": 3}
            </p>
        </div>
    </div>

    <script>
        // Hide second number field for square root operation
        document.getElementById('operation').addEventListener('change', function() {
            const num2Group = document.getElementById('num2-group');
            const num2Input = document.getElementById('num2');
            if (this.value === 'square_root') {
                num2Group.style.display = 'none';
                num2Input.removeAttribute('required');
            } else {
                num2Group.style.display = 'block';
                num2Input.setAttribute('required', 'required');
            }
        });

        // Trigger on page load to ensure correct initial state
        document.getElementById('operation').dispatchEvent(new Event('change'));
    </script>
</body>
</html>
"""


def _get_environment_label() -> str:
    return os.getenv("ENVIRONMENT", "Development")


def _perform_calculation(operation: str, num1: float, num2: float | None) -> float:
    """Centralized calculation logic for both web form and API."""
    if operation == "square_root":
        return calc.square_root(num1)

    if num2 is None:
        raise ValueError(f"Operation {operation} requires num2")

    if operation == "add":
        return calc.add(num1, num2)
    if operation == "subtract":
        return calc.subtract(num1, num2)
    if operation == "multiply":
        return calc.multiply(num1, num2)
    if operation == "divide":
        return calc.divide(num1, num2)
    if operation == "power":
        return calc.power(num1, num2)
    if operation == "modulo":
        return calc.modulo(num1, num2)
    if operation == "percentage":
        return calc.percentage(num1, num2)

    raise ValueError(f"Unknown operation: {operation}")


@app.route("/", methods=["GET"])
def index():
    """Render the calculator web interface."""
    return render_template_string(
        HTML_TEMPLATE, result=None, error=None, environment=_get_environment_label()
    )


@app.route("/", methods=["POST"])
def calculate():
    """Handle calculation requests from the web form."""
    environment = _get_environment_label()

    try:
        operation = request.form.get("operation", "").strip()
        num1_raw = request.form.get("num1", None)

        if num1_raw is None or num1_raw == "":
            raise ValueError("Missing num1")

        num1 = float(num1_raw)

        num2: float | None = None
        if operation != "square_root":
            num2_raw = request.form.get("num2", None)
            if num2_raw is None or num2_raw == "":
                raise ValueError(f"Operation {operation} requires num2")
            num2 = float(num2_raw)

        result = _perform_calculation(operation, num1, num2)

        return render_template_string(
            HTML_TEMPLATE, result=result, error=None, environment=environment
        )
    except ValueError as e:
        return render_template_string(
            HTML_TEMPLATE, result=None, error=str(e), environment=environment
        )
    except Exception as e:
        return render_template_string(
            HTML_TEMPLATE, result=None, error=f"Error: {str(e)}", environment=environment
        )


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint for monitoring and testing
    Used by: Performance tests, UAT tests, Azure health probes
    """
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "calculator-app",
                "version": "2.0",
                "student": "X00203402",
            }
        ),
        200,
    )


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    REST API endpoint for calculator operations
    Expected JSON payload:
    {
        "operation": "add|subtract|multiply|divide|power|square_root|modulo|percentage",
        "num1": <number>,
        "num2": <number>  (optional for square_root)
    }
    """
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        operation = data.get("operation", None)
        num1 = data.get("num1", None)

        if not operation or num1 is None:
            return jsonify({"error": "Missing required fields: operation, num1"}), 400

        operation = str(operation).strip()
        num1_f = float(num1)

        num2_f: float | None = None
        if operation != "square_root":
            if "num2" not in data or data.get("num2") is None:
                return jsonify({"error": f"Operation {operation} requires num2"}), 400
            num2_f = float(data.get("num2"))

        result = _perform_calculation(operation, num1_f, num2_f)

        return (
            jsonify(
                {
                    "operation": operation,
                    "num1": num1_f,
                    "num2": num2_f if operation != "square_root" else None,
                    "result": result,
                }
            ),
            200,
        )

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    # Safe defaults: no debug, bind to localhost only.
    # Override in environment for local dev if needed:
    #   set FLASK_DEBUG=1
    #   set FLASK_HOST=127.0.0.1   (or 0.0.0.0 only if you really need it)
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    host = os.getenv("FLASK_HOST", "127.0.0.1")

    app.run(host=host, port=port, debug=debug)
