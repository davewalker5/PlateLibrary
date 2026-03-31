from yoyo import step

__depends__ = {
    "0018_multiple_plate_stains_view"
}

steps = [
    step(
        """
        ALTER TABLE LOCATION
        ADD COLUMN Coordinate_System TEXT NOT NULL DEFAULT 'BNG'
        """,
        """
        -- SQLite does not support DROP COLUMN directly.
        -- Recreate table without Coordinate_System.

        CREATE TABLE LOCATION_new (
            Id             INTEGER PRIMARY KEY AUTOINCREMENT,
            Name           TEXT    NOT NULL UNIQUE,
            Grid_Reference TEXT    NULL,
            Latitude       REAL,
            Longitude      REAL
        );

        INSERT INTO LOCATION_new (Id, Name, Grid_Reference, Latitude, Longitude)
        SELECT Id, Name, Grid_Reference, Latitude, Longitude
        FROM LOCATION;

        DROP TABLE LOCATION;

        ALTER TABLE LOCATION_new RENAME TO LOCATION;
        """
    ),
]