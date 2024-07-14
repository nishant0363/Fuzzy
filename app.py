from flask import Flask, request, send_file, render_template
import os
import subprocess

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['OUTPUT_FOLDER'] = 'outputs/'

# Existing routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.csv')
        file.save(file_path)

        # Run the Jupyter notebook
        subprocess.run(['jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--output', 'process_notebook_output.ipynb', 'process_notebook.ipynb'])

        output_path = os.path.join(app.config['OUTPUT_FOLDER'], 'output.csv')
        return send_file(output_path, as_attachment=True, download_name='output.csv')

# New route to serve updates from mapping.txt
@app.route('/updates')
def get_mapping_updates():
    updates = ''
    with open('mapping.txt', 'r') as file:
        updates = file.read()
    return updates

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
