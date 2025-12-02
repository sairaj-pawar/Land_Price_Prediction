# Import necessary libraries
import os      # For file path operations
import pickle  # For loading saved ML model
import pandas as pd  # For data manipulation (DataFrame)

# This function loads the trained ML model and feature information from files
def load_model():
    """Load the trained model and feature information."""
    # Get the path to the model file (ml_model.pkl)
    # __file__ is current file location, dirname gets folder, join adds path
    model_path = os.path.join(os.path.dirname(__file__), 'training', 'ml_model.pkl')
    
    # Get the path to the feature info file (feature_info.pkl)
    feature_path = os.path.join(os.path.dirname(__file__), 'training', 'feature_info.pkl')
    
    # Check that the model and feature files exist and load them.
    # If missing, return (None, None) so callers can handle absence gracefully.
    if not os.path.exists(model_path) or not os.path.exists(feature_path):
        # Try to create demo artifacts automatically (useful for deployments where
        # the trained model wasn't committed). This creates a small dataset and
        # a minimal dummy model so the site can show predictions for demo/demoing.
        try:
            from .training import create_dummy_model as _cdm
            _cdm.create_dummy_model_artifacts(os.path.dirname(__file__))
        except Exception:
            # If creation failed, return None so caller can handle gracefully
            return None, None
        # After attempting to create, continue to load if they exist
        if not os.path.exists(model_path) or not os.path.exists(feature_path):
            return None, None

    # Open and load the model file
    # 'rb' means read binary (pickle files are binary)
    with open(model_path, 'rb') as f:
        model = pickle.load(f)  # Load the trained model

    # Open and load the feature info file
    with open(feature_path, 'rb') as f:
        feature_info = pickle.load(f)  # Load feature order and encoding info
    
    # Return both the model and feature info
    return model, feature_info

# This function prepares the input data in the correct format for the model
def prepare_features(data, feature_info):
    """Prepare features for prediction in the correct order."""
    features = []  # Empty list to store feature values
    
    # Loop through each feature in the order the model expects
    for feature in feature_info['feature_order']:
        # The model was trained with specific feature names (e.g., 'Area_sqft')
        # But forms use lowercase names (e.g., 'area_sqft')
        # So we try different variations to find the right one
        
        # First, try exact match
        if feature in data:
            val = data[feature]
        else:
            # Try with first letter lowercase (Area_sqft -> area_sqft)
            alt1 = feature[0].lower() + feature[1:]
            # Try all lowercase (Area_sqft -> area_sqft)
            alt2 = feature.lower()
            
            # Check if alternative names exist in data
            if alt1 in data:
                val = data[alt1]
            elif alt2 in data:
                val = data[alt2]
            else:
                # If feature not found, raise error with helpful message
                raise KeyError(f"Feature '{feature}' not found in input data keys: {list(data.keys())}")

        # Add the value to our features list
        features.append(val)

    # Return the list of features in correct order
    return features

# This is the main function that predicts land price
def predict_price(data):
    """Make a price prediction using the trained model."""
    # Step 1: Load the trained model and feature information
    model, feature_info = load_model()
    if model is None or feature_info is None:
        # Model or feature info not available on this installation
        # Raise a clear RuntimeError to be handled by caller (views)
        raise RuntimeError('ML model not available on server. Train/upload model to enable predictions.')
    
    # Step 2: Prepare the input data in the format model expects
    # Convert user input to list of values in correct order
    features = prepare_features(data, feature_info)
    
    # Step 3: Create a DataFrame (table) with one row
    # The model was trained on a DataFrame, so we need to give it a DataFrame
    # [features] creates a list with one row, columns=feature_order sets column names
    df = pd.DataFrame([features], columns=feature_info['feature_order'])

    # Step 4: Use the model to predict the price
    # model.predict() takes DataFrame and returns array of predictions
    # [0] gets the first (and only) prediction value
    predicted_price = model.predict(df)[0]
    
    # Step 5: Return the predicted price per square foot
    return predicted_price
