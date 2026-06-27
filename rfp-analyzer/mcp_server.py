"""
MCP Server for RFP Analyzer

This server exposes the RFP Analyzer functionality as MCP tools that can be
called by AI agents through the IBM ICA MCP Gateway.

The server runs locally and provides JSON-RPC endpoints for:
- Analyzing RFP documents
- Checking analysis status
- Retrieving analysis results
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path to import rfp-analyzer modules
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="RFP Analyzer MCP Server",
    description="MCP server exposing RFP analysis capabilities",
    version="1.0.0"
)

# Store for tracking analysis jobs
analysis_jobs: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Pydantic Models for JSON-RPC
# ============================================================================

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[int | str] = None


class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int | str] = None


# ============================================================================
# MCP Tool Definitions
# ============================================================================

MCP_TOOLS = [
    {
        "name": "analyze_rfp",
        "description": "Analyze an RFP document and extract requirements. Accepts file path or base64-encoded content. Returns a job ID for tracking progress.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the RFP file (PDF, DOCX, or TXT). Use this if file is already on the server."
                },
                "file_content": {
                    "type": "string",
                    "description": "Base64-encoded file content. Use this to upload a file."
                },
                "file_name": {
                    "type": "string",
                    "description": "Original filename (required if using file_content)"
                },
                "title": {
                    "type": "string",
                    "description": "Title for the analysis report",
                    "default": "RFP Analysis"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["markdown", "excel", "both"],
                    "description": "Output format for the analysis",
                    "default": "both"
                },
                "min_confidence": {
                    "type": "number",
                    "description": "Minimum confidence threshold (0.0-1.0) for including requirements",
                    "default": 0.0,
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": []
        }
    },
    {
        "name": "get_analysis_status",
        "description": "Check the status of an RFP analysis job",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "The job ID returned from analyze_rfp"
                }
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "get_analysis_results",
        "description": "Retrieve the results of a completed RFP analysis",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "The job ID of the completed analysis"
                },
                "format": {
                    "type": "string",
                    "enum": ["summary", "full", "markdown", "excel_path"],
                    "description": "Format of results to return",
                    "default": "summary"
                }
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "list_analyses",
        "description": "List all RFP analyses (recent first)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of analyses to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "pending", "running", "completed", "failed"],
                    "description": "Filter by status",
                    "default": "all"
                }
            },
            "required": []
        }
    }
]


# ============================================================================
# Tool Implementation Functions
# ============================================================================

async def analyze_rfp_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Start an RFP analysis job.
    
    This function handles both file paths and base64-encoded content,
    saves the file if needed, and starts the analysis in the background.
    """
    import base64
    from pathlib import Path
    
    job_id = str(uuid.uuid4())
    
    # Get parameters
    file_path: Optional[str] = params.get("file_path")
    file_content: Optional[str] = params.get("file_content")
    file_name: Optional[str] = params.get("file_name")
    title: str = params.get("title", "RFP Analysis")
    output_format: str = params.get("output_format", "both")
    min_confidence: float = params.get("min_confidence", 0.0)
    
    # Validate inputs
    if not file_path and not file_content:
        return {
            "success": False,
            "error": "Either file_path or file_content must be provided"
        }
    
    if file_content and not file_name:
        return {
            "success": False,
            "error": "file_name is required when providing file_content"
        }
    
    try:
        # Handle file content upload
        if file_content and file_name:
            # Decode base64 content
            file_bytes = base64.b64decode(file_content)
            
            # Save to uploads directory
            uploads_dir = Path("./uploads") / job_id
            uploads_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = str(uploads_dir / file_name)
            with open(file_path, "wb") as f:
                f.write(file_bytes)
            
            logger.info(f"Saved uploaded file to {file_path}")
        
        # Validate file exists (file_path is guaranteed to be str at this point)
        if not file_path or not Path(file_path).exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Create job record
        analysis_jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "file_path": file_path,
            "title": title,
            "output_format": output_format,
            "min_confidence": min_confidence,
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            "results": None
        }
        
        # Start analysis in background
        asyncio.create_task(run_analysis(job_id))
        
        return {
            "success": True,
            "job_id": job_id,
            "status": "pending",
            "message": f"Analysis started for {Path(file_path).name if file_path else 'unknown'}"
        }
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e)
        }


async def get_analysis_status_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get the status of an analysis job."""
    job_id = params.get("job_id")
    
    if not job_id:
        return {
            "success": False,
            "error": "job_id is required"
        }
    
    job = analysis_jobs.get(job_id)
    if not job:
        return {
            "success": False,
            "error": f"Job not found: {job_id}"
        }
    
    return {
        "success": True,
        "job_id": job_id,
        "status": job["status"],
        "created_at": job["created_at"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "error": job["error"]
    }


async def get_analysis_results_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve results from a completed analysis."""
    job_id = params.get("job_id")
    result_format = params.get("format", "summary")
    
    if not job_id:
        return {
            "success": False,
            "error": "job_id is required"
        }
    
    job = analysis_jobs.get(job_id)
    if not job:
        return {
            "success": False,
            "error": f"Job not found: {job_id}"
        }
    
    if job["status"] != "completed":
        return {
            "success": False,
            "error": f"Analysis not completed. Current status: {job['status']}"
        }
    
    results = job.get("results", {})
    
    if result_format == "summary":
        return {
            "success": True,
            "job_id": job_id,
            "summary": results.get("summary", {}),
            "output_files": results.get("output_files", {})
        }
    elif result_format == "full":
        return {
            "success": True,
            "job_id": job_id,
            "results": results
        }
    elif result_format == "markdown":
        md_path = results.get("output_files", {}).get("markdown")
        if md_path and Path(md_path).exists():
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            return {
                "success": True,
                "job_id": job_id,
                "markdown": content
            }
        return {
            "success": False,
            "error": "Markdown file not found"
        }
    elif result_format == "excel_path":
        return {
            "success": True,
            "job_id": job_id,
            "excel_path": results.get("output_files", {}).get("excel")
        }
    
    return {
        "success": False,
        "error": f"Unknown format: {result_format}"
    }


async def list_analyses_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """List all analyses."""
    limit = params.get("limit", 10)
    status_filter = params.get("status", "all")
    
    # Filter and sort jobs
    jobs_list = list(analysis_jobs.values())
    
    if status_filter != "all":
        jobs_list = [j for j in jobs_list if j["status"] == status_filter]
    
    # Sort by created_at (most recent first)
    jobs_list.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limit results
    jobs_list = jobs_list[:limit]
    
    # Return simplified info
    simplified = [
        {
            "job_id": j["job_id"],
            "status": j["status"],
            "title": j["title"],
            "file_path": Path(j["file_path"]).name,
            "created_at": j["created_at"],
            "completed_at": j["completed_at"]
        }
        for j in jobs_list
    ]
    
    return {
        "success": True,
        "count": len(simplified),
        "analyses": simplified
    }


# ============================================================================
# Background Analysis Runner
# ============================================================================

async def run_analysis(job_id: str):
    """
    Run the RFP analysis in the background.
    
    This function imports and runs the main analysis logic,
    updating the job status as it progresses.
    """
    job = analysis_jobs[job_id]
    
    try:
        job["status"] = "running"
        job["started_at"] = datetime.now().isoformat()
        
        logger.info(f"Starting analysis for job {job_id}")
        
        # Import analysis function
        # Note: This is a simplified version - you'll need to adapt based on your actual main.py structure
        from main import analyze as run_rfp_analysis
        
        # Prepare output directory
        output_dir = Path("./outputs/web") / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Run analysis (this is synchronous, so we run it in executor)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            run_rfp_analysis,
            job["file_path"],
            str(output_dir),
            job["title"],
            job_id,
            job["output_format"],
            job["min_confidence"]
        )
        
        # Update job with results
        job["status"] = "completed"
        job["completed_at"] = datetime.now().isoformat()
        
        # Find output files
        md_file = list(output_dir.glob("*.md"))
        excel_file = list(output_dir.glob("*.xlsx"))
        
        job["results"] = {
            "output_files": {
                "markdown": str(md_file[0]) if md_file else None,
                "excel": str(excel_file[0]) if excel_file else None
            },
            "summary": {
                "message": "Analysis completed successfully",
                "output_directory": str(output_dir)
            }
        }
        
        logger.info(f"Analysis completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed for job {job_id}: {e}", exc_info=True)
        job["status"] = "failed"
        job["completed_at"] = datetime.now().isoformat()
        job["error"] = str(e)


# ============================================================================
# JSON-RPC Endpoints
# ============================================================================

@app.get("/mcp")
async def mcp_endpoint_get():
    """
    GET endpoint for MCP - returns tools list.
    IBM ICA Gateway may use GET to validate the server and discover tools.
    Returns the same format as POST tools/list for compatibility.
    """
    return JSONResponse({
        "jsonrpc": "2.0",
        "result": {
            "tools": MCP_TOOLS
        },
        "id": None
    })


@app.post("/mcp")
async def mcp_endpoint(request: JSONRPCRequest):
    """
    Main MCP endpoint that handles JSON-RPC requests.
    
    Supports:
    - tools/list: List available tools
    - tools/call: Execute a tool
    """
    try:
        if request.method == "initialize":
            # MCP initialization handshake
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        },
                        "resources": {
                            "subscribe": False,
                            "listChanged": False
                        },
                        "prompts": {
                            "listChanged": False
                        },
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": "RFP Analyzer MCP Server",
                        "version": "1.0.0"
                    }
                },
                "id": request.id
            })
        
        elif request.method == "notifications/initialized":
            # Handle initialized notification from client
            # This is a notification, so we don't send a response
            logger.info("Client sent initialized notification")
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {},
                "id": request.id
            })
        
        elif request.method == "tools/list":
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "tools": MCP_TOOLS
                },
                "id": request.id
            })
        
        elif request.method == "resources/list":
            # Return empty resources list (we don't provide resources, only tools)
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "resources": []
                },
                "id": request.id
            })
        
        elif request.method == "prompts/list":
            # Return empty prompts list (we don't provide prompts, only tools)
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "prompts": []
                },
                "id": request.id
            })
        
        elif request.method == "resources/templates/list":
            # Return empty templates list
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "resourceTemplates": []
                },
                "id": request.id
            })
        
        elif request.method.startswith("resources/"):
            # Handle any other resources/* methods gracefully
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "resources": []
                },
                "id": request.id
            })
        
        elif request.method.startswith("prompts/"):
            # Handle any other prompts/* methods gracefully
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "prompts": []
                },
                "id": request.id
            })
        
        elif request.method == "tools/call":
            if not request.params:
                raise HTTPException(status_code=400, detail="params required for tools/call")
            
            tool_name = request.params.get("name")
            arguments = request.params.get("arguments", {})
            
            # Route to appropriate tool
            if tool_name == "analyze_rfp":
                result = await analyze_rfp_tool(arguments)
            elif tool_name == "get_analysis_status":
                result = await get_analysis_status_tool(arguments)
            elif tool_name == "get_analysis_results":
                result = await get_analysis_results_tool(arguments)
            elif tool_name == "list_analyses":
                result = await list_analyses_tool(arguments)
            else:
                raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
            
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                },
                "id": request.id
            })
        
        else:
            raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
    
    except Exception as e:
        logger.error(f"Error handling request: {e}", exc_info=True)
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": str(e)
            },
            "id": request.id
        }, status_code=500)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "RFP Analyzer MCP Server",
        "version": "1.0.0",
        "active_jobs": len([j for j in analysis_jobs.values() if j["status"] in ["pending", "running"]])
    }


@app.get("/sse")
async def mcp_sse_endpoint():
    """
    SSE (Server-Sent Events) endpoint for MCP.
    Used by Context Forge and other SSE-based MCP clients.
    Streams server info and maintains connection.
    """
    async def event_generator():
        # Send initialization event
        init_event = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False},
                    "prompts": {"listChanged": False},
                    "logging": {}
                },
                "serverInfo": {
                    "name": "RFP Analyzer MCP Server",
                    "version": "1.0.0"
                }
            }
        }
        yield f"data: {json.dumps(init_event)}\n\n"
        
        # Send tools list event
        tools_event = {
            "jsonrpc": "2.0",
            "method": "notifications/tools/list_changed",
            "params": {
                "tools": MCP_TOOLS
            }
        }
        yield f"data: {json.dumps(tools_event)}\n\n"
        
        # Keep connection alive with periodic heartbeats
        try:
            while True:
                await asyncio.sleep(30)
                heartbeat = {
                    "jsonrpc": "2.0",
                    "method": "notifications/heartbeat",
                    "params": {
                        "timestamp": datetime.now().isoformat(),
                        "status": "healthy"
                    }
                }
                yield f"data: {json.dumps(heartbeat)}\n\n"
        except asyncio.CancelledError:
            logger.info("SSE connection closed")
            return
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "RFP Analyzer MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "mcp": "/mcp (GET/POST) - JSON-RPC endpoint for MCP tools",
            "sse": "/sse (GET) - Server-Sent Events endpoint for streaming",
            "health": "/health (GET) - Health check",
            "docs": "/docs - API documentation"
        },
        "transports": ["HTTP", "SSE"],
        "protocol": "MCP (Model Context Protocol)",
        "tools": [tool["name"] for tool in MCP_TOOLS]
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", "8001"))
    
    logger.info(f"Starting RFP Analyzer MCP Server on port {port}")
    logger.info(f"MCP endpoint: http://localhost:{port}/mcp")
    logger.info(f"Health check: http://localhost:{port}/health")
    logger.info(f"API docs: http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

# Made with Bob
