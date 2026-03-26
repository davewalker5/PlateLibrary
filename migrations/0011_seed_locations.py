from yoyo import step

__depends__ = {
    "0010_location_latitude_longitude"
}

steps = [
    step(
        """
        INSERT INTO LOCATION (Name, Latitude, Longitude, Grid_Reference)
        VALUES ('Abbey Fishponds', 51.6784375886019, -1.26045961101227, 'SU 5123 9800')
        """,
        """
        DELETE FROM LOCATION
        WHERE Name = 'Abbey Fishponds'
        """
    ),
    step(
        """
        INSERT INTO LOCATION (Name, Latitude, Longitude, Grid_Reference)
        VALUES ('Barrow Hill Horse Chestnut', 51.681115673728, -1.25238681241009, 'SU 517 983')
        """,
        """
        DELETE FROM LOCATION
        WHERE Name = 'Barrow Hill Horse Chestnut'
        """
    ),
    step(
        """
        INSERT INTO LOCATION (Name, Latitude, Longitude, Grid_Reference)
        VALUES ('Barton Fields', 51.6713995304867, -1.26539919854532, 'SU 508 972')
        """,
        """
        DELETE FROM LOCATION
        WHERE Name = 'Barton Fields'
        """
    ),
    step(
        """
        INSERT INTO LOCATION (Name, Latitude, Longitude, Grid_Reference)
        VALUES ('Norris Park', 51.6830848462405, -1.26230869582991, 'SU 5109 9851')
        """,
        """
        DELETE FROM LOCATION
        WHERE Name = 'Norris Park'
        """
    ),
    step(
        """
        INSERT INTO LOCATION (Name, Latitude, Longitude, Grid_Reference)
        VALUES ('Sustrans Path Near Thrupp Lake', 51.671796, -1.250316, 'SU 519 972')
        """,
        """
        DELETE FROM LOCATION
        WHERE Name = 'Sustrans Path Near Thrupp Lake'
        """
    ),
    step(
        """
        INSERT INTO LOCATION (Name, Latitude, Longitude, Grid_Reference)
        VALUES ('Thrupp Lake', 51.6718, -1.250316, 'SU 519 972')
        """,
        """
        DELETE FROM LOCATION
        WHERE Name = 'Thrupp Lake'
        """
    ),
]