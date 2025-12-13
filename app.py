"""
Flask Web Application for Calculator - CA3
Provides web interface and REST API for the Calculator class
Student: X00203402 - Roko Skugor
"""
import os
import sys

# Ensure project root is on Python path (fixes Azure App Service imports)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string, request, jsonify
from src.calculator import Calculator

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
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Render the calculator web interface"""
    import os
    environment = os.getenv('ENVIRONMENT', 'Development')
    return render_template_string(HTML_TEMPLATE, result=None, error=None, environment=environment)


@app.route('/', methods=['POST'])
def calculate():
    """Handle calculation requests from the web form"""
    import os
    environment = os.getenv('ENVIRONMENT', 'Development')
    
    try:
        operation = request.form.get('operation')
        num1 = float(request.form.get('num1'))
        
        # Square root only needs one number
        if operation == 'square_root':
            result = calc.square_root(num1)
        else:
            num2 = float(request.form.get('num2'))
            
            if operation == 'add':
                result = calc.add(num1, num2)
            elif operation == 'subtract':
                result = calc.subtract(num1, num2)
            elif operation == 'multiply':
                result = calc.multiply(num1, num2)
            elif operation == 'divide':
                result = calc.divide(num1, num2)
            elif operation == 'power':
                result = calc.power(num1, num2)
            elif operation == 'modulo':
                result = calc.modulo(num1, num2)
            elif operation == 'percentage':
                result = calc.percentage(num1, num2)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        
        return render_template_string(HTML_TEMPLATE, result=result, error=None, environment=environment)
    
    except ValueError as e:
        return render_template_string(HTML_TEMPLATE, result=None, error=str(e), environment=environment)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, result=None, error=f"Error: {str(e)}", environment=environment)


@app.route('/health')
def health():
    """
    Health check endpoint for monitoring and testing
    Used by: Performance tests, UAT tests, Azure health probes
    """
    return jsonify({
        'status': 'healthy',
        'service': 'calculator-app',
        'version': '2.0',
        'student': 'X00203402'
    }), 200


@app.route('/api/calculate', methods=['POST'])
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
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON payload provided'}), 400
        
        operation = data.get('operation')
        num1 = data.get('num1')
        
        if operation is None or num1 is None:
            return jsonify({'error': 'Missing required fields: operation, num1'}), 400
        
        num1 = float(num1)
        
        # Square root only needs one number
        if operation == 'square_root':
            result = calc.square_root(num1)
        else:
            num2 = data.get('num2')
            if num2 is None:
                return jsonify({'error': f'Operation {operation} requires num2'}), 400
            
            num2 = float(num2)
            
            if operation == 'add':
                result = calc.add(num1, num2)
            elif operation == 'subtract':
                result = calc.subtract(num1, num2)
            elif operation == 'multiply':
                result = calc.multiply(num1, num2)
            elif operation == 'divide':
                result = calc.divide(num1, num2)
            elif operation == 'power':
                result = calc.power(num1, num2)
            elif operation == 'modulo':
                result = calc.modulo(num1, num2)
            elif operation == 'percentage':
                result = calc.percentage(num1, num2)
            else:
                return jsonify({'error': f'Unknown operation: {operation}'}), 400
        
        return jsonify({
            'operation': operation,
            'num1': num1,
            'num2': num2 if operation != 'square_root' else None,
            'result': result
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)