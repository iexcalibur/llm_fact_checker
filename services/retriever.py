from typing import List, Dict, Tuple
import numpy as np
import re

from config import SIMILARITY_THRESHOLD, TOP_K_RETRIEVAL, TOP_K_RERANK
from models.embedder import Embedder
from services.store_manager import StoreManager
from utils.logger import logger


class Retriever:
    def __init__(self, embedder: Embedder, store_manager: StoreManager):
        self.embedder = embedder
        self.store_manager = store_manager
        logger.info("Retriever initialized")
    
    def is_vague_claim(self, claim: str) -> bool:
        vague_terms = ["some", "many", "often", "recently", "usually", "generally", 
                       "might", "may", "could", "possibly", "sometimes", "often"]
        
        claim_lower = claim.lower()
        
        vague_count = sum(1 for term in vague_terms if term in claim_lower)
        
        if vague_count >= 2:
            return True
        
        has_date = bool(re.search(r'\d{4}|\d{1,2}[/-]\d{1,2}', claim))
        has_number = bool(re.search(r'\d+', claim))
        has_name = bool(re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', claim))
        
        if not (has_date or has_number or has_name) and vague_count >= 1:
            return True
        
        return False
    
    def search(self, query: str, top_k: int = None, threshold: float = None) -> List[Dict]:
        top_k = top_k or TOP_K_RETRIEVAL
        threshold = threshold or SIMILARITY_THRESHOLD
        
        try:
            query_embedding = self.embedder.embed_query(query)
            
            results = self.store_manager.search(query_embedding, n_results=top_k)
            
            facts = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    distance = results['distances'][0][i] if results['distances'] else 0.0
                    similarity = 1.0 - distance
                    
                    if i < 3:
                        logger.debug(f"Top result {i+1}: similarity={similarity:.3f}, text={doc[:80]}...")
                    
                    if similarity >= threshold:
                        fact = {
                            'text': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {},
                            'similarity': similarity,
                            'id': results['ids'][0][i] if results['ids'] and results['ids'][0] else None
                        }
                        facts.append(fact)
            
            if not facts and results['documents'] and results['documents'][0]:
                top_distance = results['distances'][0][0] if results['distances'] and results['distances'][0] else 1.0
                top_similarity = 1.0 - top_distance
                logger.warning(f"No facts above threshold {threshold}. Top similarity: {top_similarity:.3f}")
            
            logger.info(f"Retrieved {len(facts)} facts above threshold {threshold}")
            return facts
        
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def rerank(self, query: str, facts: List[Dict], top_k: int = None, llm_client = None) -> List[Dict]:
        top_k = top_k or TOP_K_RERANK
        
        if not facts:
            return []
        
        if llm_client:
            return self._rerank_with_llm(query, facts, top_k, llm_client)
        else:
            facts_sorted = sorted(facts, key=lambda x: x['similarity'], reverse=True)
            return facts_sorted[:top_k]
    
    def _rerank_with_llm(self, query: str, facts: List[Dict], top_k: int, llm_client) -> List[Dict]:
        from utils.prompts import RERANKING_PROMPT
        
        results_text = "\n".join([
            f"{i+1}. {fact['text']}\n   Source: {fact['metadata'].get('source', 'unknown')}"
            for i, fact in enumerate(facts)
        ])
        
        prompt = RERANKING_PROMPT.format(
            claim=query,
            results=results_text,
            count=len(facts)
        )
        
        try:
            response = llm_client.generate(prompt)
            ranked_indices = [int(x.strip()) - 1 for x in response.split(',')]
            
            reranked = [facts[i] for i in ranked_indices if 0 <= i < len(facts)]
            
            remaining = [fact for i, fact in enumerate(facts) if i not in ranked_indices]
            reranked.extend(remaining)
            
            return reranked[:top_k]
        
        except Exception as e:
            logger.error(f"Error in LLM re-ranking: {str(e)}")
            facts_sorted = sorted(facts, key=lambda x: x['similarity'], reverse=True)
            return facts_sorted[:top_k]
    
    def search_and_rerank(self, query: str, top_k: int = None, llm_client = None) -> List[Dict]:
        facts = self.search(query, top_k=TOP_K_RETRIEVAL)
        reranked = self.rerank(query, facts, top_k=top_k, llm_client=llm_client)
        
        logger.info(f"Search and re-ranking completed, returning {len(reranked)} facts")
        return reranked

