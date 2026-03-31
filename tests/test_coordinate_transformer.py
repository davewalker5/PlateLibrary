import pytest

from plate_library.utils.coordinate_transformer import (
    CoordinateTransformResult,
    latitude_longitude_to_os_gridref,
    latitude_longitude_to_utm,
    latitude_longitude_to_mgrs,
    latitude_longitude_to_reference,
    transform_coordinates,
)


# A known-good test point near Oxfordshire
TEST_LAT = 51.68265573758483
TEST_LON = -1.25930284959462

EXPECTED_BNG_8 = "SU 5130 9846"
EXPECTED_UTM = "30U 620339 5727178"
EXPECTED_MGRS = "30UXC2033827177"


# -----------------------------------------------------------------------------
# British National Grid
# -----------------------------------------------------------------------------
def test_latitude_longitude_to_os_gridref_known_value():
    result = latitude_longitude_to_os_gridref(TEST_LAT, TEST_LON, digits=8)
    assert result == EXPECTED_BNG_8


@pytest.mark.parametrize(
    "digits,expected",
    [
        (6, "SU 513 984"),
        (8, "SU 5130 9846"),
        (10, "SU 51305 98469"),
    ],
)
def test_latitude_longitude_to_os_gridref_precisions(digits, expected):
    result = latitude_longitude_to_os_gridref(TEST_LAT, TEST_LON, digits=digits)
    assert result == expected


@pytest.mark.parametrize("digits", [0, 4, 7, 12])
def test_latitude_longitude_to_os_gridref_rejects_invalid_digits(digits):
    with pytest.raises(ValueError, match="digits"):
        latitude_longitude_to_os_gridref(TEST_LAT, TEST_LON, digits=digits)


# -----------------------------------------------------------------------------
# UTM
# -----------------------------------------------------------------------------
def test_latitude_longitude_to_utm_known_value():
    result = latitude_longitude_to_utm(TEST_LAT, TEST_LON)
    assert result == EXPECTED_UTM


def test_latitude_longitude_to_utm_without_band():
    result = latitude_longitude_to_utm(TEST_LAT, TEST_LON, include_band=False)
    assert result == "30 620339 5727178"


def test_latitude_longitude_to_utm_with_precision():
    result = latitude_longitude_to_utm(TEST_LAT, TEST_LON, precision=2)
    assert result == "30U 620338.69 5727177.66"


def test_latitude_longitude_to_utm_rejects_polar_out_of_range():
    with pytest.raises(ValueError, match="UTM is only defined"):
        latitude_longitude_to_utm(85.0, 0.0)


# -----------------------------------------------------------------------------
# MGRS
# -----------------------------------------------------------------------------
def test_latitude_longitude_to_mgrs_known_value():
    pytest.importorskip("mgrs")
    result = latitude_longitude_to_mgrs(TEST_LAT, TEST_LON, precision=5)
    assert result == EXPECTED_MGRS


@pytest.mark.parametrize(
    "precision,expected",
    [
        (5, "30UXC2033827177"),
        (4, "30UXC20332717"),
        (3, "30UXC203271"),
        (2, "30UXC2027"),
        (1, "30UXC22"),
        (0, "30UXC"),
    ],
)
def test_latitude_longitude_to_mgrs_precisions(precision, expected):
    pytest.importorskip("mgrs")
    result = latitude_longitude_to_mgrs(TEST_LAT, TEST_LON, precision=precision)
    assert result == expected


@pytest.mark.parametrize("precision", [-1, 6, 99])
def test_latitude_longitude_to_mgrs_rejects_invalid_precision(precision):
    pytest.importorskip("mgrs")
    with pytest.raises(ValueError, match="precision"):
        latitude_longitude_to_mgrs(TEST_LAT, TEST_LON, precision=precision)


# -----------------------------------------------------------------------------
# Generic dispatch
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "system,expected",
    [
        ("BNG", EXPECTED_BNG_8),
        ("UTM", EXPECTED_UTM),
    ],
)
def test_latitude_longitude_to_reference_dispatch(system, expected):
    result = latitude_longitude_to_reference(TEST_LAT, TEST_LON, system=system)
    assert result == expected


def test_latitude_longitude_to_reference_dispatch_mgrs():
    pytest.importorskip("mgrs")
    result = latitude_longitude_to_reference(TEST_LAT, TEST_LON, system="MGRS")
    assert result == EXPECTED_MGRS


def test_latitude_longitude_to_reference_accepts_lowercase_system():
    result = latitude_longitude_to_reference(TEST_LAT, TEST_LON, system="utm")
    assert result == EXPECTED_UTM


def test_latitude_longitude_to_reference_rejects_unknown_system():
    with pytest.raises(ValueError, match="Unsupported coordinate system"):
        latitude_longitude_to_reference(TEST_LAT, TEST_LON, system="EPSG27700")


# -----------------------------------------------------------------------------
# Result wrapper
# -----------------------------------------------------------------------------
def test_transform_coordinates_returns_result_object():
    result = transform_coordinates(TEST_LAT, TEST_LON, system="BNG")

    assert isinstance(result, CoordinateTransformResult)
    assert result.system == "BNG"
    assert result.value == EXPECTED_BNG_8


def test_transform_coordinates_returns_utm_result():
    result = transform_coordinates(TEST_LAT, TEST_LON, system="UTM")

    assert result.system == "UTM"
    assert result.value == EXPECTED_UTM


def test_transform_coordinates_returns_mgrs_result():
    pytest.importorskip("mgrs")
    result = transform_coordinates(TEST_LAT, TEST_LON, system="MGRS")

    assert result.system == "MGRS"
    assert result.value == EXPECTED_MGRS


# -----------------------------------------------------------------------------
# Latitude / longitude validation
# -----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (91.0, 0.0),
        (-91.0, 0.0),
        (0.0, 181.0),
        (0.0, -181.0),
    ],
)
def test_invalid_latitude_longitude_rejected_by_bng(latitude, longitude):
    with pytest.raises(ValueError):
        latitude_longitude_to_os_gridref(latitude, longitude)


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (91.0, 0.0),
        (-91.0, 0.0),
        (0.0, 181.0),
        (0.0, -181.0),
    ],
)
def test_invalid_latitude_longitude_rejected_by_utm(latitude, longitude):
    with pytest.raises(ValueError):
        latitude_longitude_to_utm(latitude, longitude)


@pytest.mark.parametrize(
    "latitude,longitude",
    [
        (91.0, 0.0),
        (-91.0, 0.0),
        (0.0, 181.0),
        (0.0, -181.0),
    ],
)
def test_invalid_latitude_longitude_rejected_by_transform_wrapper(latitude, longitude):
    with pytest.raises(ValueError):
        transform_coordinates(latitude, longitude, system="BNG")
