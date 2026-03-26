from yoyo import step

__depends__ = {
    "0009_plate_view"
}

steps = [
    step(
        "ALTER TABLE LOCATION ADD COLUMN Latitude REAL",
        "ALTER TABLE LOCATION_new RENAME TO LOCATION"
    ),
    step(
        "ALTER TABLE LOCATION ADD COLUMN Longitude REAL",
        "DROP TABLE LOCATION"
    ),
    step(
        "SELECT 1",
        "INSERT INTO LOCATION_new (Id, Name, Grid_Reference) "
        "SELECT Id, Name, Grid_Reference FROM LOCATION"
    ),
    step(
        "SELECT 1",
        """
        CREATE TABLE LOCATION_new (
            Id             INTEGER PRIMARY KEY AUTOINCREMENT,
            Name           TEXT    NOT NULL UNIQUE,
            Grid_Reference TEXT    NULL
        )
        """
    ),
]