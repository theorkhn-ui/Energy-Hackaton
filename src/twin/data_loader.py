"""Load Enerparc plant data (schema per the Dataset Information Slides).

Expected inputs (folder '1. Main-monitoring-data' + '2. Additional Data' + '3. Errorcodes'):
- main_monitoring_data.{csv,parquet,xlsb} — wide table, columns like:
    'INV 01.01.001 / P_AC (kW)', 'INV 01.01.001 / I_DC_SUM (A)', 'INV 01.01.001 / U_DC (V)',
    'Plant / Irradiation_average (W/m²)', 'Plant / Altitude (°)',
    'DRD11A / DV (%)', 'DRD11A / EVU (%)', 'Temperature Sensor / Ambient (°C)', ...
- System_Overview.xlsx — module type + installed kWp per inverter
- Tickets.xlsx — service tickets
- errorcodes_description.xlsx + errorcodes.* — error log + translation table

Column names WILL differ slightly in the real data — fix the regexes here first.
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

INV_PAC_RE = re.compile(r"INV\s*([\d.]+)\s*/\s*P_AC", re.IGNORECASE)
IRRAD_RE = re.compile(r"Irradiation", re.IGNORECASE)
ALTITUDE_RE = re.compile(r"Altitude", re.IGNORECASE)
CURTAIL_RE = re.compile(r"/\s*(DV|EVU)\b", re.IGNORECASE)


def load_monitoring(path: str | Path) -> pd.DataFrame:
    """Load main monitoring file (csv or parquet), datetime-indexed."""
    path = Path(path)
    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path, low_memory=False)
    # find the timestamp column
    ts_col = next((c for c in df.columns
                   if c.lower() in ("timestamp", "datetime", "time", "date")
                   or "time" in c.lower()), df.columns[0])
    df[ts_col] = pd.to_datetime(df[ts_col])
    return df.set_index(ts_col).sort_index()


def get_pac(df: pd.DataFrame) -> pd.DataFrame:
    """Wide frame of inverter AC power, columns = inverter ids ('01.01.001')."""
    cols = {c: m.group(1) for c in df.columns if (m := INV_PAC_RE.search(str(c)))}
    out = df[list(cols)].rename(columns=cols).apply(pd.to_numeric, errors="coerce")
    return out


def get_irradiation(df: pd.DataFrame) -> pd.Series:
    col = next(c for c in df.columns if IRRAD_RE.search(str(c)))
    return pd.to_numeric(df[col], errors="coerce")


def get_sun_altitude(df: pd.DataFrame) -> pd.Series | None:
    col = next((c for c in df.columns if ALTITUDE_RE.search(str(c))), None)
    return pd.to_numeric(df[col], errors="coerce") if col else None


def get_curtailment(df: pd.DataFrame) -> pd.DataFrame:
    """DV / EVU curtailment signals (%, plant-level). Critical: curtailment
    moments are indistinguishable from outages without these."""
    cols = [c for c in df.columns if CURTAIL_RE.search(str(c))]
    return df[cols].apply(pd.to_numeric, errors="coerce") if cols else pd.DataFrame(index=df.index)


def load_system_overview(path: str | Path) -> pd.DataFrame:
    """inverter id -> installed kWp, module type."""
    return pd.read_excel(path)


def load_tickets(path: str | Path) -> pd.DataFrame:
    xl = pd.ExcelFile(path)
    frames = [xl.parse(s).assign(sheet=s) for s in xl.sheet_names]
    return pd.concat(frames, ignore_index=True)


def daylight_mask(df: pd.DataFrame, min_irrad: float = 50.0,
                  min_altitude: float = 5.0) -> pd.Series:
    """Filter to timestamps with meaningful production potential."""
    mask = get_irradiation(df) >= min_irrad
    alt = get_sun_altitude(df)
    if alt is not None:
        mask &= alt >= min_altitude
    return mask
