"""
Utility functions for ISS Module
Includes stardate, Julian date calculations, and market times
"""

from datetime import datetime, timezone
import time


def get_stardate():
    """
    Calculate canonical stardate based on current time
    Using Y2K epoch (January 1, 2000, 00:00:00 UTC)
    AUTHORITY: Spruked - TNG era format revoked
    """
    now = datetime.now(timezone.utc)
    stardate_epoch = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    delta = now - stardate_epoch
    stardate = delta.total_seconds() / 86400.0
    return round(stardate, 4)


def get_julian_date():
    """
    Calculate Julian date from current time
    """
    now = datetime.now(timezone.utc)
    a = (14 - now.month) // 12
    y = now.year + 4800 - a
    m = now.month + 12 * a - 3
    jdn = now.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn + (now.hour - 12) / 24 + now.minute / 1440 + now.second / 86400


def get_market_times():
    """
    Get current market session information
    """
    now = datetime.now(timezone.utc)
    market_sessions = {
        'tokyo': {'open': 0, 'close': 9},  # UTC hours
        'london': {'open': 8, 'close': 17},
        'new_york': {'open': 14, 'close': 21}
    }
    
    current_hour = now.hour
    active_markets = []
    
    for market, times in market_sessions.items():
        if times['open'] <= current_hour < times['close']:
            active_markets.append(market)
    
    return {
        'current_utc': now.isoformat(),
        'active_markets': active_markets,
        'all_sessions': market_sessions
    }


def format_timestamp(dt=None, format_type='iso'):
    """
    Format timestamp in various formats
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    formats = {
        'iso': dt.isoformat(),
        'stardate': f"Stardate {get_stardate()}",
        'julian': f"JD {get_julian_date():.6f}",
        'human': dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    }
    
    return formats.get(format_type, formats['iso'])


def get_iss_timestamp():
    """
    Get ISS timestamp data in canonical format
    AUTHORITY: Spruked - Official DALS/UCM Stardate Protocol
    """
    now = datetime.now(timezone.utc)
    timestamp_iso = now.isoformat().replace('+00:00', 'Z')
    timestamp_epoch = int(now.timestamp())
    
    # Julian date calculation
    julian_epoch = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
    timestamp_julian = 2451545.0 + (now - julian_epoch).total_seconds() / 86400.0
    
    # Canonical stardate (Y2K epoch)
    stardate_epoch = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    delta = now - stardate_epoch
    stardate_iss = round(delta.total_seconds() / 86400.0, 4)

    return {
        "timestamp_iso": timestamp_iso,
        "timestamp_epoch": timestamp_epoch,
        "timestamp_julian": round(timestamp_julian, 6),
        "stardate_iss": stardate_iss
    }


def current_timecodes():
    """
    Get all current time representations for anchoring
    Perfect for Caleon symbolic cognition and CertSig timestamp anchoring
    UPDATED: Uses canonical stardate (Y2K epoch)
    """
    now = datetime.now(timezone.utc)
    
    return {
        'iso_timestamp': now.isoformat(),
        'stardate': get_stardate(),
        'julian_date': get_julian_date(),
        'unix_timestamp': int(now.timestamp()),
        'human_readable': now.strftime('%Y-%m-%d %H:%M:%S UTC'),
        'market_info': get_market_times(),
        'anchor_hash': _generate_time_anchor_hash(now)
    }


def _generate_time_anchor_hash(dt):
    """Generate a unique hash for time anchoring"""
    import hashlib
    
    # Combine multiple time representations for unique anchoring
    anchor_string = f"{dt.isoformat()}-{get_stardate()}-{get_julian_date()}"
    return hashlib.sha256(anchor_string.encode()).hexdigest()[:16]


def ensure_folder(folder_path: str) -> str:
    """
    Ensure a folder exists, create if it doesn't
    Returns the absolute path to the folder
    """
    import os
    folder_path = os.path.abspath(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path