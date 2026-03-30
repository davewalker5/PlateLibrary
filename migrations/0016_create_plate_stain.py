from yoyo import step

__depends__ = {
    "0015_add_stain_to_view"
}

steps = [
    step(
        """
        CREATE TABLE PLATE_STAIN (
            Id       INTEGER PRIMARY KEY AUTOINCREMENT,
            Plate_Id INTEGER NOT NULL,
            Stain_Id INTEGER NOT NULL,
            FOREIGN KEY (Plate_Id) REFERENCES PLATE (Id),
            FOREIGN KEY (Stain_Id) REFERENCES STAIN (Id),
            UNIQUE (Plate_Id, Stain_Id)
        )
        """,
        "DROP TABLE IF EXISTS PLATE_STAIN"
    ),
    step(
        "CREATE INDEX IX_PLATE_STAIN_Plate_Id ON PLATE_STAIN (Plate_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_STAIN_Plate_Id"
    ),
    step(
        "CREATE INDEX IX_PLATE_STAIN_Stain_Id ON PLATE_STAIN (Stain_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_STAIN_Stain_Id"
    ),
]
