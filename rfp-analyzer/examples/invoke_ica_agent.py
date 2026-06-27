import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"
DEFAULT_AGENT_URL = "https://servicesessentials.ibm.com/agenticapps/a2a/fa134055-8890-4589-80a3-69b473fbc4b4/agents/0eed7bc0-b12b-48b4-bc79-593c5415319a"


def get_access_token(api_key: str) -> Tuple[str, int]:
    response = requests.post(
        IAM_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["access_token"], int(data.get("expires_in", 3600))


def build_candidate_requests(agent_url: str, message: str, session_id: Optional[str]) -> List[Dict[str, Any]]:
    base_payloads = [
        {
            "name": "post-agent-url-input",
            "method": "POST",
            "url": agent_url,
            "json": {
                "input": message,
                "session_id": session_id,
            },
        },
        {
            "name": "post-agent-url-message",
            "method": "POST",
            "url": agent_url,
            "json": {
                "message": message,
                "session_id": session_id,
            },
        },
        {
            "name": "post-agent-url-prompt",
            "method": "POST",
            "url": agent_url,
            "json": {
                "prompt": message,
                "session_id": session_id,
            },
        },
        {
            "name": "post-agent-url-invoke-input",
            "method": "POST",
            "url": f"{agent_url.rstrip('/')}/invoke",
            "json": {
                "input": message,
                "session_id": session_id,
            },
        },
        {
            "name": "post-agent-url-run-input",
            "method": "POST",
            "url": f"{agent_url.rstrip('/')}/run",
            "json": {
                "input": message,
                "session_id": session_id,
            },
        },
        {
            "name": "post-agent-url-chat-messages",
            "method": "POST",
            "url": f"{agent_url.rstrip('/')}/chat",
            "json": {
                "messages": [
                    {"role": "user", "content": message}
                ],
                "session_id": session_id,
            },
        },
        {
            "name": "get-agent-url",
            "method": "GET",
            "url": agent_url,
            "json": None,
        },
    ]
    return base_payloads


def invoke_candidate(
    candidate: Dict[str, Any],
    token: str,
    timeout: int = 60,
) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if candidate.get("json") is not None:
        headers["Content-Type"] = "application/json"

    response = requests.request(
        method=candidate["method"],
        url=candidate["url"],
        headers=headers,
        json=candidate.get("json"),
        timeout=timeout,
    )

    result: Dict[str, Any] = {
        "candidate": candidate["name"],
        "method": candidate["method"],
        "url": candidate["url"],
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "text": response.text,
    }

    try:
        result["json_response"] = response.json()
    except Exception:
        result["json_response"] = None

    return result


def main() -> int:
    api_key = os.getenv("IBM_CLOUD_API_KEY") or os.getenv("ICA_API_KEY")
    bearer_token = os.getenv("ICA_BEARER_TOKEN") or os.getenv("OPENAI_API_KEY")
    auth_mode = os.getenv("ICA_AUTH_MODE", "auto").lower()
    agent_url = os.getenv("ICA_AGENT_URL", DEFAULT_AGENT_URL)
    message = os.getenv("ICA_TEST_MESSAGE", "Hello. Please introduce yourself briefly.")
    session_id = os.getenv("ICA_SESSION_ID", f"stub-session-{int(time.time())}")

    if len(sys.argv) > 1:
        message = sys.argv[1]

    print(f"Using agent URL: {agent_url}")
    print(f"Using session ID: {session_id}")

    token = None

    if auth_mode == "bearer":
        token = bearer_token
        if not token:
            print("ERROR: ICA_AUTH_MODE=bearer but ICA_BEARER_TOKEN/OPENAI_API_KEY is not set.")
            return 1
        print("Using direct bearer token mode.")
    elif auth_mode == "iam":
        if not api_key:
            print("ERROR: ICA_AUTH_MODE=iam but IBM_CLOUD_API_KEY/ICA_API_KEY is not set.")
            return 1
        print("Fetching IAM access token...")
        try:
            token, expires_in = get_access_token(api_key)
            print(f"Access token acquired. Expires in ~{expires_in}s")
        except Exception as exc:
            print(f"ERROR: Failed to get IAM token: {exc}")
            return 2
    else:
        if bearer_token:
            token = bearer_token
            print("Using auto auth mode: selected direct bearer token.")
        elif api_key:
            print("Using auto auth mode: selected IAM API key exchange.")
            try:
                token, expires_in = get_access_token(api_key)
                print(f"Access token acquired. Expires in ~{expires_in}s")
            except Exception as exc:
                print(f"ERROR: Failed to get IAM token: {exc}")
                return 2
        else:
            print("ERROR: Set one of ICA_BEARER_TOKEN, OPENAI_API_KEY, IBM_CLOUD_API_KEY, or ICA_API_KEY.")
            return 1

    custom_payload_raw = os.getenv("ICA_CUSTOM_PAYLOAD")
    if custom_payload_raw:
        try:
            custom_payload = json.loads(custom_payload_raw)
            candidates = [
                {
                    "name": "custom-payload-post-agent-url",
                    "method": "POST",
                    "url": agent_url,
                    "json": custom_payload,
                }
            ]
        except Exception as exc:
            print(f"ERROR: ICA_CUSTOM_PAYLOAD is not valid JSON: {exc}")
            return 3
    else:
        candidates = build_candidate_requests(agent_url, message, session_id)

    for candidate in candidates:
        print("\n" + "=" * 80)
        print(f"Trying candidate: {candidate['name']}")
        print(f"{candidate['method']} {candidate['url']}")
        if candidate.get("json") is not None:
            print("Payload:")
            print(json.dumps(candidate["json"], indent=2))

        try:
            result = invoke_candidate(candidate, token)
            print(f"Status: {result['status_code']}")
            if result["json_response"] is not None:
                print("JSON response:")
                print(json.dumps(result["json_response"], indent=2))
            else:
                print("Raw response:")
                print(result["text"][:4000])

            if 200 <= result["status_code"] < 300:
                print("\nSUCCESS: Candidate returned a 2xx response.")
                return 0

        except Exception as exc:
            print(f"Request failed: {exc}")

    print("\nNo candidate invocation pattern succeeded.")
    print("Next step: inspect the exact ICA API contract and set ICA_CUSTOM_PAYLOAD if needed.")
    return 4


if __name__ == "__main__":
    raise SystemExit(main())

# Made with Bob
