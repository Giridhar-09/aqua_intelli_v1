"""
AquaIntelli - GenAI Module: MCP Server
Model Context Protocol server exposing water intelligence tools.
"""
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MCPWaterTools:
    """
    MCP-compatible tool server for water intelligence.
    Exposes tools that can be called by LLM agents.
    """

    def __init__(self):
        self.tools = {
            "get_groundwater_status": {
                "name": "get_groundwater_status",
                "description": "Get comprehensive groundwater status for a location including GRACE anomaly, soil moisture, and AI forecast.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number", "description": "Latitude"},
                        "lon": {"type": "number", "description": "Longitude"},
                        "district": {"type": "string", "description": "District name"},
                        "state": {"type": "string", "description": "State name"},
                    },
                    "required": ["lat", "lon"],
                },
            },
            "predict_borewell": {
                "name": "predict_borewell",
                "description": "Predict borewell drilling success probability using satellite data and geology.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lat": {"type": "number"}, "lon": {"type": "number"},
                        "soil_type": {"type": "string", "enum": ["red", "black", "alluvial", "laterite", "sandy"]},
                        "depth_m": {"type": "number"}, "aquifer_type": {"type": "string"},
                    },
                    "required": ["lat", "lon"],
                },
            },
            "calculate_irrigation": {
                "name": "calculate_irrigation",
                "description": "Calculate crop water requirement using FAO-56 Penman-Monteith model.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "crop_type": {"type": "string"}, "growth_stage": {"type": "string"},
                        "temp_c": {"type": "number"}, "humidity_pct": {"type": "number"},
                    },
                    "required": ["crop_type"],
                },
            },
            "query_water_network": {
                "name": "query_water_network",
                "description": "Query the water network graph for rivers, aquifers, reservoirs, and their relationships.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {"type": "string", "enum": ["rivers", "aquifers", "districts", "reservoirs", "all"]},
                    },
                    "required": ["entity_type"],
                },
            },
            "get_water_futures": {
                "name": "get_water_futures",
                "description": "Get current water futures exchange prices and AI price predictions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset_id": {"type": "string", "description": "Asset ID e.g. WFX-AP-Q2"},
                    },
                },
            },
        }

    def list_tools(self) -> list[dict]:
        return list(self.tools.values())

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute an MCP tool call."""
        if tool_name == "get_groundwater_status":
            from ..services.groundwater_service import get_groundwater_status
            return await get_groundwater_status(
                arguments.get("lat", 16.5), arguments.get("lon", 80.6),
                arguments.get("district", ""), arguments.get("state", "")
            )
        elif tool_name == "predict_borewell":
            from ..services.borewell_service import borewell_predictor
            return borewell_predictor.predict(**arguments)
        elif tool_name == "calculate_irrigation":
            from ..services.irrigation_service import calculate_etc
            return calculate_etc(**arguments)
        elif tool_name == "query_water_network":
            from .graph_rag import graph_rag
            return {"entities": graph_rag.query_graph(arguments.get("entity_type", "all"))}
        elif tool_name == "get_water_futures":
            from ..services.exchange_service import get_all_assets, get_price_oracle
            asset_id = arguments.get("asset_id")
            if asset_id:
                return get_price_oracle(asset_id)
            return {"assets": get_all_assets()}
        else:
            return {"error": f"Unknown tool: {tool_name}"}


# Singleton
mcp_tools = MCPWaterTools()
