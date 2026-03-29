---
name: get_your_ip
description: "Check your public IP address to verify VPN/proxy connectivity."
---

# Get Your IP

Run this to see your current public IP:

```bash
curl -s https://api.ipify.org
```

If VPN is enabled, this should show a VPN IP (not the server's direct IP).
