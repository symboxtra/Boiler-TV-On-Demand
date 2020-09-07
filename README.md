## Purdue Boiler TV On Demand API ##

Caches and tracks movie information from Purdue's [Boiler TV On Demand page](https://boilertvondemand-housing-purdue-edu.swankmp.net).

The cache is refreshed daily by default.

```bash
# Manual ingest
python -m btv_on_demand.ingest

# Scheduled ingest
python -m btv_on_demand

# Custom scheduled ingest
BTV_INGEST_INTERVAL_H=4 python -m btv_on_demand
```
