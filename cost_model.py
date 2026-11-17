"""Tiny cost/margin calculator for the whale options. Edit the numbers, rerun.

    python cost_model.py
    python cost_model.py --price 7500
"""
import argparse

# Current business (from the exercise) - replace with your own estimates / measurements.
BASE_INFRA = 5_400          # EUR/month, shared stack for 300 tenants
DEDICATED_DB = 1_200
DEDICATED_APP = 1_500
SLA_EXTRAS = 600            # backup, DR, monitoring for 99.9%
SCALE_SHARED = 2_500        # scale shared cluster to survive their peak
OPS_SEPARATE_STACK = 1_000  # engineering time to operate a separate stack

OPTIONS = {
    "A shared stack":           SCALE_SHARED + SLA_EXTRAS,
    "B dedicated DB":           DEDICATED_DB + SLA_EXTRAS + OPS_SEPARATE_STACK // 2,
    "C fully dedicated stack":  DEDICATED_DB + DEDICATED_APP + SLA_EXTRAS + OPS_SEPARATE_STACK,
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--price", type=float, default=6_000, help="EUR/month charged to the whale")
    price = ap.parse_args().price
    print(f"Price: EUR {price:,.0f}/month\n")
    print(f"{'option':<26}{'extra cost':>12}{'margin EUR':>12}{'margin %':>10}")
    for name, cost in OPTIONS.items():
        print(f"{name:<26}{cost:>12,.0f}{price - cost:>12,.0f}{(price - cost) / price:>10.0%}")
