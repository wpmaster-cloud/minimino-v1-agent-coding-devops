---
name: vpn_proxy
description: "All outbound web traffic is automatically routed through a VPN proxy for IP rotation and anonymity."
---

# VPN Proxy

All outbound HTTP/HTTPS traffic from this agent is automatically routed through a VPN proxy. No special flags or configuration needed — `curl`, `python requests`, `wget`, etc. all go through the VPN.

**Excluded from proxy** (goes direct):
- LLM API calls (NIM/NVIDIA)
- Internal k8s services (Redis, MCP servers)

## Verify

Check your VPN IP:
```bash
curl -s https://api.ipify.org
```

This should show a VPN IP, not the server's direct IP.

## Bypass proxy for a specific request

If you need to skip the proxy for a specific call:
```bash
curl -s --noproxy '*' https://example.com
```

Or in Python:
```python
requests.get("https://example.com", proxies={"http": None, "https": None})
```
