from pathlib import Path
from feast import FileSource
customer_history_source = FileSource(
    name='customer_hourly_parquet',
    path=str(Path(__file__).resolve().parents[1] / 'data/processed/customer_hourly.parquet'),
    timestamp_field='event_timestamp',
    created_timestamp_column='created_timestamp',
)
