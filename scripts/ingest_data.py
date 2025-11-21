import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from tqdm import tqdm

from config import VERIFIED_FACTS_CSV
from models.embedder import Embedder
from services.store_manager import StoreManager
from utils.logger import logger


def ingest_csv_to_database(csv_path: str = None, batch_size: int = 50):
    csv_path = csv_path or VERIFIED_FACTS_CSV
    
    # Check if CSV file exists
    if not Path(csv_path).exists():
        logger.error(f"CSV file not found: {csv_path}")
        logger.info(f"Please create {csv_path} with columns: fact, source, date, context")
        return
    
    logger.info(f"Reading facts from {csv_path}")
    try:
        df = pd.read_csv(csv_path, on_bad_lines='skip')
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        try:
            logger.info("Trying alternative CSV reading method with python engine...")
            df = pd.read_csv(
                csv_path, 
                engine='python',
                on_bad_lines='skip',
                sep=',',
                quotechar='"',
                skipinitialspace=True
            )
        except Exception as e2:
            logger.error(f"Alternative method also failed: {str(e2)}")
            logger.info("Please check your CSV file format. Each row should have exactly 4 columns: fact,source,date,context")
            logger.info("If facts contain commas, they should be enclosed in quotes.")
            return
    
    required_columns = ['fact']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns: {missing_columns}")
        return
    
    logger.info("Initializing embedder and store manager...")
    embedder = Embedder()
    store_manager = StoreManager()
    
    existing_count = store_manager.count()
    logger.info(f"Existing facts in database: {existing_count}")
    
    facts = df.to_dict('records')
    logger.info(f"Processing {len(facts)} facts...")
    
    total_added = 0
    for i in tqdm(range(0, len(facts), batch_size), desc="Processing batches"):
        batch = facts[i:i+batch_size]
        
        fact_texts = [fact.get('fact', str(fact)) for fact in batch]
        
        try:
            embeddings = embedder.embed_documents(fact_texts)
        except Exception as e:
            logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
            continue
        
        metadatas = []
        for fact in batch:
            metadata = {
                "source": fact.get('source', 'unknown'),
                "date": str(fact.get('date', '')),
                "context": str(fact.get('context', ''))
            }
            metadatas.append(metadata)
        
        try:
            store_manager.add_facts(batch, embeddings, metadatas)
            total_added += len(batch)
            logger.debug(f"Added batch {i//batch_size + 1}, total added: {total_added}")
        except Exception as e:
            logger.error(f"Error adding batch {i//batch_size + 1} to database: {str(e)}")
            continue
    
    final_count = store_manager.count()
    logger.info(f"Ingestion complete. Total facts in database: {final_count}")
    logger.info(f"Added {total_added} new facts")


def main():
    logger.info("Starting data ingestion")
    
    ingest_csv_to_database()
    
    logger.info("Data ingestion complete")


if __name__ == "__main__":
    main()

