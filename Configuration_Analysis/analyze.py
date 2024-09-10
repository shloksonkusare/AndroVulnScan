import os
import pickle
from pathlib import Path
import ctypes
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from feature_extraction import parse_manifest, parse_gradle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListItem, ListFlowable
from reportlab.lib.units import inch

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'zip'}

def load_model(model_path):
    with open(model_path, 'rb') as file:
        return pickle.load(file)

def find_file(directory, filename):
    for root, dirs, files in os.walk(directory):
        if filename in files:
            return os.path.join(root, filename)
    return None

def generate_report(manifest_features, gradle_features, prediction):
    report = []

    # Security Assessment
    report.append("### Security Assessment ###")
    if prediction == 1:
        report.append("Status: Secure")
        report.append("Your app's configuration follows security best practices.")
    else:
        report.append("Status: Insecure")
        report.append("Your app's configuration poses potential security risks. Consider the following changes:")

    # Permissions Analysis
    report.append("\n### Permissions Analysis ###")
    excessive_permissions = [p for p in manifest_features['permissions'] if p not in ["android.permission.INTERNET", "android.permission.ACCESS_FINE_LOCATION"]]
    
    if excessive_permissions:
        report.append(f"Your app requests the following permissions that may not be necessary: {', '.join(excessive_permissions)}.")
        report.append("Consider removing unnecessary permissions to minimize security risks.")
    else:
        report.append("Your app requests only necessary permissions.")

    # Components Analysis
    report.append("\n### Components Analysis ###")
    if manifest_features['components']['activities'] == 0:
        report.append("Warning: No activities are defined in your AndroidManifest.xml.")
    else:
        report.append(f"Your app defines {manifest_features['components']['activities']} activity(ies).")

    if manifest_features['components']['services'] == 0:
        report.append("Warning: No services are defined in your AndroidManifest.xml.")
    else:
        report.append(f"Your app defines {manifest_features['components']['services']} service(s).")

    if manifest_features['components']['receivers'] == 0:
        report.append("Warning: No receivers are defined in your AndroidManifest.xml.")
    else:
        report.append(f"Your app defines {manifest_features['components']['receivers']} receiver(s).")

    if manifest_features['components']['providers'] == 0:
        report.append("Warning: No providers are defined in your AndroidManifest.xml.")
    else:
        report.append(f"Your app defines {manifest_features['components']['providers']} provider(s).")

    # SDK Version Compatibility
    report.append("\n### SDK Version Compatibility ###")
    min_sdk_version = int(manifest_features['min_sdk'])  # Convert to int before comparison
    report.append(f"Minimum SDK Version: {min_sdk_version}")
    if min_sdk_version < 21:
        report.append("Recommendation: Consider increasing the minimum SDK version to at least 21 for better compatibility with modern Android devices.")

    # Dependency Management (Gradle)
    report.append("\n### Dependency Management ###")
    outdated_dependencies = []  # Example, you'd populate this with actual outdated libraries
    if outdated_dependencies:
        report.append("The following dependencies are outdated:")
        for dep in outdated_dependencies:
            report.append(f" - {dep}")
        report.append("Consider updating these dependencies to their latest versions.")
    else:
        report.append("All dependencies are up-to-date.")

    # Summary
    report.append("\n### Summary ###")
    report.append("Based on the analysis, consider making the suggested changes to improve your app's security, performance, and compatibility.")

    return "\n".join(report)

def save_report_as_pdf(report, pdf_path):
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles for headings and normal text
    title_style = styles['Title']
    heading_style = ParagraphStyle(name="HeadingStyle", fontSize=14, leading=16, spaceAfter=12, textColor=colors.darkblue, fontName="Helvetica-Bold")
    normal_style = styles['BodyText']
    bullet_style = ParagraphStyle(name="BulletStyle", bulletIndent=20, leading=14)

    content = []

    # Title
    content.append(Paragraph("Configuration Analysis Report", title_style))
    content.append(Spacer(1, 0.2 * inch))

    # Splitting report into sections
    sections = report.split("\n### ")

    for section in sections:
        if section.strip() == "":
            continue
        
        # Extract heading and text
        lines = section.split("\n")
        heading = lines[0].strip("### ")
        content.append(Paragraph(heading, heading_style))

        for line in lines[1:]:
            if line.startswith("- "):
                # Handle bullet points
                content.append(ListFlowable([ListItem(Paragraph(line.strip("- "), bullet_style))]))
            else:
                # Handle regular paragraphs
                content.append(Paragraph(line, normal_style))
            content.append(Spacer(1, 0.1 * inch))

    pdf.build(content)

def get_downloads_folder():
    """Detect the user's Downloads folder."""
    if os.name == 'nt':  # Windows
        import ctypes.wintypes  # Explicitly import wintypes
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return str(Path(buf.value).parent / "Downloads")
    else:  # MacOS/Linux
        return os.path.join(os.path.expanduser('~'), 'Downloads')

def analyze_directory(directory):
    manifest_path = find_file(directory, 'AndroidManifest.xml')
    gradle_path = find_file(directory, 'build.gradle')

    if not manifest_path or not gradle_path:
        return 'Required files not found in the directory.'

    manifest_features = parse_manifest(manifest_path)
    gradle_features = parse_gradle(gradle_path)

    # Prepare input for model
    input_features = {
        'permission_count': len(manifest_features['permissions']),
        'activity_count': manifest_features['components']['activities'],
        'service_count': manifest_features['components']['services'],
        'receiver_count': manifest_features['components']['receivers'],
        'provider_count': manifest_features['components']['providers'],
        'min_sdk': int(manifest_features['min_sdk']),  # Ensure this is converted to int
    }

    feature_vector = [
        input_features['permission_count'],
        input_features['activity_count'],
        input_features['service_count'],
        input_features['receiver_count'],
        input_features['provider_count'],
        input_features['min_sdk']
    ]

    # Load model and make prediction
    model = load_model('security_model.pkl')
    prediction = model.predict([feature_vector])

    # Generate detailed report
    report = generate_report(manifest_features, gradle_features, prediction[0])

    # Save report as PDF in the Downloads folder
    downloads_folder = get_downloads_folder()
    pdf_path = os.path.join(downloads_folder, "Configuration_Analysis_Report.pdf")
    save_report_as_pdf(report, pdf_path)

    return pdf_path

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Extract the uploaded project
            import zipfile
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(app.config['UPLOAD_FOLDER'])

            # Analyze the project
            pdf_path = analyze_directory(app.config['UPLOAD_FOLDER'])

            # Serve the report for download
            return send_from_directory(directory=str(Path(get_downloads_folder())), path="Configuration_Analysis_Report.pdf")

    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Upload your project</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .container {
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                max-width: 500px;
                width: 100%;
                text-align: center;
            }

            h1 {
                margin-bottom: 20px;
                font-size: 24px;
                color: #4CAF50;
            }

            input[type="file"] {
                display: block;
                margin: 20px auto;
            }

            input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }

            input[type="submit"]:hover {
                background-color: #45a049;
            }

            footer {
                margin-top: 20px;
                font-size: 14px;
                color: #777;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Upload your project (ZIP file)</h1>
            <form action="" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <input type="submit" value="Upload">
            </form>
        </div>
    </body>
    </html>
    '''


if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
