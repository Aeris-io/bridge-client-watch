# `bridge_monitor.json` reference

```
GET https://aerisvalidator.space/bridge/api/bridge_monitor.json
```

One static JSON file, rebuilt about every 30 minutes. No authentication, no rate limit on Aeris's side. Schema id: `aeris.celestia.bridge_monitor.v2`.

Units: TIA amounts are in **utia** (1 TIA = 1 000 000 utia). Timestamps are ISO 8601 in UTC.

## Top level

| Field | Type | Description |
|---|---|---|
| `schema` | string | `aeris.celestia.bridge_monitor.v2` |
| `updated_at_utc` | string | When this file was built |
| `sources` | object | Plain-text description of every upstream endpoint used |
| `ibc` | object | IBC light clients and transfer channels, see [below](#ibc) |
| `blobstream` | object | Current Blobstream state, see [below](#blobstream) |
| `blobstream_lag_baseline` | object | Min / max / average lag over the monitor's own history |
| `blobstream_lag_history` | array | One point per sample: `ts_utc`, `lag_blocks`, `lag_hours` |
| `blobstream_lag_analysis` | object | Shape of the lag over time, see [below](#blobstream_lag_analysis) |
| `blobstream_relay_events` | array | Relay transactions found on the contract in the scanned range |
| `blobstream_relay_scan` | object | Ethereum block range that was scanned: `scanned_from_block`, `scanned_to_block` |
| `blobstream_relay_cost` | object | Average gas cost and blocks covered per relay, from real past relays |
| `recent_transfers` | array | Latest outgoing IBC transfers of TIA |
| `transfer_stats_by_chain` | object | Transfer counts and volume per counterparty chain |
| `recent_events` | array | Risk-level transitions, newest first |
| `collection_stats` | object | How long the build took and how many live calls it made |
| `note` | string | How risk is defined |

## `ibc`

| Field | Type | Description |
|---|---|---|
| `total_clients` | int | IBC light clients Celestia has open |
| `total_chains` | int | Distinct counterparty chains |
| `risk_counts_by_client` | object | `{healthy, watch, critical, frozen, expired}` counted per client |
| `risk_counts_by_chain` | object | The same, counted per chain by its best client |
| `chains_with_live_transfer_channel` | int | Chains with an open ICS-20 transfer channel |
| `total_escrowed_utia_network` | int | utia held in all transfer escrow accounts |
| `chains` | array | One entry per counterparty chain |

### `ibc.chains[]`

| Field | Type | Description |
|---|---|---|
| `chain_id` | string | Counterparty chain id, e.g. `osmosis-1` |
| `pretty_name` | string | Display name from the Cosmos chain registry |
| `logo` | string | Logo URL from the chain registry |
| `client_count` | int | Clients pointing at this chain |
| `stale_client_count` | int | Of those, how many are abandoned |
| `primary_risk` | string | Risk level of the best client: `healthy`, `watch`, `critical`, `frozen` or `expired` |
| `healthiest_client` | object | The best client, same shape as `clients[]` |
| `clients` | array | Every client for this chain |
| `transfer_channel_count` | int | Open transfer channels |
| `transfer_channels` | array | Channel id, client id, counterparty channel, escrow address and balance |
| `total_escrowed_utia` | int | utia escrowed across this chain's channels |
| `last_update_tx` | object \| null | The latest `update_client` transaction, if found |

### Client object

| Field | Type | Description |
|---|---|---|
| `client_id` | string | e.g. `07-tendermint-10` |
| `status` | string | Status as reported by the IBC module |
| `risk` | string | Aeris risk level |
| `trusting_period_s` | number | Trusting period in seconds |
| `last_update_utc` | string | Time of the last header update |
| `seconds_remaining` | int | Time left in the trust window; negative once expired |
| `pct_remaining` | number | Share of the trust window left, in percent; negative once expired |
| `estimated_expiry_utc` | string | `last_update_utc + trusting_period_s` |

## `blobstream`

| Field | Type | Description |
|---|---|---|
| `available` | bool | Whether the contract could be read |
| `contract` | string | SP1Blobstream contract address |
| `contract_chain` | string | `Ethereum mainnet` |
| `relayed_celestia_height` | int | Latest Celestia height the contract has accepted |
| `live_celestia_height` | int | Celestia's current height |
| `lag_blocks` | int | `live − relayed` |
| `lag_estimated_seconds`, `lag_estimated_hours` | number | Lag converted to time |
| `checked_at_utc` | string | When the contract was read |

## `blobstream_lag_analysis`

| Field | Type | Description |
|---|---|---|
| `sample_size`, `window_hours`, `window_days` | number | How much history the analysis covers |
| `growth_rate_blocks_per_hour` | int | Average lag growth |
| `increasing_steps`, `flat_steps`, `decreasing_steps` | int | How sample-to-sample changes are split |
| `never_decreased` | bool | The lag has not gone down once in the window |
| `non_decreasing_streak_hours` | number | How long it has been growing or flat |
| `rate_stability_pct` | number | Hour-to-hour variation of the growth rate |
| `looks_like_total_relay_stall` | bool | `true` when the lag never decreased **and** grows at a steady rate: the relayer has posted nothing, rather than posting slowly |

## `recent_events[]`

| Field | Type | Description |
|---|---|---|
| `ts_utc` | string | When the transition was seen |
| `chain_id` | string | Counterparty chain |
| `client_id` | string | The client whose level changed |
| `event` | string | `risk_change` |
| `severity` | string | How serious the transition is, e.g. `medium` for healthy → expired, `low` for a recovery |
| `risk_from`, `risk_to` | string | Old and new level |
| `detail` | string | Human-readable sentence |
