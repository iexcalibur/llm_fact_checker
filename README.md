# 🚀 LLM Fact Checker

<img width="1512" height="982" alt="Screenshot 2025-11-22 at 3 14 55 AM" src="https://github.com/user-attachments/assets/060e7a2c-74ad-48ec-a944-50f4bdca6a1c" />
<img width="1512" height="982" alt="Screenshot 2025-11-22 at 3 14 30 AM" src="https://github.com/user-attachments/assets/f7bff924-03a1-4e15-a91b-f75432468d65" />
<img width="1512" height="982" alt="Screenshot 2025-11-22 at 3 14 39 AM" src="https://github.com/user-attachments/assets/c5e3f5f9-8ac0-4927-847f-8d3663924221" />


## Prerequisites

- **Python 3.11 or 3.12** (Python 3.13+ not supported due to PyTorch compatibility)
- **pip** package manager
- **~2GB free disk space** (for models and dependencies)
- **Internet connection** (for downloads and API access)
- **Anthropic API key** ([Get one here](https://console.anthropic.com/))

---

## Step 1: Clone/Download the Project

```bash
# Navigate to project directory
cd llm-fact-checker
```

---

## Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3.11 -m venv .venv
# OR
python3.12 -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

**✅ Verify:** You should see `(.venv)` in your terminal prompt

**Note:** Always activate the virtual environment before running any commands.

---

## Step 3: Install Dependencies

### Option A: CPU-only Installation (Recommended for most users)

```bash
# Ensure virtual environment is activated
# Install PyTorch CPU version first (faster, smaller download)
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### Option B: GPU Installation (If you have NVIDIA GPU)

```bash
# Install all dependencies (includes CUDA-enabled PyTorch)
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

**Expected output:**
```
Successfully installed torch-2.1.2 sentence-transformers-2.3.1 ...
✓ Download and installation successful
You can now load the package via spacy.load('en_core_web_sm')
```

**⏱️ Time:** 5-8 minutes depending on internet speed

---

## Step 4: Configure API Key

### Create `.env` file:

**On macOS/Linux:**
```bash
touch .env
echo "ANTHROPIC_API_KEY=sk-ant-your-actual-key-here" >> .env
```

**On Windows:**
```bash
# Create .env file manually or use:
echo ANTHROPIC_API_KEY=sk-ant-your-actual-key-here > .env
```

**Or manually create** `.env` file in project root with:
```
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-api-key-here
```

**Get your API key:** https://console.anthropic.com/settings/keys

**✅ Verify:**
```bash
# Check file exists
ls -la .env  # macOS/Linux
dir .env     # Windows

# Should show: ANTHROPIC_API_KEY=sk-ant-...
cat .env     # macOS/Linux
type .env    # Windows
```

**🔒 Security Note:** Never commit `.env` to version control. It's already in `.gitignore`.

---

## Step 5: Prepare Facts Database

### Check if sample data exists:

**On macOS/Linux:**
```bash
ls data/verified_facts.csv
```

**On Windows:**
```bash
dir data\verified_facts.csv
```

### If file doesn't exist - Create sample data:

```bash
# Create data directory if needed
mkdir -p data  # macOS/Linux
mkdir data     # Windows

# Create sample CSV
cat > data/verified_facts.csv << 'EOF'
fact,source,date,context
"PM Kisan Samman Nidhi provides Rs 6000 per year to eligible farmers","Ministry of Agriculture",2024-02-10,"Direct benefit transfer scheme"
"India became the world's most populous country in 2023 with 142.86 crore population","United Nations",2023-04-24,"Official UN population estimates"
"No universal free electricity scheme announced for all farmers as of January 2025","Ministry of Power",2024-12-20,"State schemes may exist separately"
EOF
```

### Ingest facts into vector database:

```bash
python scripts/ingest_data.py
```

**Expected output:**
```
INFO - Reading facts from data/verified_facts.csv
INFO - Initializing embedder and store manager...
INFO - Processing X facts...
Processing batches: 100%|████████| 1/1 [00:02<00:00]
INFO - Ingestion complete. Total facts in database: X
```

**⏱️ Time:** 1-2 minutes

**⚠️ Note:** If you see dimension mismatch errors, delete `data/chroma_db/` folder and run ingestion again.

---

## Step 6: Verify Installation (Recommended)

Before launching the UI, verify everything works:

### Quick Health Check:

```bash
# 1. Check database populated
python -c "from services.store_manager import StoreManager; sm = StoreManager(); print(f'✅ Facts in DB: {sm.count()}')"

# 2. Check embedder loads
python -c "from models.embedder import Embedder; e = Embedder(); print('✅ Embedder loaded')"

# 3. Check claim extractor
python -c "from models.claim_extractor import ClaimExtractor; c = ClaimExtractor(); print('✅ Claim extractor loaded')"

# 4. Check API key
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('✅ API key loaded' if os.getenv('ANTHROPIC_API_KEY') else '❌ API key missing')"
```
---

## Step 7: Launch the Application

```bash
# Make sure virtual environment is activated (you should see .venv in prompt)
streamlit run app.py
```

**First launch:** May take 20-30 seconds as models load into memory

**Browser opens automatically at:** http://localhost:8501

**If browser doesn't open:** Manually navigate to the URL shown in terminal

---

## 🎯 First Run - What to Expect

### Loading Times:
- **App startup:** 20-30 seconds (models loading)
- **First query:** 3-5 seconds (additional initialization)
- **Subsequent queries:** 2-3 seconds (normal speed)

### Normal Behavior:
- ✅ "Loading..." message for 30 seconds on first start
- ✅ First query takes longer than expected
- ✅ Browser takes time to open

**This is all normal!** Subsequent queries will be faster.

---

## ✅ Using the Application

### 1. Single Claim Verification

**Navigate to:** "📝 Single Claim" tab

**Try the assignment example:**
```
The Indian government has announced free electricity to all farmers starting July 2025.
```

**Click:** "🔍 Verify Claim"

**Expected result:**
- **Verdict:** ❌ Likely False or Definitely False
- **Confidence:** 70-90%
- **Reasoning:** Clear explanation citing evidence
- **Evidence:** 2-3 relevant facts displayed

### 2. Text Analysis

**Navigate to:** "📄 Text Analysis" tab

**Paste multi-claim text:**
```
PM Kisan provides Rs 6,000 per year to farmers. 
The government announced free electricity for all.
India has the largest population in the world.
```

**Click:** "🔍 Analyze Text"

**System will:**
- Extract individual claims (usually 2-3)
- Verify each claim separately
- Show summary statistics (True/False/Unverifiable counts)

### 3. Database Information

**Navigate to:** "💾 Database Info" tab

**View:**
- Total number of facts in database
- Sample facts with sources
- Metadata (source, date, context)

---

## 📁 Project Structure

```
llm-fact-checker/
├── app.py                      # Main Streamlit UI
├── config.py                   # Global settings
├── requirements.txt            # Dependencies
├── .env                        # API keys (you create this)
│
├── data/
│   ├── verified_facts.csv     # Source facts (50 samples provided)
│   └── chroma_db/             # Vector DB (auto-generated)
│
├── models/                     # ML Components
│   ├── claim_extractor.py     # spaCy extraction
│   ├── embedder.py            # BGE embeddings
│   └── llm_client.py          # Claude API
│
├── services/                   # Business Logic
│   ├── pipeline.py            # Main orchestrator
│   ├── retriever.py           # Search & ranking
│   └── store_manager.py       # ChromaDB wrapper
│
├── scripts/                    # Utilities
│   ├── ingest_data.py         # Data ingestion
│   └── test_assignment_example.py  # Validation test
│
└── utils/                      # Helpers
    ├── logger.py              # Logging
    └── prompts.py             # LLM prompts
```

---


### Customizing Configuration

Edit `config.py` to change:
- **Embedding model** (default: `BAAI/bge-small-en-v1.5`)
- **Similarity threshold** (default: 0.65)
- **LLM model** (default: `claude-haiku-4-5-20251001`)
- **Top-K results** (default: 5)

### Performance Optimization

- **First query slow?** Normal - models caching
- **Want faster?** Reduce `TOP_K_RETRIEVAL` in config
- **Running locally?** CPU mode is sufficient
- **High volume?** Consider GPU for embeddings

### Cost Management

- **Average cost:** ~$0.001-0.01 per claim
- **Haiku 4.5:** Most cost-effective Claude model
- **Reduce costs:** Lower `TOP_K_RETRIEVAL` (fewer facts sent to LLM)

---

**Happy Fact-Checking! 🔍**
