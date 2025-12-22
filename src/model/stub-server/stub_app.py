from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze_code():
    """
    Mock endpoints that mici the extension's analysis. 
    Accpets json -> {"code": "string_of_code" }
    Returns -> {"complexity": "O(x)", "loops_detected": int "explanation": "..." }
    """

    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "Missing 'code' field in request"}), 400
    
    code = data['code']

    # heuristics for "analysis" frontend mock
    loop_count = len(re.findall(r'\b(for|while)\b', code))
    function_count = len(re.findall(r'\bdef |function|=>', code))

    # determine complexity using extension.tx pre-backend logic
    complexity = 'O(1)'
    if loop_count > 0 and function_count == 0:
        complexity = 'O(n)'
    elif loop_count > 1:
        complexity = 'O(n²)'
    elif function_count > 2:
        complexity = 'O(n log n)'


    response = {
        "complexity": complexity,
        "loops_detected": loop_count, 
        "functions_detected": function_count, 
        "explanation": f"Mock analysis based on {loop_count} loops and {function_count} functions."
    }

    return jsonify(response), 200

@app.route('/health', methods=['GET'])
def health_check():
    """ Health check endpoint """
    return jsonify({"status": "ok", "message": "Flask server stub running."}), 200

if __name__ == "__main__":
    print("Starting flask stub server...")
    print("Endpoints:")
    print("  POST /analyze - Code complexity analysis")
    print("  GET  /health  - Health check")
    app.run(host='0.0.0.0', port=5000, debug=True)
