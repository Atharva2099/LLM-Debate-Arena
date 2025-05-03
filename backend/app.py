"""
LLM Debate Arena - Flask API
This module provides the API endpoints for the LLM Debate Arena
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from typing import Dict, Any

from debate_manager import DebateManager
from llm_api_service import LLMApiService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend/build')
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Enable CORS for all /api/ routes

# Initialize the debate manager and API service
debate_manager = DebateManager()
api_service = LLMApiService()

# API Keys storage (in memory for demonstration, use a secure storage in production)
api_keys = {}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve the frontend application"""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/debate/start', methods=['POST'])
def start_debate():
    """Start a new debate"""
    try:
        # Start a new debate
        debate_status = debate_manager.start_new_debate()
        return jsonify(debate_status), 200
    except Exception as e:
        logger.error(f"Error starting debate: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debate/progress', methods=['POST'])
def progress_debate():
    """Progress the debate to the next step"""
    try:
        # Progress the debate
        debate_status = debate_manager.progress_debate()
        return jsonify(debate_status), 200
    except Exception as e:
        logger.error(f"Error progressing debate: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debate/toggle', methods=['POST'])
def toggle_debate():
    """Toggle the debate running state (pause/resume)"""
    try:
        # Toggle the debate running state
        debate_status = debate_manager.toggle_debate_running()
        return jsonify(debate_status), 200
    except Exception as e:
        logger.error(f"Error toggling debate state: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debate/status', methods=['GET'])
def get_debate_status():
    """Get the current debate status"""
    try:
        # Get the current debate status
        debate_status = debate_manager.get_debate_status()
        return jsonify(debate_status), 200
    except Exception as e:
        logger.error(f"Error getting debate status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debate/export', methods=['GET'])
def export_debate():
    """Export the debate log"""
    try:
        # Get the format parameter (default to markdown)
        format_type = request.args.get('format', 'markdown')
        
        # Export the debate log
        debate_log = debate_manager.export_debate(format_type=format_type)
        
        return jsonify({"log": debate_log, "format": format_type}), 200
    except Exception as e:
        logger.error(f"Error exporting debate: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/keys', methods=['POST'])
def update_api_keys():
    """Update the API keys"""
    try:
        # Get the API keys from the request
        data = request.json
        
        # Validate the request data
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request data"}), 400
        
        # Update the API keys
        global api_keys
        api_keys = data
        
        # Update the API keys in the API service
        api_service.update_api_keys(api_keys)
        
        # Return success
        return jsonify({"message": "API keys updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating API keys: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_llm_response():
    """Generate a response from an LLM"""
    try:
        # Get the data from the request
        data = request.json
        
        # Validate the request data
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid request data"}), 400
        
        # Extract the parameters
        model_id = data.get('model_id')
        prompt = data.get('prompt')
        max_tokens = data.get('max_tokens', 250)
        temperature = data.get('temperature', 0.7)
        
        # Validate the required parameters
        if not model_id or not prompt:
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Generate the response
        response = api_service.generate_response(
            model_id=model_id,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Return the response
        return jsonify({"response": response}), 200
    except Exception as e:
        logger.error(f"Error generating LLM response: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Get the port from the environment (for deployment)
    port = int(os.environ.get('PORT', 5001))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=True)