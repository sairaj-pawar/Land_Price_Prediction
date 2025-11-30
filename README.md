# Land Price Prediction (Django + scikit-learn)

This repository contains a Django web application that integrates a scikit-learn machine learning pipeline to predict land price per square foot.

Key, factual items (from repository source):
- Django project: `land_price_project`
- Main app: `land_price_app`
- Training script: `land_price_app/training/train_model.py` — trains a RandomForest regression pipeline and saves `ml_model.pkl` and `feature_info.pkl` in `land_price_app/training/`.
- ML helper for inference: `land_price_app/ml_helpers.py` — loads the saved pipeline and performs single-row predictions.
- Web integration: `land_price_app/views.py` uses `predict_price()` to compute and persist `LandPrediction` objects (model defined at `land_price_app/models.py`).
- Data file referenced by training script: `0a73f94e-90e3-4ebd-9d94-15dc8066ad52.xlsx` (present in repository).

How to run (local development)
1. Create and activate a Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
2. Install dependencies:
```powershell
pip install -r requirements.txt
```
3. Run migrations and start the server:
```powershell
python manage.py migrate
python manage.py runserver
```

Train the ML model (creates `ml_model.pkl` and `feature_info.pkl`):
```powershell
python land_price_app/training/train_model.py
```

NOTE / Best practices:
- Large or sensitive files (the Excel dataset and the model pickle) are present in this repo. If you want to keep the repository public, consider removing those files from version control and documenting the steps required to regenerate them (running the training script).
- The `.gitignore` in this project excludes `db.sqlite3`, `staticfiles/`, and common ML artifact files (e.g., `*.pkl`) to avoid committing generated or sensitive artifacts.

If you'd like, I can (choose one):
- remove large files from git history (helpful if you already committed them) using BFG or git filter-repo,
- or initialize a local git repo and make a first commit for you and/or push to your GitHub remote.
# Land Price Prediction System (Satara Dataset)

A Django web application that predicts land prices in Satara using machine learning. The system uses a Random Forest Regressor model trained on local land price data to provide accurate price predictions based on various features like location, area, and amenities.

## Features

- Real-time land price predictions
- User authentication system
- Interactive dashboard with analytics
- Clean and responsive Bootstrap 5 UI
- Chart visualizations
- Historical prediction tracking

## Tech Stack

- Python 3.10+
- Django 4.x
- scikit-learn
- pandas, numpy, matplotlib
- Bootstrap 5
- Chart.js
- SQLite database

## Setup Instructions

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Train the ML model:
   ```bash
   python land_price_app/training/train_model.py
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the application at: http://127.0.0.1:8000/

## Project Structure

```
land_price_project/
├── manage.py
├── requirements.txt
├── README.md
├── land_price_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── land_price_app/
│   ├── migrations/
│   ├── static/land_price_app/
│   ├── templates/land_price_app/
│   ├── models.py
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   ├── ml_helpers.py
│   └── training/train_model.py
└── db.sqlite3
```

## Usage

1. Create an account or log in
2. Fill in the land details form
3. Get instant price predictions
4. View historical predictions in the dashboard
5. Analyze trends through charts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.