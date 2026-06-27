# RFP Analyzer MCP Server - Quick Reference

## 🚀 Quick Commands

### Start Server
```bash
cd rfp-analyzer
python mcp_server.py
```

### Test Server
```bash
python test_mcp_server.py
```

### Expose Server (ngrok)
```bash
python expose_server.py
```

### Register with IBM ICA
```bash
python register_with_ibm_ica.py
```

## 📡 Endpoints

| Endpoint | URL | Purpose |
|----------|-----|---------|
| MCP | `http://localhost:8001/mcp` | Main JSON-RPC endpoint |
| Health | `http://localhost:8001/health` | Health check |
| Docs | `http://localhost:8001/docs` | API documentation |
| Root | `http://localhost:8001/` | Service info |

## 🛠️ Available MCP Tools

1. **`analyze_rfp`** - Start RFP analysis
   - Inputs: `file_path`, `file_content`, `title`, `output_format`, `min_confidence`
   - Returns: `job_id`, `status`

2. **`get_analysis_status`** - Check job status
   - Inputs: `job_id`
   - Returns: `status`, `created_at`, `completed_at`

3. **`get_analysis_results`** - Get results
   - Inputs: `job_id`, `format` (summary/full/markdown/excel_path)
   - Returns: Analysis results

4. **`list_analyses`** - List all analyses
   - Inputs: `limit`, `status`
   - Returns: List of analyses

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your-key-here
MCP_SERVER_PORT=8001
MCP_AUTHORIZATION=Bearer your-token
```

### Files
- `.env` - Environment variables
- `.mcp_server_id` - Registered server ID
- `.ngrok_tunnel.json` - Tunnel information

## 📝 Usage Examples

### Test MCP Endpoint
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### Analyze RFP
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "analyze_rfp",
      "arguments": {
        "file_path": "/path/to/rfp.pdf",
        "title": "My RFP"
      }
    },
    "id": 2
  }'
```

### Check Status
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_analysis_status",
      "arguments": {"job_id": "abc-123"}
    },
    "id": 3
  }'
```

## 🐍 Python Usage

### From Agent
```python
from src.agents.base_with_mcp import BaseAgentWithMCP

agent = BaseAgentWithMCP(
    name="rfp_assistant",
    system_prompt="You help analyze RFP documents.",
    mcp_server_url="<your-mcp-endpoint>",
    mcp_authorization="Bearer <token>"
)

response = agent.process_request(
    "Analyze the RFP at /path/to/rfp.pdf"
)
```

### Direct MCP Call
```python
import requests

response = requests.post(
    "http://localhost:8001/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "analyze_rfp",
            "arguments": {
                "file_path": "/path/to/rfp.pdf"
            }
        },
        "id": 1
    }
)

result = response.json()
job_id = result["result"]["content"][0]["text"]
```

## 🐳 Docker Commands

### Build
```bash
docker build -t rfp-analyzer-mcp .
```

### Run
```bash
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=your-key \
  rfp-analyzer-mcp
```

### Docker Compose
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## 🔍 Troubleshooting

### Check Server Status
```bash
curl http://localhost:8001/health
```

### View Logs
```bash
tail -f logs/rfp_analyzer.log
```

### Test Tools Discovery
```bash
python -c "import requests; print(requests.post('http://localhost:8001/mcp', json={'jsonrpc':'2.0','method':'tools/list','id':1}).json())"
```

### Check Port
```bash
netstat -an | findstr 8001
```

## 📚 Documentation

- **Setup Guide**: [`MCP_SERVER_SETUP.md`](MCP_SERVER_SETUP.md)
- **Expose & Register**: [`EXPOSE_AND_REGISTER.md`](EXPOSE_AND_REGISTER.md)
- **Implementation**: [`IMPLEMENTATION_SUMMARY.md`](IMPLEMENTATION_SUMMARY.md)
- **Main README**: [`README.md`](README.md)

## 🔗 Important URLs

### Local
- Server: http://localhost:8001
- Health: http://localhost:8001/health
- Docs: http://localhost:8001/docs
- ngrok Dashboard: http://localhost:4040

### IBM ICA
- Gateway: https://ica-pr-us-south-global-ica-pr-us-south-global.apps.ica-pr-us-south.cp.fyre.ibm.com
- Your Server: `https://ica-gateway.../servers/<server-id>/mcp`

## ⚡ Common Tasks

### Start Everything
```bash
# Terminal 1: Start MCP server
cd rfp-analyzer
python mcp_server.py

# Terminal 2: Expose with ngrok
python expose_server.py

# Terminal 3: Register with IBM ICA
python register_with_ibm_ica.py
```

### Test End-to-End
```bash
# 1. Start server
python mcp_server.py &

# 2. Run tests
python test_mcp_server.py

# 3. Test with agent
python test_rfp_agent.py
```

### Deploy to Production
```bash
# Build Docker image
docker build -t rfp-analyzer-mcp .

# Push to registry
docker tag rfp-analyzer-mcp:latest <registry>/rfp-analyzer-mcp:latest
docker push <registry>/rfp-analyzer-mcp:latest

# Deploy (example for AWS ECS)
aws ecs update-service --cluster my-cluster --service rfp-analyzer --force-new-deployment
```

## 📊 Monitoring

### Health Check
```bash
watch -n 5 'curl -s http://localhost:8001/health | jq'
```

### Active Jobs
```bash
curl http://localhost:8001/health | jq '.active_jobs'
```

### Recent Analyses
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"list_analyses","arguments":{"limit":5}},"id":1}' \
  | jq
```

## 🎯 Next Steps

1. ✅ Server running locally
2. ✅ Exposed publicly (ngrok or cloud)
3. ✅ Registered with IBM ICA
4. ⏳ Test from your agent
5. ⏳ Process sample RFPs
6. ⏳ Deploy to production

---

**Quick Help**: Run `python <script>.py --help` for any script