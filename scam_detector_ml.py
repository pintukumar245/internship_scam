"""
ML-Based Scam Detection Model
Trains and predicts company scam probability using machine learning
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Model file paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "scam_detector_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scam_detector_scaler.pkl")
TRAINING_DATA_PATH = os.path.join(MODEL_DIR, "training_data.json")

class ScamDetectorML:
    """Machine Learning based scam detection system."""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.load_model()
    
    def load_model(self):
        """Load pre-trained model or create new one."""
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                print("[OK] ML Model loaded successfully")
            except Exception as e:
                print(f"[WARNING] Failed to load model: {e}. Creating new model...")
                self.create_default_model()
        else:
            print("[INFO] No pre-trained model found. Creating default model...")
            self.create_default_model()
    
    def create_default_model(self):
        """Create and train a new model with default training data."""
        # Generate synthetic training data based on known scam patterns
        training_data = self.generate_training_data()
        
        if training_data is not None:
            X, y = training_data
            self.train_model(X, y)
            self.save_model()
    
    def generate_training_data(self):
        """Generate or load training data from historical records."""
        try:
            # Try to load existing training data
            if os.path.exists(TRAINING_DATA_PATH):
                with open(TRAINING_DATA_PATH, 'r') as f:
                    data = json.load(f)
                    if data:
                        return self._prepare_features(data)
        except:
            pass
        
        # Generate synthetic training data with known scam patterns
        X = []
        y = []  # 1 = scam, 0 = legitimate
        
        # Scam companies characteristics (y=1)
        scam_patterns = [
            # [fee_demand, online_presence_low, negative_reviews, employee_size, stipend_low, cert_issues, complaints]
            [1, 1, 1, 0, 1, 1, 1],  # Classic scam
            [1, 0, 1, 0, 1, 1, 1],  # Scam with some presence
            [1, 1, 0, 0, 1, 0, 1],  # Fee-focused scam
            [0, 1, 1, 0, 0, 1, 1],  # Hidden scam
            [1, 0, 1, 1, 1, 1, 0],  # Medium-sized scam
            [0, 0, 1, 0, 1, 1, 1],  # Fake certificate scam
        ]
        
        # Legitimate companies characteristics (y=0)
        legit_patterns = [
            # [no_fee, good_presence, positive_reviews, large_size, fair_stipend, valid_cert, low_complaints]
            [0, 1, 1, 1, 1, 0, 0],  # Established company
            [0, 1, 0, 1, 1, 0, 0],  # Large company, ok reviews
            [0, 0, 1, 0, 1, 0, 0],  # Smaller but legit
            [0, 1, 1, 1, 0, 0, 1],  # Some issues but fundamentally safe
            [0, 0, 0, 0, 1, 0, 0],  # Startup but legitimate
            [0, 1, 1, 0, 1, 0, 0],  # Mid-size legitimate
        ]
        
        # Build training set
        for pattern in scam_patterns:
            X.append(pattern)
            y.append(1)
        
        for pattern in legit_patterns:
            X.append(pattern)
            y.append(0)
        
        # Add some variations
        X = np.array(X)
        y = np.array(y)
        
        # Add noise/variations
        X_varied = []
        y_varied = []
        for i in range(len(X)):
            for _ in range(3):  # Create 3 variations of each
                noise = np.random.normal(0, 0.1, len(X[i]))
                X_varied.append(np.clip(X[i] + noise, 0, 1))
                y_varied.append(y[i])
        
        return np.array(X_varied), np.array(y_varied)
    
    def train_model(self, X, y):
        """Train the ML model."""
        try:
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train ensemble model
            self.model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            self.model.fit(X_scaled, y)
            
            print(f"[OK] ML Model trained on {len(X)} samples")
            
            # Evaluate
            score = self.model.score(X_scaled, y)
            print(f"[OK] Model accuracy: {score:.2%}")
            
        except Exception as e:
            print(f"[ERROR] Model training failed: {e}")
    
    def save_model(self):
        """Save trained model to disk."""
        try:
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.scaler, SCALER_PATH)
            print(f"[OK] Model saved to {MODEL_PATH}")
        except Exception as e:
            print(f"[ERROR] Failed to save model: {e}")
    
    def extract_features(self, company_data):
        """Extract features from company data for ML prediction."""
        # Feature engineering
        features = []
        
        # Feature 1: Fee demand indicator (0-1)
        fee_demand = 1 if any(phrase in str(company_data.get('scam_details', '')).lower() 
                              for phrase in ['fee', 'charge', 'deposit', 'money']) else 0
        features.append(fee_demand)
        
        # Feature 2: Online presence (0-1, inverted)
        snippets_count = len(company_data.get('snippets', []))
        online_presence = 0 if snippets_count < 3 else 1
        features.append(1 - online_presence)  # Inverted: low presence = higher risk
        
        # Feature 3: Negative reviews/complaints (0-1)
        scam_details = str(company_data.get('scam_details', '')).lower()
        negative_indicators = sum([
            'complaint' in scam_details,
            'fraud' in scam_details,
            'scam' in scam_details,
            'fake' in scam_details,
            'cheat' in scam_details
        ]) / 5
        features.append(min(1, negative_indicators))
        
        # Feature 4: Employee size indicator (0-1)
        employee_size = str(company_data.get('employee_size', '')).lower()
        size_risky = 1 if '1-10' in employee_size or 'small' in employee_size else 0
        features.append(size_risky)
        
        # Feature 5: Stipend related issues (0-1)
        # Noted from snippets
        snippets_text = ' '.join([s.get('snippet', '') for s in company_data.get('snippets', [])])
        stipend_risky = 1 if any(word in snippets_text.lower() 
                                for word in ['unpaid', 'low salary', '1000', '1100', '1200']) else 0
        features.append(stipend_risky)
        
        # Feature 6: Certificate issues (0-1)
        cert_issues = 1 if 'certificate' in scam_details else 0
        features.append(cert_issues)
        
        # Feature 7: Number of complaints (normalized to 0-1)
        complaints_count = len(company_data.get('local_records', []))
        complaints_normalized = min(1, complaints_count / 10)
        features.append(complaints_normalized)
        
        return np.array(features).reshape(1, -1)
    
    def predict_scam_probability(self, company_data):
        """Predict scam probability using ML model."""
        if self.model is None or self.scaler is None:
            print("[WARNING] Model not loaded, returning baseline score")
            return None
        
        try:
            features = self.extract_features(company_data)
            features_scaled = self.scaler.transform(features)
            
            # Get probability
            probability = self.model.predict_proba(features_scaled)[0][1]  # Probability of scam
            
            # Convert to 0-100 scale
            ml_score = int(probability * 100)
            
            return {
                'ml_score': ml_score,
                'confidence': probability,
                'is_scam_likely': ml_score > 60,
                'model_used': 'GradientBoosting'
            }
        except Exception as e:
            print(f"[ERROR] Prediction error: {e}")
            return None
    
    def update_with_feedback(self, company_data, is_scam_confirmed):
        """Update model with real feedback from users."""
        try:
            # Load existing training data
            training_data = []
            if os.path.exists(TRAINING_DATA_PATH):
                with open(TRAINING_DATA_PATH, 'r') as f:
                    training_data = json.load(f)
            
            # Add new feedback
            features = self.extract_features(company_data)
            new_data = {
                'features': features[0].tolist(),
                'label': 1 if is_scam_confirmed else 0,
                'company': company_data.get('name'),
                'timestamp': pd.Timestamp.now().isoformat()
            }
            training_data.append(new_data)
            
            # Save updated data
            with open(TRAINING_DATA_PATH, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            print(f"[OK] Model updated with feedback for {company_data.get('name')}")
            
            # Periodically retrain (after every 10 feedbacks)
            if len(training_data) % 10 == 0:
                print("[INFO] Retraining model with accumulated feedback...")
                X = np.array([d['features'] for d in training_data])
                y = np.array([d['label'] for d in training_data])
                self.train_model(X, y)
                self.save_model()
        
        except Exception as e:
            print(f"[ERROR] Feedback update error: {e}")


# Global instance
ml_detector = ScamDetectorML()

def get_ml_prediction(company_data):
    """Get ML-based scam probability."""
    return ml_detector.predict_scam_probability(company_data)

def report_feedback(company_data, is_scam):
    """Report feedback to improve model."""
    ml_detector.update_with_feedback(company_data, is_scam)
