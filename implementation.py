from flask import Flask, request, jsonify, render_template, send_file
import os
import threading
import subprocess
from werkzeug.utils import secure_filename
import sys


# Initialize the Flask app
app = Flask(__name__)


# Define folder paths for storing uploaded papers and results
UPLOAD_FOLDER = 'papers'
RESULTS_FOLDER = 'results'
SUMMARY_FILE = os.path.join(RESULTS_FOLDER, 'summaries.txt')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Dictionary to track the processing status of the summarization task
processing_status = {
    'in_progress': False,
    'done': False
}



# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


# Route to render the main page (index)
@app.route('/')
def index():
    return render_template('main.html')



# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify({'error': 'Invalid file'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        os.remove(file_path)
    file.save(file_path)

    return jsonify({'status': 'uploaded', 'filename': filename}), 200



# Route to start the summarization process
@app.route('/start_summary', methods=['POST'])
def start_summary():
    if processing_status['in_progress']:
        return jsonify({'status': 'already running'}), 202

    def run_summary_pipeline():
        processing_status['in_progress'] = True
        processing_status['done'] = False

        if os.path.exists(SUMMARY_FILE):
            os.remove(SUMMARY_FILE)

        try:
            subprocess.run([sys.executable, 'final.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running final.py: {e}")
        finally:
            processing_status['in_progress'] = False
            processing_status['done'] = True

    threading.Thread(target=run_summary_pipeline).start()
    return jsonify({'status': 'started'}), 202



# Route to check the current status of the summarization task
@app.route('/check_progress')
def check_progress():
    return jsonify(processing_status)



# Route to retrieve the generated summary (if available)
@app.route('/get_summary')
def get_summary():
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'r') as f:
            return f.read()
    return "Summary not ready", 404


# Route to download the generated summary file
@app.route('/download_summary')
def download_summary():
    if os.path.exists(SUMMARY_FILE):
        return send_file(SUMMARY_FILE, as_attachment=True)
    return "Summary file not found", 404


# Route to view the knowledge graph image (if generated)
@app.route('/view_graph')
def view_graph():
    graph_path = os.path.join(RESULTS_FOLDER, 'graph.png')
    if os.path.exists(graph_path):
        return send_file(graph_path, mimetype='image/png')
    return "Graph not available", 404


# Route to download the combined summary file
def view_combined():
    path = os.path.join(RESULTS_FOLDER, 'combined_summary.txt')
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Combined summary file not found", 404

if __name__ == '__main__':
    app.run(debug=True)

