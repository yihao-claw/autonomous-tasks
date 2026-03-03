# Brave Shim Integration Debugging Report

## Problem
OpenClaw's `web_search` tool returns "SUBSCRIPTION_TOKEN_INVALID (422)" error from real Brave API, not from local shim.

## Evidence
1. ✅ brave_shim running on http://127.0.0.1:8000
   - Status check: `curl -s http://127.0.0.1:8000/status` → returns `{"status":"online"}`
   - Direct search works: `curl -G http://127.0.0.1:8000/res/v1/web/search?q=test` → returns valid results

2. ❌ brave_shim receives NO requests from OpenClaw
   - Monitoring `/opt/brave_shim/log/brave_shim.log`
   - After calling `web_search`, no new log entries
   - Therefore: OpenClaw is NOT calling local shim

3. ✅ Patch applied correctly
   - Files modified: `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/reply-*.js`
   - `BRAVE_SEARCH_ENDPOINT = "http://127.0.0.1:8000/res/v1/web/search"` ✓

## Hypothesis
OpenClaw uses a different code path for web_search that:
- Doesn't go through the patched JS files
- OR loads code differently (bundled, compiled, etc.)
- OR has a different initialization sequence

## Next Steps Needed
1. Find the actual entry point for web_search tool execution
2. Trace how OpenClaw initializes and calls tools
3. Either:
   - Patch the actual code being executed, OR
   - Configure OpenClaw to use a custom Brave endpoint, OR
   - Use a MITM proxy to intercept HTTPS → HTTP conversion
