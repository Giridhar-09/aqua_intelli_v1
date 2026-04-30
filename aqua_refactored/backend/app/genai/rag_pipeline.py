"""
AquaIntelli - GenAI: RAG Pipeline (Robust Version)
Direct API implementation for 32-bit compatibility.
"""
import logging
import os
import json
import httpx
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.is_mock = True
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.docs = [
            "AquaIntelli monitors groundwater using GRACE-FO satellite data. Negative anomalies indicate depletion.",
            "The Krishna Basin is a major reservoir source in Andhra Pradesh, providing water to millions.",
            "Borewell success depends on soil type. Hard rock granite requires DTH rigs, while alluvial soil uses rotary rigs.",
            "FAO-56 Penman-Monteith is the gold standard for calculating reference evapotranspiration (ET0).",
            "Nagarjuna Sagar Dam is one of the world's largest masonry dams, located on the Krishna River.",
            "Climate change is accelerating glacial melt, impacting river discharges in the Indo-Gangetic plain.",
            "AQUIFER SCAN uses electromagnetic sensors to map subsurface water-bearing formations up to 500m depth.",
        ]

    def initialize(self):
        """Initialize pipeline - Check API key."""
        if not self.api_key or "sk-" not in self.api_key:
            logger.warning("OPENAI_API_KEY not found. RAG running in static mode.")
            self.is_mock = True
        else:
            self.is_mock = False
            logger.info("OpenAI RAG Pipeline initialized.")

    async def query(self, question: str) -> Dict:
        """Query the intelligence platform."""
        # Simple keyword-based document retrieval (the 'R' in RAG)
        q_words = question.lower().split()
        relevant_docs = []
        for doc in self.docs:
            if any(word in doc.lower() for word in q_words if len(word) > 3):
                relevant_docs.append(doc)
        
        context = "\n".join(relevant_docs) if relevant_docs else self.docs[0]

        if self.is_mock:
            return {
                "answer": f"Searching knowledge base... Found relevant data on: {context[:50]}... Please configure OPENAI_API_KEY for full AI insights.",
                "sources": relevant_docs or ["Internal Knowledge"],
                "mode": "static"
            }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-3.5-turbo",
                        "messages": [
                            {"role": "system", "content": f"You are AquaIntelli AI. Use this context to answer: {context}"},
                            {"role": "user", "content": question}
                        ],
                        "temperature": 0.5
                    },
                    timeout=20.0
                )
                data = resp.json()
                if "choices" in data:
                    return {
                        "answer": data["choices"][0]["message"]["content"],
                        "sources": relevant_docs or ["General Water Science"],
                        "mode": "ai-real"
                    }
                else:
                    return {"answer": f"API Error: {data.get('error', {}).get('message', 'Unknown')}", "mode": "error"}
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {"answer": f"Connection error: {str(e)}", "mode": "error"}

rag_pipeline = RAGPipeline()
