"""List Celestia's IBC counterparty chains by how much trust window their best client has left.

Usage:  python expiring_clients.py [--all]

Without --all, chains whose best client has already expired are skipped.
Standard library only.
"""
import json
import sys
import urllib.request

URL = "https://aerisvalidator.space/bridge/api/bridge_monitor.json"


def main() -> None:
    show_all = "--all" in sys.argv
    with urllib.request.urlopen(URL, timeout=30) as resp:
        data = json.load(resp)

    rows = []
    for chain in data["ibc"]["chains"]:
        best = chain.get("healthiest_client") or {}
        if not show_all and chain["primary_risk"] == "expired":
            continue
        rows.append((best.get("pct_remaining", 0.0), chain, best))

    rows.sort(key=lambda r: r[0])

    print(f"{'chain':<34} {'risk':<9} {'left':>7}  expires (UTC)")
    for pct, chain, best in rows:
        expiry = (best.get("estimated_expiry_utc") or "")[:16].replace("T", " ")
        print(f"{chain['chain_id']:<34} {chain['primary_risk']:<9} {pct:>6.1f}%  {expiry}")

    print(f"\nsnapshot: {data['updated_at_utc']}")


if __name__ == "__main__":
    main()
