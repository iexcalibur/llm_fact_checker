from typing import List, Optional
import spacy

from config import SPACY_MODEL
from utils.logger import logger


class ClaimExtractor:
    
    def __init__(self):
        self.spacy_model = None
        self._load_spacy()
        logger.info("ClaimExtractor initialized with spaCy")
    
    def _load_spacy(self):
        try:
            logger.info(f"Loading spaCy model: {SPACY_MODEL}")
            self.spacy_model = spacy.load(SPACY_MODEL)
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.error(f"spaCy model {SPACY_MODEL} not found")
            logger.info(f"Please run: python -m spacy download {SPACY_MODEL}")
            raise
    
    def extract_claims(self, text: str) -> List[str]:
        if not self.spacy_model:
            self._load_spacy()
        
        doc = self.spacy_model(text)
        claims = []
        
        for sent in doc.sents:
            sent_text = sent.text.strip()
            
            if len(sent_text) < 20:
                continue
            
            if sent_text.endswith('?'):
                continue
            
            if sent_text.endswith('!'):
                continue
            
            has_verb = any(token.pos_ == "VERB" for token in sent)
            has_noun = any(token.pos_ in ["NOUN", "PROPN"] for token in sent)
            
            if has_verb and has_noun:
                claims.append(sent_text)
        
        logger.info(f"Extracted {len(claims)} claims using spaCy")
        return claims
    
    def extract_claims_llm(self, text: str, llm_client) -> List[str]:
        from utils.prompts import CLAIM_EXTRACTION_PROMPT
        
        prompt = CLAIM_EXTRACTION_PROMPT.format(text=text)
        
        try:
            response = llm_client.generate(prompt)
            
            claims = []
            for line in response.strip().split('\n'):
                line = line.strip()
                if line and len(line) > 2:
                    if line[0].isdigit():
                        line = line.split('.', 1)[-1].strip()
                    if line:
                        claims.append(line)
            
            logger.info(f"Extracted {len(claims)} claims using LLM")
            return claims
            
        except Exception as e:
            logger.error(f"Error extracting claims with LLM: {str(e)}")
            logger.info("Falling back to spaCy extraction")
            return self.extract_claims(text)