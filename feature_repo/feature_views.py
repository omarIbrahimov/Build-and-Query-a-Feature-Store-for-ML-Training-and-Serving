from datetime import timedelta
from feast import FeatureView, Field
from feast.types import Float64, Int64
from entities import customer
from sources import customer_history_source
customer_history = FeatureView(
    name='customer_history', entities=[customer], ttl=timedelta(hours=2), online=True,
    schema=[Field(name='txn_count_24h',dtype=Int64),Field(name='amount_sum_24h',dtype=Float64),
            Field(name='amount_mean_24h',dtype=Float64),Field(name='transfer_count_24h',dtype=Int64),
            Field(name='has_history_24h',dtype=Int64),Field(name='snapshot_epoch_seconds',dtype=Int64),
            Field(name='max_source_epoch_seconds',dtype=Int64)],
    source=customer_history_source,
    description='Prior 24 complete hours; hourly refresh includes zero-activity snapshots. Timestamp is simulated availability.'
)
