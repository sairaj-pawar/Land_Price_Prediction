import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

# Define column types
NUMERIC_FEATURES = ['Area_sqft', 'Distance_to_City_km']
CATEGORICAL_FEATURES = ['Village', 'Road_Access', 'Water_Source', 'Land_Use', 'Soil_Type', 'Nearby_Development']
BINARY_FEATURES = ['Electricity_Available']
TARGET = 'Price_per_sqft'

def load_data():
    """Load and prepare the dataset."""
    # Path to the dataset
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               '0a73f94e-90e3-4ebd-9d94-15dc8066ad52.xlsx')
    
    # Read the dataset
    df = pd.read_excel(dataset_path)
    
    # Handle missing values in Water_Source column
    if 'Water_Source' in df.columns:
        missing_count = df['Water_Source'].isna().sum()
        if missing_count > 0:
            print(f"Filling {missing_count} missing Water_Source values with 'None'...")
            df['Water_Source'] = df['Water_Source'].fillna('None')
    
    return df

def create_preprocessor():
    """Create a preprocessing pipeline for numeric and categorical features."""
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    
    # Create column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, NUMERIC_FEATURES),
            ('cat', categorical_transformer, CATEGORICAL_FEATURES),
            ('bin', 'passthrough', BINARY_FEATURES)
        ])
    
    return preprocessor

def train_model():
    """Train the Random Forest model and save it along with the preprocessor."""
    print("Loading data...")
    df = load_data()
    
    # Prepare feature matrix X and target vector y
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES]
    y = df[TARGET]
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create preprocessing pipeline
    print("Creating preprocessing pipeline...")
    preprocessor = create_preprocessor()
    
    # Create and train the model pipeline
    print("Training model...")
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    model.fit(X_train, y_train)
    
    # Evaluate the model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"Model Performance:")
    print(f"Training R² Score: {train_score:.4f}")
    print(f"Testing R² Score: {test_score:.4f}")
    
    # Save the model
    print("Saving model...")
    model_path = os.path.join(os.path.dirname(__file__), 'ml_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model saved successfully at: {model_path}")
    
    # Save feature lists for reference
    feature_info = {
        'numeric_features': NUMERIC_FEATURES,
        'categorical_features': CATEGORICAL_FEATURES,
        'binary_features': BINARY_FEATURES,
        'feature_order': NUMERIC_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES
    }
    
    feature_path = os.path.join(os.path.dirname(__file__), 'feature_info.pkl')
    with open(feature_path, 'wb') as f:
        pickle.dump(feature_info, f)
    
    print(f"Feature information saved at: {feature_path}")

if __name__ == '__main__':
    train_model()