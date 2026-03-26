from yoyo import step

__depends__ = {
    "0013_series_code"
}

steps = [
    step(
        "ALTER TABLE SERIES ADD COLUMN Plate_Format TEXT",
        "-- SQLite down migration left as no-op",
    ),

    step(
        "UPDATE SERIES SET Plate_Format = 'simple' WHERE Plate_Format IS NULL",
        "UPDATE SERIES SET Plate_Format = NULL WHERE Plate_Format = 'simple'",
    ),

    step(
        "UPDATE SERIES SET Plate_Format = 'subsequence' WHERE Name = 'I - LAKWAR Prepared Slides for Microbiology'",
        "UPDATE SERIES SET Plate_Format = 'simple' WHERE Name = 'I - LAKWAR Prepared Slides for Microbiology'",
    ),

    step(
        "CREATE INDEX IF NOT EXISTS idx_series_plate_format ON SERIES (Plate_Format)",
        "DROP INDEX IF EXISTS idx_series_plate_format",
    ),
]