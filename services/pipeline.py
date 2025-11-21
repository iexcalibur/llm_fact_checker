from typing import List, Dict, Optional
from models.claim_extractor import ClaimExtractor
from models.embedder import Embedder
from models.llm_client import LLMClient
from services.retriever import Retriever
from services.store_manager import StoreManager
from utils.logger import logger


class FactCheckPipeline:
    
    def __init__(
        self,
        claim_extractor: Optional[ClaimExtractor] = None,
        embedder: Optional[Embedder] = None,
        llm_client: Optional[LLMClient] = None,
        store_manager: Optional[StoreManager] = None
    ):
        self.claim_extractor = claim_extractor or ClaimExtractor()
        self.embedder = embedder or Embedder()
        self.llm_client = llm_client or LLMClient()
        self.store_manager = store_manager or StoreManager()
        
        self.retriever = Retriever(self.embedder, self.store_manager)
        
        logger.info("FactCheckPipeline initialized successfully")
    
    def extract_claims(self, text: str, method: str = "spacy") -> List[str]:
        logger.info(f"Extracting claims using method: {method}")
        
        if method == "llm":
            return self.claim_extractor.extract_claims_llm(text, self.llm_client)
        else:
            return self.claim_extractor.extract_claims(text)
    
    def verify_claim(self, claim: str, evidence: Optional[str] = None) -> Dict:
        logger.info(f"Verifying claim: {claim[:100]}...")
        
        if evidence is None:
            relevant_facts = self.retriever.search_and_rerank(
                claim,
                llm_client=self.llm_client
            )
            
            if not relevant_facts:
                logger.warning("No relevant evidence found in database")
                return {
                    "claim": claim,
                    "verdict": "Unverifiable",
                    "confidence": 0.0,
                    "evidence": [],
                    "reasoning": "No relevant evidence found in database. Cannot verify this claim with available information."
                }
            
            evidence_list = [fact['text'] for fact in relevant_facts[:3]]
            
            evidence_text = "\n\n".join([
                f"Evidence {i+1}:\n{fact['text']}\nSource: {fact['metadata'].get('source', 'unknown')}\nDate: {fact['metadata'].get('date', 'unknown')}"
                for i, fact in enumerate(relevant_facts[:3])
            ])
            
            logger.info(f"Retrieved {len(relevant_facts)} relevant facts")
        else:
            evidence_text = evidence
            evidence_list = [evidence]
        
        result = self.llm_client.verify_claim(claim, evidence_text)
        
        result["claim"] = claim
        result["evidence"] = evidence_list
        
        logger.info(f"Verification complete: {result['verdict']} (confidence: {result.get('confidence', 0):.2f})")
        return result
    
    def verify_text(self, text: str, extract_claims: bool = True, method: str = "spacy") -> List[Dict]:
        logger.info("Starting text verification")
        
        if extract_claims:
            claims = self.extract_claims(text, method=method)
        else:
            claims = [text]
        
        if not claims:
            logger.warning("No claims extracted from text")
            return []
        
        logger.info(f"Verifying {len(claims)} claims")
        
        results = []
        for i, claim in enumerate(claims, 1):
            logger.info(f"Verifying claim {i}/{len(claims)}")
            result = self.verify_claim(claim)
            results.append(result)
        
        logger.info(f"Text verification complete: {len(results)} claims verified")
        return results
    
    def verify_multiple_claims(self, claims: List[str]) -> List[Dict]:
        logger.info(f"Verifying {len(claims)} claims")
        
        results = []
        for i, claim in enumerate(claims, 1):
            logger.info(f"Verifying claim {i}/{len(claims)}")
            result = self.verify_claim(claim)
            results.append(result)
        
        logger.info(f"Batch verification complete")
        return results