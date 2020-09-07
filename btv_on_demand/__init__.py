from .utils import get_env_override

INTERVAL_H = float(get_env_override('BTV_INGEST_INTERVAL_H', '24'))