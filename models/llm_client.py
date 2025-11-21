import os
import json
from typing import Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

from config import CLAUDE_MODEL, CLAUDE_MAX_TOKENS, CLAUDE_TEMPERATURE
from utils.logger import logger

load_dotenv()


class LLMClient:
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = CLAUDE_MODEL
        self.max_tokens = CLAUDE_MAX_TOKENS
        self.temperature = CLAUDE_TEMPERATURE
        
        logger.info(f"LLMClient initialized with model: {self.model}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        try:
            temperature = kwargs.get("temperature", self.temperature)
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            
            messages = [{"role": "user", "content": prompt}]
            
            api_params = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            
            if system_prompt is not None:
                api_params["system"] = system_prompt
            
            response = self.client.messages.create(**api_params)
            
            result = response.content[0].text
            logger.debug(f"LLM generated response: {result[:100]}...")
            return result
        
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            raise
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> Dict:
        try:
            response = self.generate(prompt, system_prompt, **kwargs)
            
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            return json.loads(response)
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.debug(f"Response was: {response}")
            raise
        except Exception as e:
            logger.error(f"Error generating JSON response: {str(e)}")
            raise
    
    def verify_claim(self, claim: str, evidence: str) -> Dict:
        from utils.prompts import VERIFICATION_PROMPT
        
        prompt = VERIFICATION_PROMPT.format(claim=claim, evidence=evidence)
        
        try:
            result = self.generate_json(prompt)
            
            verdict = result.get('verdict', 'Unverifiable')
            confidence = result.get('confidence', 0.5)
            
            if verdict.upper() in ['TRUE', 'CORRECT', 'ACCURATE', 'YES']:
                if confidence >= 0.8:
                    verdict = "Definitely True"
                elif confidence >= 0.6:
                    verdict = "Likely True"
                else:
                    verdict = "Possibly True"
            elif verdict.upper() in ['FALSE', 'INCORRECT', 'INACCURATE', 'NO']:
                if confidence >= 0.8:
                    verdict = "Definitely False"
                elif confidence >= 0.6:
                    verdict = "Likely False"
                else:
                    verdict = "Possibly False"
            else:
                verdict = "Unverifiable"
            
            output = {
                "verdict": verdict,
                "confidence": float(confidence),
                "reasoning": result.get('reasoning', result.get('explanation', 'No reasoning provided'))
            }
            
            logger.info(f"Claim verification: {verdict} (confidence: {confidence:.2f})")
            return output
            
        except Exception as e:
            logger.error(f"Error verifying claim: {str(e)}")
            return {
                "verdict": "Unverifiable",
                "confidence": 0.0,
                "reasoning": f"Error during verification: {str(e)}"
            }