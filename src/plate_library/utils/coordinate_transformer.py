from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from pyproj import CRS, Transformer
import mgrs as mgrs_lib


CoordinateSystem = Literal["BNG", "UTM", "MGRS"]


# -----------------------------------------------------------------------------
# CRS / transformer helpers
# -----------------------------------------------------------------------------
WGS84 = CRS.from_epsg(4326)
BNG = CRS.from_epsg(27700)

_bng_transformer = Transformer.from_crs(WGS84, BNG, always_xy=True)


# -----------------------------------------------------------------------------
# Result container
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class CoordinateTransformResult:
    system: CoordinateSystem
    value: str


# -----------------------------------------------------------------------------
# Generic helpers
# -----------------------------------------------------------------------------
def _validate_latitude_longitude(latitude: float, longitude: float) -> None:
    """Validate latitude/longitude ranges."""
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude {latitude} is out of range (-90 to 90)")
    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude {longitude} is out of range (-180 to 180)")


# -----------------------------------------------------------------------------
# British National Grid helpers
# -----------------------------------------------------------------------------
def _easting_northing_to_os_gridref(easting: float, northing: float, digits: int) -> str:
    """
    Convert British National Grid Easting/Northing to an OS grid reference.

    :param easting: National Grid Easting
    :param northing: National Grid Northing
    :param digits: Total numeric digits in the returned grid reference
                   (6, 8, or 10)
    :return: OS grid reference, e.g. "SP 510 065"
    """
    if digits not in (6, 8, 10):
        raise ValueError("OS grid reference digits must be one of: 6, 8, 10")

    if easting < 0 or easting >= 700000:
        raise ValueError(f"Easting {easting} is out of the OS National Grid bounds")

    if northing < 0 or northing >= 1300000:
        raise ValueError(f"Northing {northing} is out of the OS National Grid bounds")

    easting_100k = int(math.floor(easting / 100000))
    northing_100k = int(math.floor(northing / 100000))

    # No "I" in the OS lettering scheme
    letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"

    letter_1 = (19 - northing_100k) - ((19 - northing_100k) % 5) + ((easting_100k + 10) // 5)
    letter_2 = ((19 - northing_100k) * 5 % 25) + (easting_100k % 5)
    letter_pair = letters[letter_1] + letters[letter_2]

    e_remainder = int(math.floor(easting)) % 100000
    n_remainder = int(math.floor(northing)) % 100000

    keep = digits // 2
    factor = 10 ** (5 - keep)

    e_str = str(e_remainder // factor).zfill(keep)
    n_str = str(n_remainder // factor).zfill(keep)

    return f"{letter_pair} {e_str} {n_str}"


def latitude_longitude_to_os_gridref(latitude: float, longitude: float, digits: int = 8) -> str:
    """
    Convert latitude/longitude (WGS84) to British National Grid reference.

    Backward-compatible convenience wrapper.
    """
    _validate_latitude_longitude(latitude, longitude)
    easting, northing = _bng_transformer.transform(longitude, latitude)
    return _easting_northing_to_os_gridref(easting, northing, digits=digits)


# -----------------------------------------------------------------------------
# UTM helpers
# -----------------------------------------------------------------------------
def _utm_zone_number(longitude: float) -> int:
    """Return the UTM longitudinal zone number (1-60)."""
    return int((longitude + 180) // 6) + 1


def _utm_zone_letter(latitude: float) -> str:
    """
    Return the UTM latitude band letter.

    Valid for latitudes between 80°S and 84°N.
    """
    if latitude < -80 or latitude > 84:
        raise ValueError("UTM is only defined between 80°S and 84°N")

    bands = "CDEFGHJKLMNPQRSTUVWX"
    index = int((latitude + 80) // 8)

    # X is repeated for the 72-84 band
    if index > 19:
        index = 19

    return bands[index]


def latitude_longitude_to_utm(
    latitude: float,
    longitude: float,
    include_band: bool = True,
    precision: int = 0,
) -> str:
    """
    Convert latitude/longitude (WGS84) to UTM.

    :param latitude: WGS84 latitude
    :param longitude: WGS84 longitude
    :param include_band: Whether to include latitude band letter
    :param precision: Decimal places for easting/northing
    :return: e.g. "30U 699375 5713975"
    """
    _validate_latitude_longitude(latitude, longitude)

    if latitude < -80 or latitude > 84:
        raise ValueError("UTM is only defined between 80°S and 84°N")

    zone_number = _utm_zone_number(longitude)
    zone_letter = _utm_zone_letter(latitude)

    epsg = 32600 + zone_number if latitude >= 0 else 32700 + zone_number
    utm_crs = CRS.from_epsg(epsg)
    transformer = Transformer.from_crs(WGS84, utm_crs, always_xy=True)

    easting, northing = transformer.transform(longitude, latitude)

    easting_str = f"{easting:.{precision}f}"
    northing_str = f"{northing:.{precision}f}"

    if include_band:
        return f"{zone_number}{zone_letter} {easting_str} {northing_str}"
    return f"{zone_number} {easting_str} {northing_str}"


# -----------------------------------------------------------------------------
# MGRS helpers
# -----------------------------------------------------------------------------
def latitude_longitude_to_mgrs(latitude: float, longitude: float, precision: int = 5) -> str:
    """
    Convert latitude/longitude (WGS84) to MGRS.

    :param latitude: WGS84 latitude
    :param longitude: WGS84 longitude
    :param precision: MGRS precision, 0-5
                      5 = 1m precision
                      4 = 10m precision
                      3 = 100m precision
    :return: e.g. "30UWB9937513975"
    """
    _validate_latitude_longitude(latitude, longitude)

    if precision not in (0, 1, 2, 3, 4, 5):
        raise ValueError("MGRS precision must be between 0 and 5")

    converter = mgrs_lib.MGRS()
    mgrs_value = converter.toMGRS(latitude, longitude, MGRSPrecision=precision)

    if isinstance(mgrs_value, bytes):
        mgrs_value = mgrs_value.decode("ascii")

    return mgrs_value


# -----------------------------------------------------------------------------
# Generic public API
# -----------------------------------------------------------------------------
def latitude_longitude_to_reference(
    latitude: float,
    longitude: float,
    system: CoordinateSystem = "BNG",
    *,
    os_digits: int = 8,
    utm_include_band: bool = True,
    utm_precision: int = 0,
    mgrs_precision: int = 5,
) -> str:
    """
    Convert latitude/longitude to the requested coordinate reference format.

    Supported systems:
    - BNG  : British National Grid
    - UTM  : Universal Transverse Mercator
    - MGRS : Military Grid Reference System
    """
    system = system.upper()

    if system == "BNG":
        return latitude_longitude_to_os_gridref(latitude, longitude, digits=os_digits)

    if system == "UTM":
        return latitude_longitude_to_utm(
            latitude,
            longitude,
            include_band=utm_include_band,
            precision=utm_precision,
        )

    if system == "MGRS":
        return latitude_longitude_to_mgrs(
            latitude,
            longitude,
            precision=mgrs_precision,
        )

    raise ValueError(f"Unsupported coordinate system: {system}")


def transform_coordinates(
    latitude: float,
    longitude: float,
    system: CoordinateSystem = "BNG",
    *,
    os_digits: int = 8,
    utm_include_band: bool = True,
    utm_precision: int = 0,
    mgrs_precision: int = 5,
) -> CoordinateTransformResult:
    """
    Convenience wrapper returning both the target system and the transformed value.
    """
    value = latitude_longitude_to_reference(
        latitude,
        longitude,
        system=system,
        os_digits=os_digits,
        utm_include_band=utm_include_band,
        utm_precision=utm_precision,
        mgrs_precision=mgrs_precision,
    )
    return CoordinateTransformResult(system=system.upper(), value=value)
