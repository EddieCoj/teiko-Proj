setup:
    pip install -r requirements.txt

pipeline:
    python load_data.py
    python -c "from your_analysis_module import run_all; run_all()"

dashboard:
    python dashboard/app.py