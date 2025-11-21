# Claim Extraction Prompt
CLAIM_EXTRACTION_PROMPT = """
Extract all factual claims from the following text. 
A claim is a statement that can be verified as true or false.

Text: {text}

Return only the claims, one per line. Be precise and specific.
"""

# Verification Prompt
VERIFICATION_PROMPT = """
You are a fact-checker. Verify the following claim against the provided evidence.

Claim: {claim}

Evidence:
{evidence}

Based on the evidence provided, determine:
1. Verdict: One of "True", "False", or "Unverifiable"
   - "True" if evidence supports the claim
   - "False" if evidence contradicts the claim
   - "Unverifiable" if evidence is insufficient or unclear
2. Reasoning: Brief explanation (2-3 sentences) explaining your verdict

Format your response as JSON:
{{
    "verdict": "True" | "False" | "Unverifiable",
    "reasoning": "Your explanation here"
}}
"""

# Re-ranking Prompt
RERANKING_PROMPT = """
Rank the following search results by relevance to the claim.

Claim: {claim}

Search Results:
{results}

Rank them from most relevant (1) to least relevant ({count}).
Return only the indices in order of relevance, comma-separated.
"""

# Fact Generation Prompt (for data ingestion)
FACT_GENERATION_PROMPT = """
Extract structured factual information from the following text.

Text: {text}

Extract:
1. Key factual statements (one per line)
2. Source information
3. Date/context if available

Format as JSON array:
[
    {{
        "fact": "The factual statement",
        "source": "Source information",
        "date": "Date if available",
        "context": "Additional context"
    }}
]
"""

# Query Expansion Prompt
QUERY_EXPANSION_PROMPT = """
Generate search queries to find evidence for this claim.

Claim: {claim}

Generate 3-5 alternative phrasings or related search queries.
Return them as a JSON array of strings:
["query1", "query2", "query3"]
"""

