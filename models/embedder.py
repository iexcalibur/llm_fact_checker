from typing import List, Union
import torch
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, EMBEDDING_DEVICE
from utils.logger import logger


class Embedder:
    
    def __init__(self, model_name: str = None, device: str = None):
        self.model_name = model_name or EMBEDDING_MODEL
        self.device = device or EMBEDDING_DEVICE
        
        logger.info(f"Loading embedding model: {self.model_name} on {self.device}")
        
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def embed(self, text: Union[str, List[str]], normalize: bool = True) -> Union[List[float], List[List[float]]]:
        try:
            if isinstance(text, str):
                text = [text]
            
            embeddings = self.model.encode(
                text,
                normalize_embeddings=normalize,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            # Convert to list format
            if len(embeddings) == 1:
                return embeddings[0].tolist()
            else:
                return embeddings.tolist()
        
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def embed_query(self, query: str) -> List[float]:
        return self.embed(query, normalize=True)
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        return self.embed(documents, normalize=True)

