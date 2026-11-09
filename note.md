# PaySim feature store

## Data — STEP 2–4

We checked the full dataset before selecting customers.

| Check | Result |
|---|---:|
| Transactions | 6,362,620 |
| Unique senders | 6,353,307 |
| Senders with one transaction | 99.85% |
| Missing sender or recipient IDs | 0 |
| Invalid times, amounts or labels | 0 |
| Negative amounts | 0 |
| Zero amounts | 16 |
| Identical complete duplicate rows | 0 |

We kept valid zero amounts. Duplicate-looking rows would not automatically be deleted because the dataset has no authoritative transaction ID.

We selected 400 customers using a fixed MD5 ordering and another 100 with activity in different hours. All their transactions were retained: **500 customers, 600 transactions**. The active group is for demonstrating updates and is not representative of the population. Selection does not use fraud labels.

DuckDB scans the large CSV with a 512 MB memory limit. The notebook reuses saved preparation on normal runs. STEP 2 can rebuild it from the ZIP.

Time is `2025-01-01 00:00 UTC + (step − 1) hours`. The date is arbitrary. The actual data covers steps 1–743. We do not invent an order for transactions within an hour.

## Features — STEP 5–7

| Feature | Meaning |
|---|---|
| `txn_count_24h` | Recent transaction count |
| `amount_sum_24h` | Recent total amount |
| `amount_mean_24h` | Recent average amount |
| `transfer_count_24h` | Recent TRANSFER count |
| `has_history_24h` | Whether the window contains any transactions |

At boundary B, the window is **[B − 24 hours, B)**. Current-hour transactions are excluded. Fraud labels and balance fields are not used in calculations.

Unknown customers have missing features. Known customers with empty windows have zero counts. Their mean uses a zero placeholder, identified by `has_history_24h = 0`.

We created **253,830 hourly snapshots**, including zero refreshes after history expires. This costs extra rows but stops old activity remaining online forever.

Two additional fields record the snapshot boundary and latest contributing transaction. These support freshness and leakage checks; they are not model inputs.

## Feast — STEP 8–10

```text
Transactions → hourly features → Parquet → historical training retrieval
                                      ↘ SQLite → online lookup
```

The entity is `customer_id`. Feast registers the Parquet source and customer feature view. Parquet stores history; SQLite serves the latest materialized values.

Snapshot availability is the Feast timestamp. The normal simulation assumes features become available at B with zero delay. A test checks a ten-minute delay. The created timestamp also represents simulated availability, not the date we ran the notebook.

The file backend can collapse repeated customer/time requests or omit requests before the first snapshot. We retrieve unique pairs and left-merge onto the original requests to preserve every transaction.

| Cohort | Requests | Matched snapshots | Nonempty 24-hour history |
|---|---:|---:|---:|
| Random customers | 400 | 0 | 0 |
| Active group | 200 | 100 | 12 |

Most senders have no previous transaction. Many repeats are more than 24 hours apart. The missing and empty histories are expected and checked against raw transactions.

## Validation — STEP 11–14

| Check | Result |
|---|---:|
| Prediction rows checked against raw history | 600 |
| Boundary and leakage checks | 9 passed |
| Raw/offline/online field comparisons | 7,014 |
| Mismatches | 0 |
| Repeated materialization gives identical values | Passed |
| Final known rolling windows become empty | Passed |

The checks cover exact boundaries, same-hour transactions, duplicate prediction requests, shuffled input, future transactions, delayed availability, TTL and unknown customers. Adding a future transaction must not change earlier results.

Consistency is checked at two simulated cutoffs: January 10, 2025 at 21:30 UTC and January 31 at 19:30 UTC. Counts and missing values match exactly. Amounts allow small floating-point rounding differences.

The aggregation window is 24 hours; snapshot TTL is 2 hours. SQLite does not enforce our TTL on lookup, so the notebook rejects stale and future values explicitly. Temporary stores isolate each simulation and are cleaned up at the end.

## Model and limitations — STEP 15–16

The sample contains **no fraud cases**, so we did not train the optional fraud model. A larger sample with both classes and chronological evaluation is needed.

This is a local feature-store demonstration. It does not implement streaming, late-arrival corrections or distributed serving. Hourly refreshes for millions of customer IDs would need a more scalable approach.

## Files

| Path | Purpose |
|---|---|
| `notebooks/feature_store.ipynb` | All preparation, calculations, checks and saved results |
| `feature_repo/` | Feast configuration, entity, source and feature view |
| `data/raw/` | Original ZIP and extracted CSV |
| `data/processed/` | Selected transactions, feature history, training data and cached audit |
| `requirements.txt` | Libraries needed to run the notebook |
| `note.md` | Design choices and results |

Setup instructions are at the top of the notebook. There are no separate helper modules or test scripts.

References: [PaySim](https://www.kaggle.com/datasets/ealaxi/paysim1), [Feast point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins), [SQLite store](https://docs.feast.dev/reference/online-stores/sqlite).
