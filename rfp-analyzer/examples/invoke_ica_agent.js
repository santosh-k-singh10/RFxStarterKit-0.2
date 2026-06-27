const IAM_TOKEN_URL = 'https://iam.cloud.ibm.com/identity/token';
const DEFAULT_AGENT_URL = 'https://servicesessentials.ibm.com/agenticapps/a2a/fa134055-8890-4589-80a3-69b473fbc4b4/agents/0eed7bc0-b12b-48b4-bc79-593c5415319a';

async function getAccessToken(apiKey) {
  const body = new URLSearchParams({
    grant_type: 'urn:ibm:params:oauth:grant-type:apikey',
    apikey: apiKey
  });

  const response = await fetch(IAM_TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body
  });

  if (!response.ok) {
    throw new Error(`IAM token fetch failed: ${response.status} ${await response.text()}`);
  }

  return await response.json();
}

function buildCandidateRequests(agentUrl, message, sessionId) {
  return [
    {
      name: 'post-agent-url-input',
      method: 'POST',
      url: agentUrl,
      json: {
        input: message,
        session_id: sessionId
      }
    },
    {
      name: 'post-agent-url-message',
      method: 'POST',
      url: agentUrl,
      json: {
        message,
        session_id: sessionId
      }
    },
    {
      name: 'post-agent-url-prompt',
      method: 'POST',
      url: agentUrl,
      json: {
        prompt: message,
        session_id: sessionId
      }
    },
    {
      name: 'post-agent-url-invoke-input',
      method: 'POST',
      url: `${agentUrl.replace(/\/$/, '')}/invoke`,
      json: {
        input: message,
        session_id: sessionId
      }
    },
    {
      name: 'post-agent-url-run-input',
      method: 'POST',
      url: `${agentUrl.replace(/\/$/, '')}/run`,
      json: {
        input: message,
        session_id: sessionId
      }
    },
    {
      name: 'post-agent-url-chat-messages',
      method: 'POST',
      url: `${agentUrl.replace(/\/$/, '')}/chat`,
      json: {
        messages: [
          { role: 'user', content: message }
        ],
        session_id: sessionId
      }
    },
    {
      name: 'get-agent-url',
      method: 'GET',
      url: agentUrl
    }
  ];
}

async function invokeCandidate(candidate, token) {
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: 'application/json'
  };

  const options = {
    method: candidate.method,
    headers
  };

  if (candidate.json !== undefined) {
    headers['Content-Type'] = 'application/json';
    options.body = JSON.stringify(candidate.json);
  }

  const response = await fetch(candidate.url, options);
  const text = await response.text();

  let jsonResponse = null;
  try {
    jsonResponse = JSON.parse(text);
  } catch (_) {
    jsonResponse = null;
  }

  return {
    candidate: candidate.name,
    method: candidate.method,
    url: candidate.url,
    statusCode: response.status,
    headers: Object.fromEntries(response.headers.entries()),
    text,
    jsonResponse
  };
}

async function main() {
  const apiKey = process.env.IBM_CLOUD_API_KEY || process.env.ICA_API_KEY;
  const agentUrl = process.env.ICA_AGENT_URL || DEFAULT_AGENT_URL;
  const message = process.argv[2] || process.env.ICA_TEST_MESSAGE || 'Hello. Please introduce yourself briefly.';
  const sessionId = process.env.ICA_SESSION_ID || `stub-session-${Date.now()}`;

  if (!apiKey) {
    console.error('ERROR: Set IBM_CLOUD_API_KEY or ICA_API_KEY in the environment.');
    process.exit(1);
  }

  console.log(`Using agent URL: ${agentUrl}`);
  console.log(`Using session ID: ${sessionId}`);
  console.log('Fetching IAM access token...');

  let tokenData;
  try {
    tokenData = await getAccessToken(apiKey);
    console.log(`Access token acquired. Expires in ~${tokenData.expires_in || 3600}s`);
  } catch (error) {
    console.error(`ERROR: Failed to get IAM token: ${error.message}`);
    process.exit(2);
  }

  let candidates;
  if (process.env.ICA_CUSTOM_PAYLOAD) {
    try {
      const customPayload = JSON.parse(process.env.ICA_CUSTOM_PAYLOAD);
      candidates = [
        {
          name: 'custom-payload-post-agent-url',
          method: 'POST',
          url: agentUrl,
          json: customPayload
        }
      ];
    } catch (error) {
      console.error(`ERROR: ICA_CUSTOM_PAYLOAD is not valid JSON: ${error.message}`);
      process.exit(3);
    }
  } else {
    candidates = buildCandidateRequests(agentUrl, message, sessionId);
  }

  for (const candidate of candidates) {
    console.log('\n' + '='.repeat(80));
    console.log(`Trying candidate: ${candidate.name}`);
    console.log(`${candidate.method} ${candidate.url}`);
    if (candidate.json !== undefined) {
      console.log('Payload:');
      console.log(JSON.stringify(candidate.json, null, 2));
    }

    try {
      const result = await invokeCandidate(candidate, tokenData.access_token);
      console.log(`Status: ${result.statusCode}`);
      if (result.jsonResponse !== null) {
        console.log('JSON response:');
        console.log(JSON.stringify(result.jsonResponse, null, 2));
      } else {
        console.log('Raw response:');
        console.log(result.text.slice(0, 4000));
      }

      if (result.statusCode >= 200 && result.statusCode < 300) {
        console.log('\nSUCCESS: Candidate returned a 2xx response.');
        process.exit(0);
      }
    } catch (error) {
      console.error(`Request failed: ${error.message}`);
    }
  }

  console.error('\nNo candidate invocation pattern succeeded.');
  console.error('Next step: inspect the exact ICA API contract and set ICA_CUSTOM_PAYLOAD if needed.');
  process.exit(4);
}

main().catch((error) => {
  console.error(`Unhandled error: ${error.message}`);
  process.exit(10);
});

// Made with Bob
