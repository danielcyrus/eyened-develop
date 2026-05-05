import csv
import json
import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for

app = Flask(__name__)

PDF_FOLDER = 'pdfs'
JSON_FOLDER = 'output'
CSV_FILE = 'patient_records.csv'

# The structure to show if no JSON is found
DEFAULT_DATA = {
    "name": "", "Date of Birth": "", "Gender": "", "NHS Number": "",
    "Patient Postcode": "", "Patient Town": "", "Visual Status": "",
    "Form Version": "", "Registration Date": "", "Patient Date": "",
    "Signatory Is": "",
    "Boolean Questions": {
        "Live alone?": "", "Support with care?": "", "Poor mobility?": "",
        "Hearing impairment?": "", "Learning disability?": "", "Dementia?": "",
        "Specialist education service?": ""
    },
    "Employment status": "", "Ethnicity": "", "Diagnosis Source": "",
    "Right Eye Diagnosis": "", "Left Eye Diagnosis": "", 
    "Main Diagnosis": "", "hospital_name": ""
}

def get_pdf_list():
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    return sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')])

def flatten_dict(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

@app.route('/')
def index():
    pdfs = get_pdf_list()
    # Force index to be at least 0
    current_index = max(1, int(request.args.get('index', 1)))
    
    if not pdfs:
        return "<h1>No PDFs found</h1><p>Please add PDF files to the 'pdfs' folder.</p>"
    
    if current_index >= len(pdfs):
        return "<h1>Processing Complete</h1><p>All files have been reviewed.</p>"

    current_pdf = pdfs[current_index]
    json_filename = current_pdf.replace('.pdf', '.json')
    json_path = os.path.join(JSON_FOLDER, json_filename)
    
    # Load existing data OR use a fresh copy of the default
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
    else:
        # Crucial: Use .copy() to prevent dictionary mutation errors
        data = json.loads(json.dumps(DEFAULT_DATA))

    return render_template('index.html', data=data, pdf_file=current_pdf, index=current_index)

@app.route('/save', methods=['POST'])
def save():
    index = int(request.form.get('index'))
    
    # Reconstruct dictionary from form
    updated_data = {
        "name": request.form.get("name"),
        "Date of Birth": request.form.get("Date of Birth"),
        "Gender": request.form.get("Gender"),
        "NHS Number": request.form.get("NHS Number"),
        "Patient Postcode": request.form.get("Patient Postcode"),
        "Patient Town": request.form.get("Patient Town"),
        "Visual Status": request.form.get("Visual Status"),
        "Form Version": request.form.get("Form Version"),
        "Registration Date": request.form.get("Registration Date"),
        "Patient Date": request.form.get("Patient Date"),
        "Signatory Is": request.form.get("Signatory Is"),
        "Boolean Questions": {
            "Live alone?": request.form.get("Live alone?"),
            "Support with care?": request.form.get("Support with care?"),
            "Poor mobility?": request.form.get("Poor mobility?"),
            "Hearing impairment?": request.form.get("Hearing impairment?"),
            "Learning disability?": request.form.get("Learning disability?"),
            "Dementia?": request.form.get("Dementia?"),
            "Specialist education service?": request.form.get("Specialist education service?"),
        },
        "Employment status": request.form.get("Employment status"),
        "Ethnicity": request.form.get("Ethnicity"),
        "Diagnosis Source": request.form.get("Diagnosis Source"),
        "Right Eye Diagnosis": request.form.get("Right Eye Diagnosis"),
        "Left Eye Diagnosis": request.form.get("Left Eye Diagnosis"),
        "Main Diagnosis": request.form.get("Main Diagnosis"),
        "hospital_name": request.form.get("hospital_name")
    }

    flat_data = flatten_dict(updated_data)
    
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=flat_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(flat_data)

    return redirect(url_for('index', index=index + 1))

@app.route('/pdfs/<path:filename>')
def serve_pdf(filename):
    return send_from_directory(PDF_FOLDER, filename)

if __name__ == '__main__':
    if not os.path.exists(JSON_FOLDER):
        os.makedirs(JSON_FOLDER)
    app.run(debug=True, port=1874)
