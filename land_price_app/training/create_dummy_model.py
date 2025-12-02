"""
Create a tiny dummy dataset and a simple model if the real artifacts are missing.

This helps a deployed demo work when the trained model and data are not present.
The dummy model is intentionally simple and only for demo/testing — it is
not intended to be used as a real, production ML model.
"""
import os
import pickle
import pandas as pd


def create_dummy_dataset(target_path):
    """Create a small Excel dataset containing a Village column so the form can load it."""
    df = pd.DataFrame({
        'Village': ['Village A', 'Village B', 'Village C', 'Village D'],
        'Area_sqft': [1000, 1500, 1200, 2000],
        'Distance_to_City_km': [5.0, 10.2, 3.5, 20.0],
        'Road_Access': ['City Road', 'Highway', 'Rural Road', 'City Road'],
        'Water_Source': ['Well', 'Borewell', 'River', 'None'],
        'Land_Use': ['Residential', 'Agricultural', 'Commercial', 'Residential'],
        'Soil_Type': ['Loamy', 'Sandy', 'Clay', 'Rocky'],
        'Nearby_Development': ['High', 'Medium', 'Low', 'High'],
        'Electricity_Available': [True, True, False, True],
        'Price_per_sqft': [50, 30, 40, 60],
    })
    df.to_excel(target_path, index=False)


class DummyModel:
    """A tiny model with a predict(df) method that accepts a DataFrame and returns a numeric price.

    The model uses a simple deterministic formula using Area and Distance and small contributions
    from other columns so predictions behave consistently in the demo.
    """
    def predict(self, df):
        prices = []
        for _, row in df.iterrows():
            area = float(row.get('Area_sqft', 0) or 0)
            distance = float(row.get('Distance_to_City_km', 0) or 0)
            electricity = row.get('Electricity_Available', False)
            # small heuristic: base price per sqft depends on area & distance
            price = 20 + (area * 0.02) - (distance * 0.3)
            if electricity:
                price += 3
            # small category signal (length of village string)
            village = str(row.get('Village', '') or '')
            price += min(len(village), 20) * 0.1
            prices.append(float(price))
        return pd.np.array(prices) if hasattr(pd, 'np') else __import__('numpy').array(prices)


def create_dummy_model_artifacts(base_dir=None):
    """Create ml_model.pkl and feature_info.pkl and a small dataset if missing.

    Returns tuple (model_path, feature_path, dataset_path)
    """
    if base_dir is None:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    training_dir = os.path.join(base_dir, 'training')
    os.makedirs(training_dir, exist_ok=True)

    # dataset path: write the demo dataset to both the app folder and the
    # project root so callers that look in either location (forms.py, training)
    # will find a usable file on a fresh deployment.
    app_level_dataset_path = os.path.join(os.path.dirname(training_dir), '0a73f94e-90e3-4ebd-9d94-15dc8066ad52.xlsx')
    # project root is one level above the app (this matches train_model/forms path)
    project_root = os.path.abspath(os.path.join(os.path.dirname(training_dir), '..'))
    project_level_dataset_path = os.path.join(project_root, '0a73f94e-90e3-4ebd-9d94-15dc8066ad52.xlsx')

    # model and feature info
    model_path = os.path.join(training_dir, 'ml_model.pkl')
    feature_path = os.path.join(training_dir, 'feature_info.pkl')

    # Create dataset if missing in EITHER location (try both, ignore write errors)
    try:
        if not os.path.exists(app_level_dataset_path):
            create_dummy_dataset(app_level_dataset_path)
    except Exception:
        # ignore write failures in constrained environments
        pass

    try:
        if not os.path.exists(project_level_dataset_path):
            create_dummy_dataset(project_level_dataset_path)
    except Exception:
        # ignore write failures in constrained environments
        pass

    # Create and save a simple DummyModel and feature_info
    model = DummyModel()
    feature_info = {
        'numeric_features': ['Area_sqft', 'Distance_to_City_km'],
        'categorical_features': ['Village', 'Road_Access', 'Water_Source', 'Land_Use', 'Soil_Type', 'Nearby_Development'],
        'binary_features': ['Electricity_Available'],
        'feature_order': ['Area_sqft', 'Distance_to_City_km', 'Village', 'Road_Access', 'Water_Source', 'Land_Use', 'Soil_Type', 'Nearby_Development', 'Electricity_Available']
    }

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    with open(feature_path, 'wb') as f:
        pickle.dump(feature_info, f)

    # Prefer project-level dataset path in return value, but also expose app-level
    # path so callers can decide where to look first.
    return model_path, feature_path, project_level_dataset_path, app_level_dataset_path


if __name__ == '__main__':
    p = create_dummy_model_artifacts()
    print('Created dummy model artifacts:', p)
