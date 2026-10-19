#!/usr/bin/env sh
# Print Blobstream's current lag behind Celestia and whether it looks like a stalled relayer.
# Needs: curl, jq
set -eu

URL="https://aerisvalidator.space/bridge/api/bridge_monitor.json"

curl -fsS "$URL" | jq -r '
  .blobstream as $b
  | .blobstream_lag_analysis as $a
  | "relayed to Ethereum: \($b.relayed_celestia_height)",
    "Celestia now:        \($b.live_celestia_height)",
    "lag:                 \($b.lag_blocks) blocks (~\($b.lag_estimated_hours) h)",
    "growth:              \($a.growth_rate_blocks_per_hour) blocks/h over \($a.window_days) days",
    "verdict:             \(if $a.looks_like_total_relay_stall then "relayer stalled (nothing posted)" else "relaying" end)"
'
