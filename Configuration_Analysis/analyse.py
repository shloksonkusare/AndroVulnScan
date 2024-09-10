import os
import zipfile
from flask import Flask, request, send_file, render_template
from xml.dom import minidom
import json
from fpdf import FPDF
from pathlib import Path

app = Flask(__name__)

# Path to the Downloads folder
DOWNLOADS_PATH = str(Path.home() / "Downloads")

# Function to analyze AndroidManifest.xml
def analyze_android_manifest(xml_file):
    try:
        manifest = minidom.parse(xml_file)
        permissions = manifest.getElementsByTagName("uses-permission")
        permission_list = [p.getAttribute("android:name") for p in permissions]
        return {"permissions": permission_list}
    except Exception as e:
        return {"error": str(e)}

# Function to analyze build.gradle
def analyze_gradle(gradle_file):
    analysis = {}
    try:
        with open(gradle_file, "r") as file:
            content = file.readlines()
            for line in content:
                if "minSdkVersion" in line:
                    analysis["minSdkVersion"] = line.split()[1]
                if "targetSdkVersion" in line:
                    analysis["targetSdkVersion"] = line.split()[1]
                if "compileSdkVersion" in line:
                    analysis["compileSdkVersion"] = line.split()[1]
    except Exception as e:
        return {"error": str(e)}
    return analysis

# Function to generate PDF report
def generate_pdf_report(analysis, report_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt="Android Project Analysis Report", ln=True, align="C")
    pdf.ln(10)

    # Add Manifest Analysis
    pdf.cell(200, 10, txt="AndroidManifest.xml Analysis:", ln=True, align="L")
    if "permissions" in analysis['manifest']:
        pdf.cell(200, 10, txt=f"Permissions: {', '.join(analysis['manifest']['permissions'])}", ln=True, align="L")
    else:
        pdf.cell(200, 10, txt="Error analyzing AndroidManifest.xml", ln=True, align="L")
    
    pdf.ln(10)
    
    # Add Gradle Analysis
    pdf.cell(200, 10, txt="build.gradle Analysis:", ln=True, align="L")
    if "error" in analysis['gradle']:
        pdf.cell(200, 10, txt="Error analyzing build.gradle", ln=True, align="L")
    else:
        for key, value in analysis['gradle'].items():
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True, align="L")

    # Save the report to the Downloads folder
    report_path = os.path.join(DOWNLOADS_PATH, report_name)
    pdf.output(report_path)
    return report_path

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded", 400

    zip_file = request.files['file']
    if zip_file.filename == '':
        return "No selected file", 400

    # Save the uploaded file to a temporary location
    temp_zip_path = os.path.join(DOWNLOADS_PATH, zip_file.filename)
    zip_file.save(temp_zip_path)

    try:
        # Extract the ZIP file
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            extract_path = os.path.join(DOWNLOADS_PATH, "extracted_project")
            zip_ref.extractall(extract_path)

        # Analyze AndroidManifest.xml
        manifest_path = os.path.join(extract_path, 'app', 'src', 'main', 'AndroidManifest.xml')
        manifest_analysis = analyze_android_manifest(manifest_path)

        # Analyze build.gradle
        gradle_path = os.path.join(extract_path, 'app', 'build.gradle')
        gradle_analysis = analyze_gradle(gradle_path)

        # Combine analysis
        analysis = {
            "manifest": manifest_analysis,
            "gradle": gradle_analysis
        }

        # Generate PDF report
        report_name = "android_project_analysis_report.pdf"
        report_path = generate_pdf_report(analysis, report_name)

        # Send the generated report to the user
        return send_file(report_path, as_attachment=True)

    finally:
        # Clean up extracted files and temp ZIP
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        if os.path.exists(extract_path):
            for root, dirs, files in os.walk(extract_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(extract_path)

if __name__ == "__main__":
    app.run(debug=True)
