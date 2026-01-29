from flask import Flask, render_template, request, jsonify
import sys
import os

# Google Sheets Imports
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

app = Flask(__name__)

# --- Configuration ---
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1zDZoQEhg-3xIRW-Gemmm-R0lOiQ6Iiq_2ZMuQgZKJ3I/edit?gid=0#gid=0"
WORKSHEET_NAME = "RDB"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/submit', methods=['POST'])
def submit_result():
    data = request.json
    
    # Validation
    required_fields = ["Branch", "Name", "CRM", "Email", "MBTI", "Description"]
    if not all(field in data for field in required_fields):
        return jsonify({"success": False, "message": "Missing fields"}), 400

    if not GSPREAD_AVAILABLE:
        return jsonify({"success": False, "message": "Server Error: gspread library not found"}), 500

    try:
        # Locate Credentials
        print("--- Starting Sheet Save Process ---")
        json_path = os.path.join(app.root_path, 'service_account.json')
        print(f"Looking for credentials at: {json_path}")
        
        if not os.path.exists(json_path):
             print("ERROR: service_account.json file not found.")
             return jsonify({"success": False, "message": "Service Account Key not found on server. Please ensure 'service_account.json' is in the folder."}), 500

        # Authenticate
        print("Authenticating with Google...")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
        client = gspread.authorize(creds)
        
        print(f"Opening Spreadsheet URL: {SPREADSHEET_URL[:30]}...")
        sheet = client.open_by_url(SPREADSHEET_URL)
        print(f"Opening Worksheet: {WORKSHEET_NAME}")
        worksheet = sheet.worksheet(WORKSHEET_NAME)
        
        # Prepare Row
        row = [
            data["Branch"],
            data["Name"],
            data["CRM"],
            data["Email"],
            data["MBTI"],
            data["Description"]
        ]
        
        print(f"Appending row: {row}")
        worksheet.append_row(row)
        print("SUCCESS: Row appended to Google Sheet.")
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"CRITICAL ERROR saving to sheet: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    # 'debug=False' is required for most cloud environments to prevent signal errors
    # Port 5000 is default, but cloud providers might ignore this or map it automatically
    app.run(debug=False, port=5000)
