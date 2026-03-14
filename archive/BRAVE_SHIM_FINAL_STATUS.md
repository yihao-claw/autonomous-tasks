# Brave Shim Integration - Final Status Report

**Date:** 2026-02-23 04:15 UTC

## Problem Summary
OpenClaw's `web_search` tool returns "Brave Search API error (422): SUBSCRIPTION_TOKEN_INVALID" instead of connecting to local `brave_shim` running on localhost:8000.

## What Works ✅
1. **brave_shim itself** is fully functional
   - HTTP server on 127.0.0.1:8000 ✓
   - HTTPS server on 127.0.0.1:8443 ✓  
   - Can be accessed directly: `curl http://127.0.0.1:8000/res/v1/web/search?q=test` → returns valid results

2. **Patches applied successfully**
   - OpenClaw code patched to use `http://127.0.0.1:8000/res/v1/web/search`
   - File: `/usr/local/lib/node_modules/openclaw/dist/plugin-sdk/reply-CqKtVq5t.js`
   - Verified with: `grep -c "http://127.0.0.1:8000" /usr/local/lib/node_modules/openclaw/dist/**/*.js`
   - Result: 10 references found ✓

3. **Network redirection attempts**
   - /etc/hosts modified: `127.0.0.1 api.search.brave.com` ✓
   - NODE_TLS_REJECT_UNAUTHORIZED=0 set ✓
   - HTTP/HTTPS interceptor modules created ✓

## What Doesn't Work ❌
- brave_shim receives **ZERO requests** from OpenClaw
- web_search still tries to use real Brave API (hence the 422 error)
- All interception attempts failed

## Hypothesis
OpenClaw's `web_search` tool might be:
1. Implemented directly in Anthropic SDK (not patched)
2. Using a built-in binary or compiled module
3. Loaded through a different code path than expected
4. Using a hardcoded endpoint that bypasses patches

## Current Setup
- brave_shim: Running on HTTP:8000 + HTTPS:8443
- /etc/hosts: api.search.brave.com → 127.0.0.1
- NODE_OPTIONS: brave-shim-final.js interceptor loaded
- Patches: Applied to all openclaw dist files
- Certificates: Self-signed certs ready at /opt/brave_shim/certs/

## Next Steps Required
**User input needed:** How did you previously get brave_shim working with OpenClaw? What was the exact configuration or command?

## Files Modified
- /etc/hosts
- /opt/brave_shim/brave_shim.py (added HTTPS support)
- /usr/local/lib/node_modules/openclaw/dist/**/*.js (patched Brave API URLs)
- ~/.openclaw/openclaw.json (added tools.web configuration)
- /home/node/.openclaw/.env (environment variables)

## Environment Variables Set
```bash
NODE_OPTIONS="--require /usr/local/lib/node_modules/openclaw/dist/brave-shim-final.js"
NODE_TLS_REJECT_UNAUTHORIZED=0
BRAVE_API_KEY=shim
BRAVE_API_ENDPOINT=http://127.0.0.1:8000
```
