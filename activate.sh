#!/bin/bash
# Helper script to create and activate virtual environment
# Usage: source activate.sh

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

# Check for Python 3.13+ compatibility issues
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 13 ]; then
    echo ""
    echo "⚠️  WARNING: Python $PYTHON_VERSION detected."
    echo "   PyTorch (required for embeddings) doesn't support Python 3.13+ yet."
    echo "   Recommended: Use Python 3.11 or 3.12 instead."
    echo ""
    echo "   To create venv with Python 3.11/3.12:"
    echo "   - python3.11 -m venv .venv  (or python3.12)"
    echo "   - rm -rf .venv  (to remove current venv first)"
    echo ""
    echo "   Continue anyway? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted. Please use Python 3.11 or 3.12."
        return 1
    fi
    echo ""
fi

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "Virtual environment created!"
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip --quiet

echo "Installing dependencies..."
INSTALL_LOG=$(mktemp)
if pip install -r requirements.txt > "$INSTALL_LOG" 2>&1; then
    echo "✅ Dependencies installed successfully"
    rm -f "$INSTALL_LOG"
else
    echo ""
    echo "⚠️  Some dependencies failed to install. Checking error log..."
    
    # Check if torch failed (common with Python 3.13+)
    if grep -qi "torch" "$INSTALL_LOG" || grep -qi "No matching distribution" "$INSTALL_LOG"; then
        echo ""
        echo "❌ PyTorch installation failed (Python $PYTHON_VERSION not supported yet)"
        echo ""
        echo "📋 Solution: Install packages individually..."
        
        # Install packages that don't require torch
        echo "   Installing core packages..."
        pip install streamlit python-dotenv anthropic chromadb pandas numpy beautifulsoup4 requests tqdm 2>/dev/null || true
        
        echo "   Installing spacy..."
        pip install spacy 2>/dev/null || echo "   ⚠️  spacy failed"
        
        echo "   Attempting transformers (may fail without torch)..."
        pip install transformers 2>/dev/null || echo "   ⚠️  transformers requires torch"
        
        echo "   Attempting sentence-transformers (may fail without torch)..."
        pip install sentence-transformers 2>/dev/null || echo "   ⚠️  sentence-transformers requires torch"
        
        echo ""
        echo "🔧 RECOMMENDED FIX:"
        echo "   1. Remove current venv: rm -rf .venv"
        echo "   2. Create new venv with Python 3.11 or 3.12:"
        echo "      python3.11 -m venv .venv"
        echo "      # or"
        echo "      python3.12 -m venv .venv"
        echo "   3. Activate and install: source .venv/bin/activate && pip install -r requirements.txt"
        echo ""
    else
        echo "   Installation errors detected. Full log saved."
        cat "$INSTALL_LOG"
    fi
    rm -f "$INSTALL_LOG"
fi

echo "Downloading spaCy model..."
if python -m spacy download en_core_web_sm --quiet 2>/dev/null; then
    echo "✅ spaCy model downloaded"
else
    echo "⚠️  Failed to download spaCy model. You can try manually: python -m spacy download en_core_web_sm"
fi

echo ""
echo "✅ Setup complete! Virtual environment is now active."
echo "   You should see (.venv) in your terminal prompt."
echo ""
if [ "$PYTHON_MAJOR" -gt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -gt 12 ]); then
    echo "⚠️  Note: You're using Python $PYTHON_VERSION."
    echo "   If you encounter issues with ML packages, consider creating a new venv with Python 3.11 or 3.12:"
    echo "   python3.11 -m venv .venv  # or python3.12 -m venv .venv"
    echo ""
fi
echo "Next steps:"
echo "  1. Copy env.template to .env: cp env.template .env"
echo "  2. Edit .env and add your ANTHROPIC_API_KEY"
echo "  3. Prepare data: cp data/verified_facts.csv.example data/verified_facts.csv"
echo "  4. Ingest data: python scripts/ingest_data.py"
echo "  5. Run app: streamlit run app.py"
echo ""

