import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
import numpy as np
import tensorflow as tf
import joblib

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Note: python-dotenv not installed. AI features will work but env vars won't load from .env file.")
    print("Install with: pip install python-dotenv")

# Import the custom company analyzer search engine
import search_engine

# Import ML scam detector and email alerts
from scam_detector_ml import get_ml_prediction
from email_alerts import subscribe_to_alerts, unsubscribe_from_alerts, send_company_alert, get_user_subscriptions

app = Flask(__name__)

# Data file paths
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
REVIEWS_FILE = os.path.join(DATA_DIR, "user_reviews.json")
REPORTS_FILE = os.path.join(DATA_DIR, "scam_reports.json")

# Ensure the data directory and JSON databases exist
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(REVIEWS_FILE):
    with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f)
if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

# Try loading the legacy diabetes model and scaler with error protection
model = None
scaler = None
try:
    model_path = os.path.join(os.path.dirname(__file__), "diabetes_model.keras")
    scaler_path = os.path.join(os.path.dirname(__file__), "scaler.joblib")
    
    if os.path.exists(model_path):
        model = tf.keras.models.load_model(model_path)
        print("Successfully loaded Diabetes Keras model.")
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        print("Successfully loaded Scaler joblib file.")
except Exception as e:
    print(f"Warning: Failed to load legacy diabetes prediction model/scaler: {e}")

# Helper functions to manage JSON databases
def get_company_reviews(company_name):
    cleaned = search_engine.clean_company_name(company_name).lower()
    try:
        with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
            all_reviews = json.load(f)
            return all_reviews.get(cleaned, [])
    except Exception as e:
        print(f"Error reading reviews file: {e}")
        return []

def add_company_review(company_name, author, rating, comment):
    cleaned = search_engine.clean_company_name(company_name).lower()
    if not author.strip():
        author = "Anonymous Student"
        
    new_review = {
        'author': author,
        'rating': int(rating),
        'comment': comment,
        'date': datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    
    try:
        with open(REVIEWS_FILE, 'r+', encoding='utf-8') as f:
            all_reviews = json.load(f)
            if cleaned not in all_reviews:
                all_reviews[cleaned] = []
            all_reviews[cleaned].insert(0, new_review) # Add to the beginning
            f.seek(0)
            json.dump(all_reviews, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"Error writing review: {e}")

def get_all_scam_reports():
    try:
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading reports file: {e}")
        return []

def add_scam_report(student_name, company_name, scam_type, details):
    if not student_name.strip():
        student_name = "Anonymous Student"
        
    report = {
        'student_name': student_name,
        'company_name': search_engine.clean_company_name(company_name),
        'scam_type': scam_type,
        'complaint_details': details,
        'date': datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    
    try:
        with open(REPORTS_FILE, 'r+', encoding='utf-8') as f:
            reports = json.load(f)
            reports.insert(0, report) # New reports at the top
            f.seek(0)
            json.dump(reports, f, indent=4)
            f.truncate()
    except Exception as e:
        print(f"Error adding scam report: {e}")


# ================= ROUTES =================

# 1. Homepage - Internship Scam Radar Home
@app.route("/")
def home():
    return render_template("index.html")

# 2. Company Analysis Audit Dashboard
@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    company_name = ""
    if request.method == "POST":
        company_name = request.form.get("company_name", "")
    else:
        company_name = request.args.get("company_name", "")
        
    if not company_name:
        return redirect(url_for("home"))
        
    # Analyze company via search engine
    company_data = search_engine.analyze_company(company_name)
    
    # Load user reviews for this company
    reviews = get_company_reviews(company_name)
    
    # Update score if reviews indicate negative feedback
    if reviews:
        negative_reviews = [r for r in reviews if r['rating'] <= 2]
        if negative_reviews:
            company_data['scam_score'] = min(100, company_data['scam_score'] + len(negative_reviews) * 8)
            company_data['risk_breakdown']['review_sentiment'] = min(100, company_data['risk_breakdown']['review_sentiment'] + len(negative_reviews) * 15)
            
            warning_msg = f"Alert: {len(negative_reviews)} student complaints filed on ScamShield for this company."
            if warning_msg not in company_data['scam_details']:
                company_data['scam_details'].insert(0, warning_msg)
    
    # Get ML-based scam prediction
    ml_prediction = get_ml_prediction(company_data)
    if ml_prediction:
        company_data['ml_score'] = ml_prediction.get('ml_score', company_data['scam_score'])
        company_data['ml_confidence'] = ml_prediction.get('confidence', 0)
        company_data['model_used'] = ml_prediction.get('model_used', 'Template-based')
        
        # Blend heuristic and ML scores (70% heuristic, 30% ML)
        company_data['scam_score'] = int(0.7 * company_data['scam_score'] + 0.3 * ml_prediction.get('ml_score', 0))
    
    return render_template("dashboard.html", company=company_data, reviews=reviews)

# 3. Add Student Review
@app.route("/add_review", methods=["POST"])
def add_review():
    company_name = request.form.get("company_name", "")
    author = request.form.get("author", "Anonymous")
    rating = request.form.get("rating", "5")
    comment = request.form.get("comment", "")
    
    if company_name and comment:
        add_company_review(company_name, author, rating, comment)
        
    return redirect(url_for("analyze", company_name=company_name))

# 4. Public Reports List Page
@app.route("/reports_list")
def reports_list():
    reports = get_all_scam_reports()
    return render_template("reports_list.html", reports=reports)


# ================= EMAIL ALERTS ROUTES =================

# 6. Subscribe to Email Alerts
@app.route("/subscribe_alerts", methods=["POST"])
def subscribe_alerts():
    try:
        email = request.form.get("email", "").strip()
        companies = request.form.getlist("companies")
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'message': 'Invalid email address'}), 400
        
        if not companies:
            # If no companies specified, add current company from referrer
            company_name = request.form.get("company_name", "")
            if company_name:
                companies = [company_name]
        
        result = subscribe_to_alerts(email, companies)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 7. Unsubscribe from Email Alerts
@app.route("/unsubscribe_alerts", methods=["POST", "GET"])
def unsubscribe_alerts():
    try:
        email = request.args.get("email") or request.form.get("email", "")
        
        if not email:
            return redirect(url_for("home"))
        
        result = unsubscribe_from_alerts(email)
        
        if request.method == "GET":
            return f"<html><body><h2>{result['message']}</h2><p><a href='/'>Back to Home</a></p></body></html>"
        else:
            return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 8. Get User's Email Subscriptions
@app.route("/get_subscriptions", methods=["POST"])
def get_subscriptions():
    try:
        email = request.form.get("email", "").strip()
        
        if not email:
            return jsonify({'success': False, 'subscriptions': []}), 400
        
        subscriptions = get_user_subscriptions(email)
        return jsonify({
            'success': True,
            'email': email,
            'subscriptions': subscriptions
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# 9. ML Scam Score API
@app.route("/api/ml_score", methods=["POST"])
def ml_score_api():
    try:
        company_data = request.get_json()
        
        if not company_data:
            return jsonify({'error': 'No company data provided'}), 400
        
        ml_result = get_ml_prediction(company_data)
        
        return jsonify({
            'success': True,
            'ml_score': ml_result.get('ml_score'),
            'confidence': ml_result.get('confidence'),
            'is_scam_likely': ml_result.get('is_scam_likely'),
            'model': ml_result.get('model_used')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 10. Report Scam (with ML feedback)
@app.route("/report", methods=["POST"])
def report():
    student_name = request.form.get("student_name", "Anonymous")
    company_name = request.form.get("company_name", "")
    scam_type = request.form.get("scam_type", "Other")
    complaint_details = request.form.get("complaint_details", "")
    
    if company_name and complaint_details:
        add_scam_report(student_name, company_name, scam_type, complaint_details)
        
        # Trigger email alerts to subscribers
        details = [f"New complaint: {scam_type}", complaint_details[:100]]
        send_company_alert(company_name, 0, 0, details)
        
    return redirect(url_for("reports_list"))


# ================= LEGACY ROUTES =================

# 11. Public Reports List Page (moved from position 5)
@app.route("/reports_list_old")
def reports_list_old():
    reports = get_all_scam_reports()
    return render_template("reports_list.html", reports=reports)

# 6. Legacy Diabetes Form page
@app.route("/diabetes")
def diabetes():
    return render_template("diabetes.html", prediction=None)

# 7. Legacy Diabetes Predict Action
@app.route("/predict", methods=["POST"])
def predict():
    if model is None or scaler is None:
        prediction = "Error: Diabetes ML model files are not loaded on server."
        return render_template("diabetes.html", prediction=prediction)
        
    try:
        input_features = [
            float(request.form.get("female", 0)),
            float(request.form.get("male", 0)),
            float(request.form.get("other", 0)),
            float(request.form.get("age", 0)),
            float(request.form.get("race_AfricanAmerican", 0)),
            float(request.form.get("race_Asian", 0)),
            float(request.form.get("race_Caucasian", 0)),
            float(request.form.get("race_Hispanic", 0)),
            float(request.form.get("race_Other", 0)),
            float(request.form.get("hypertension", 0)),
            float(request.form.get("heart_disease", 0)),
            float(request.form.get("no_info", 0)),
            float(request.form.get("current", 0)),
            float(request.form.get("ever", 0)),
            float(request.form.get("former", 0)),
            float(request.form.get("never", 0)),
            float(request.form.get("not_current", 0)),
            float(request.form.get("bmi", 0)),
            float(request.form.get("hbA1c_level", 0)),
            float(request.form.get("blood_glucose_level", 0))
        ]
        
        input_data = np.array([input_features])
        input_scaled = scaler.transform(input_data)
        result = model.predict(input_scaled)
        prediction = "Diabetes Hai (Positive)" if result[0][0] > 0.5 else "Diabetes nahi hai (Negative)"
    except Exception as e:
        prediction = f"Error during model prediction: {e}"
        
    return render_template("diabetes.html", prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)