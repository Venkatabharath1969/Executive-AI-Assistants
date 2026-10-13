"""Use the Windows-approved proxy for Gemini when no explicit proxy is set."""

import json
import os
import subprocess
import sys
from urllib.parse import urlsplit
from urllib.request import getproxies, proxy_bypass


def configure_system_proxy() -> bool:
    """Resolve Windows PAC settings without elevation or persistent OS changes."""
    if sys.platform != "win32":
        return False
    proxies = getproxies()
    if any(proxies.get(key) for key in ("https", "wss", "all")):
        return False
    host = "generativelanguage.googleapis.com"
    if proxy_bypass(host):
        return False

    command = (
        "$ErrorActionPreference = 'Stop'; "
        "$target = [uri]'https://generativelanguage.googleapis.com/'; "
        "$proxy = [System.Net.WebRequest]::GetSystemWebProxy(); "
        "$resolved = $proxy.GetProxy($target); "
        "if ($resolved -eq $target) { ConvertTo-Json -InputObject '' } "
        "else { ConvertTo-Json -InputObject $resolved.AbsoluteUri }"
    )
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        proxy_url = json.loads(result.stdout.strip())
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        raise RuntimeError(
            "Cannot resolve the Windows network proxy. Ask IT for an approved "
            "HTTPS_PROXY setting, then restart the app."
        ) from exc
    if not isinstance(proxy_url, str):
        raise RuntimeError("Windows returned an invalid network proxy.")
    if not proxy_url:
        return False
    parsed = urlsplit(proxy_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise RuntimeError("Windows returned an unsupported network proxy URL.")

    os.environ["HTTPS_PROXY"] = proxy_url
    os.environ["WSS_PROXY"] = proxy_url
    print("[Network] Using the Windows-configured proxy for HTTPS and Gemini Live.")
    return True
