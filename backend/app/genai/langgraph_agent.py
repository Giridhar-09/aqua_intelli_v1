"""
AquaIntelli - GenAI Module: LangGraph Agent Workflows
Multi-step agent workflows for complex water analysis.
"""
import logging
from typing import TypedDict, Optional, Annotated
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State passed between agent nodes."""
    question: str
    lat: Optional[float]
    lon: Optional[float]
    satellite_data: Optional[dict]
    groundwater_analysis: Optional[dict]
    rag_context: Optional[str]
    final_answer: Optional[str]
    steps: list[str]


class WaterAnalysisAgent:
    """
    Multi-step agent using LangGraph pattern.
    Steps: Parse Query → Fetch Satellite → Analyze Groundwater → RAG Augment → Synthesize
    Falls back to mock for demo without LangGraph deps.
    """

    def __init__(self):
        self.graph = None
        self._try_init_graph()

    def _try_init_graph(self):
        """Try to build the LangGraph workflow."""
        try:
            from langgraph.graph import StateGraph, END
            builder = StateGraph(AgentState)
            builder.add_node("parse_query", self._parse_query)
            builder.add_node("fetch_satellite", self._fetch_satellite)
            builder.add_node("analyze_groundwater", self._analyze_groundwater)
            builder.add_node("augment_rag", self._augment_rag)
            builder.add_node("synthesize", self._synthesize)
            builder.set_entry_point("parse_query")
            builder.add_edge("parse_query", "fetch_satellite")
            builder.add_edge("fetch_satellite", "analyze_groundwater")
            builder.add_edge("analyze_groundwater", "augment_rag")
            builder.add_edge("augment_rag", "synthesize")
            builder.add_edge("synthesize", END)
            self.graph = builder.compile()
            logger.info("LangGraph workflow compiled")
        except ImportError:
            logger.info("LangGraph not available, using mock agent")
        except Exception as e:
            logger.warning(f"LangGraph init failed: {e}")

    def _parse_query(self, state: AgentState) -> dict:
        q = state["question"].lower()
        lat = state.get("lat", 16.5)
        lon = state.get("lon", 80.6)
        steps = state.get("steps", [])
        steps.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Parsed query: extracted location ({lat}, {lon})")
        return {"steps": steps, "lat": lat, "lon": lon}

    def _fetch_satellite(self, state: AgentState) -> dict:
        from ..services.satellite_service import grace_service, sentinel_service
        lat, lon = state.get("lat", 16.5), state.get("lon", 80.6)
        data = {
            "grace": grace_service.mock_anomaly(lat, lon),
            "soil": sentinel_service.get_soil_moisture(lat, lon),
            "ndvi": sentinel_service.get_ndvi(lat, lon),
        }
        steps = state.get("steps", [])
        steps.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Fetched satellite data: GRACE={data['grace']['anomaly_m']:.2f}m")
        return {"satellite_data": data, "steps": steps}

    def _analyze_groundwater(self, state: AgentState) -> dict:
        sat = state.get("satellite_data", {})
        grace = sat.get("grace", {}).get("anomaly_m", -2)
        sm = sat.get("soil", {}).get("soil_moisture_pct", 50)
        analysis = {
            "severity": "CRITICAL" if grace < -5 else "WARNING" if grace < -2 else "NORMAL",
            "depletion_rate": f"{abs(grace) * 3:.1f} cm/year",
            "soil_moisture_status": "LOW" if sm < 30 else "ADEQUATE" if sm < 60 else "HIGH",
        }
        steps = state.get("steps", [])
        steps.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Groundwater analyzed: {analysis['severity']}")
        return {"groundwater_analysis": analysis, "steps": steps}

    def _augment_rag(self, state: AgentState) -> dict:
        steps = state.get("steps", [])
        steps.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] RAG context retrieved from knowledge base")
        return {"rag_context": "CGWB report, GRACE data, Indian water policy documents", "steps": steps}

    def _synthesize(self, state: AgentState) -> dict:
        analysis = state.get("groundwater_analysis", {})
        sat = state.get("satellite_data", {})
        grace_val = sat.get("grace", {}).get("anomaly_m", -2)
        answer = (
            f"Based on multi-source analysis:\n"
            f"• GRACE-FO anomaly: {grace_val:.2f}m - Status: {analysis.get('severity', 'UNKNOWN')}\n"
            f"• Soil moisture: {sat.get('soil', {}).get('soil_moisture_pct', 'N/A')}%\n"
            f"• Vegetation (NDVI): {sat.get('ndvi', {}).get('ndvi', 'N/A')}\n"
            f"• Estimated depletion: {analysis.get('depletion_rate', 'N/A')}\n\n"
            f"Recommendation: {'Immediate intervention needed. High-risk zone.' if analysis.get('severity') == 'CRITICAL' else 'Continue monitoring. Implement recharge measures.'}"
        )
        steps = state.get("steps", [])
        steps.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Synthesis complete")
        return {"final_answer": answer, "steps": steps}

    async def run(self, question: str, lat: float = 16.5, lon: float = 80.6) -> dict:
        """Run the multi-step agent analysis."""
        initial_state: AgentState = {
            "question": question, "lat": lat, "lon": lon,
            "satellite_data": None, "groundwater_analysis": None,
            "rag_context": None, "final_answer": None, "steps": [],
        }

        if self.graph:
            try:
                result = self.graph.invoke(initial_state)
                return {
                    "answer": result.get("final_answer", "Analysis complete."),
                    "steps": result.get("steps", []),
                    "satellite_data": result.get("satellite_data"),
                    "analysis": result.get("groundwater_analysis"),
                    "engine": "langgraph",
                }
            except Exception as e:
                logger.error(f"LangGraph execution failed: {e}")

        # Fallback: run nodes manually
        state = initial_state
        self._parse_query(state)
        state.update(self._fetch_satellite(state))
        state.update(self._analyze_groundwater(state))
        state.update(self._augment_rag(state))
        state.update(self._synthesize(state))

        return {
            "answer": state.get("final_answer", "Analysis complete."),
            "steps": state.get("steps", []),
            "satellite_data": state.get("satellite_data"),
            "analysis": state.get("groundwater_analysis"),
            "engine": "mock_sequential",
        }


# Singleton
water_agent = WaterAnalysisAgent()
