# LLM Model Configuration
CLAUDE_MODEL = "claude-haiku-4-5-20251001" 
CLAUDE_MAX_TOKENS = 4096
CLAUDE_TEMPERATURE = 0.0

# Embedding Model Configuration
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBEDDING_DIMENSION = 384
EMBEDDING_DEVICE = "cpu"

# Claim Extraction Model
SPACY_MODEL = "en_core_web_sm"

# Similarity and Verification Thresholds
SIMILARITY_THRESHOLD = 0.65
VERIFICATION_CONFIDENCE_THRESHOLD = 0.6
TOP_K_RETRIEVAL = 5
TOP_K_RERANK = 3

# ChromaDB Configuration
CHROMA_DB_PATH = "./data/chroma_db"
COLLECTION_NAME = "verified_facts"

# Data Configuration
VERIFIED_FACTS_CSV = "./data/verified_facts.csv"

# Streamlit Configuration
STREAMLIT_TITLE = "🔍 LLM Fact Checker"
STREAMLIT_DESCRIPTION = """
Verify claims against a database of verified facts using:
- **Semantic Search**: BAAI/bge-small-en-v1.5 embeddings
- **Vector Database**: ChromaDB for fast retrieval
- **LLM Verification**: Claude Haiku 4.5 for reasoning
"""

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/fact_checker.log"

# Verdict Configuration
VERDICTS = {
    "TRUE": "✅ True",
    "FALSE": "❌ False",
    "UNVERIFIABLE": "🤷♂️ Unverifiable"
}