from pyproj import Transformer
import math


# The transformer is a Python wrapper for the PROJ cartographic projection library
# EPSG:4326 specifies the source as the WGS84 latitude/longitude GPS coordinates
# EPSG:27700 specifies the target as OSGB36 / British National Grid easting/northing coordinates
_transformer = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)


def _easting_northing_to_os_gridref(easting, northing, digits):
    """
    Convert British National Grid Easting/Northing to OS grid reference

    :param easting: National grid Easting
    :param northign: National grid northing
    :param digits: Number of digits in the returned grid reference
    :return: OS grid reference
    """
    if digits not in (6, 8, 10):
        raise ValueError("Invalid grid reference digits")
    
    if easting < 0 or easting >= 700000:
        raise ValueError(f"Easting {easting} is out of the OS National Grid bounds")

    if northing < 0 or northing >= 1300000:
        raise ValueError(f"Northing {northing} is out of the OS National Grid bounds")

    # Determine which 100km square of the grid the coordinate lies in
    easting_100k = int(math.floor(easting / 100000))
    northing_100k = int(math.floor(northing / 100000))

    # The 25-character alphabet used by the OS - note that there is no "I" in thecharacter set
    letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"

    # Calculate the letter pair. Conceptually, there is a 500km supergrid providing
    # the first letter:
    #
    # S  T
    # N  O
    # H  J
    #
    # And a 100km square inside each of the above:
    #
    # A B C D E
    # F G H J K
    # L M N O P
    # Q R S T U
    # V W X Y Z

    letter_1 = (19 - northing_100k) - ((19 - northing_100k) % 5) + ((easting_100k + 10) // 5)
    letter_2 = ((19 - northing_100k) * 5 % 25) + (easting_100k % 5)
    letter_pair = letters[letter_1] + letters[letter_2]

    # Calculate the remainders within 100km square. For example, if the easting were 451234,
    # this yields 51234 m East inside the identified square
    e_remainder = int(math.floor(easting)) % 100000
    n_remainder = int(math.floor(northing)) % 100000

    # Grid references don't show full m precision so calculate a factor that can be used
    # to reduce the metre precision to the desired number of digits. For example, a 6-digit
    # grid reference retains 3 digits in each of East and North
    keep = digits // 2
    factor = 10 ** (5 - keep)

    e_str = str(e_remainder // factor).zfill(keep)
    n_str = str(n_remainder // factor).zfill(keep)

    return f"{letter_pair} {e_str} {n_str}"


def latitude_longitude_to_os_gridref(latitude, longitude, digits):
    """
    Convert a latitude and longitude to an OS grid reference

    :param latitude: National grid Easting
    :param longitude: National grid northing
    :param digits: Number of digits in the returned grid reference
    :return: OS grid reference
    """
    easting, northing = _transformer.transform(longitude, latitude)
    return _easting_northing_to_os_gridref(easting, northing, digits=digits)
