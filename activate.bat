@echo off
REM Helper script to create and activate virtual environment on Windows
REM Usage: activate.bat

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo Virtual environment created!
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Downloading spaCy model...
python -m spacy download en_core_web_sm

echo.
echo Setup complete! Virtual environment is now active.
echo You should see (.venv) in your terminal prompt.
echo.
echo Next steps:
echo   1. Copy env.template to .env: copy env.template .env
echo   2. Edit .env and add your ANTHROPIC_API_KEY
echo   3. Prepare data: copy data\verified_facts.csv.example data\verified_facts.csv
echo   4. Ingest data: python scripts\ingest_data.py
echo   5. Run app: streamlit run app.py
echo.

