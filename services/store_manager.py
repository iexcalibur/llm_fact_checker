from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from config import CHROMA_DB_PATH, COLLECTION_NAME, EMBEDDING_MODEL, EMBEDDING_DIMENSION
from utils.logger import logger


class StoreManager:
    
    def __init__(self, collection_name: str = None, persist_directory: str = None):
        self.collection_name = collection_name or COLLECTION_NAME
        self.persist_directory = persist_directory or CHROMA_DB_PATH
        self.expected_dimension = EMBEDDING_DIMENSION
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            # Check if dimension matches
            try:
                # Try to get a sample to check dimension
                sample = self.collection.peek(limit=1)
                if sample.get('embeddings') and len(sample['embeddings']) > 0:
                    existing_dim = len(sample['embeddings'][0])
                    if existing_dim != self.expected_dimension:
                        logger.warning(f"Collection has dimension {existing_dim} but expected {self.expected_dimension}")
                        logger.info(f"Deleting old collection to recreate with correct dimension")
                        self.client.delete_collection(name=self.collection_name)
                        self.collection = self.client.create_collection(
                            name=self.collection_name,
                            metadata={"description": "Verified facts database", "embedding_dimension": self.expected_dimension}
                        )
                        logger.info(f"Created new collection: {self.collection_name} with dimension {self.expected_dimension}")
                    else:
                        logger.info(f"Loaded existing collection: {self.collection_name}")
            except Exception as e:
                logger.warning(f"Could not verify collection dimension: {str(e)}")
                logger.info(f"Using existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Verified facts database", "embedding_dimension": self.expected_dimension}
            )
            logger.info(f"Created new collection: {self.collection_name} with dimension {self.expected_dimension}")
    
    def add_facts(self, facts: List[Dict], embeddings: List[List[float]], metadatas: List[Dict] = None):
        if not facts or not embeddings:
            logger.warning("No facts or embeddings provided")
            return
        
        if len(facts) != len(embeddings):
            raise ValueError("Number of facts must match number of embeddings")
        
        documents = [fact.get('fact', fact.get('text', str(fact))) for fact in facts]
        import time
        base_id = int(time.time() * 1000)
        ids = [f"fact_{base_id}_{i}" for i in range(len(documents))]
        
        if metadatas is None:
            metadatas = [
                {
                    "source": fact.get('source', 'unknown'),
                    "date": fact.get('date', ''),
                    "context": fact.get('context', '')
                }
                for fact in facts
            ]
        
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(facts)} facts to collection")
        
        except Exception as e:
            logger.error(f"Error adding facts to database: {str(e)}")
            raise
    
    def search(self, query_embedding: List[float], n_results: int = 5, where: Dict = None) -> Dict:
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
            logger.debug(f"Search returned {len(results.get('documents', [{}])[0])} results")
            return results
        
        except Exception as e:
            logger.error(f"Error searching database: {str(e)}")
            return {
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]],
                'ids': [[]]
            }
    
    def get_all_facts(self) -> List[Dict]:
        try:
            results = self.collection.get()
            
            facts = []
            for i, doc in enumerate(results['documents']):
                facts.append({
                    'id': results['ids'][i],
                    'fact': doc,
                    'metadata': results['metadatas'][i] if results['metadatas'] else {}
                })
            
            logger.debug(f"Retrieved {len(facts)} facts from database")
            return facts
        
        except Exception as e:
            logger.error(f"Error retrieving all facts: {str(e)}")
            return []
    
    def delete_fact(self, fact_id: str):
        try:
            self.collection.delete(ids=[fact_id])
            logger.info(f"Deleted fact with ID: {fact_id}")
        except Exception as e:
            logger.error(f"Error deleting fact: {str(e)}")
            raise
    
    def update_fact(self, fact_id: str, fact: str, metadata: Dict = None):
        try:
            self.collection.delete(ids=[fact_id])
            logger.warning(f"Update for {fact_id} requires re-adding with new embedding")
        except Exception as e:
            logger.error(f"Error updating fact: {str(e)}")
            raise
    
    def count(self) -> int:
        try:
            count = self.collection.count()
            logger.debug(f"Collection contains {count} facts")
            return count
        except Exception as e:
            logger.error(f"Error counting facts: {str(e)}")
            return 0

