from yoyo import step

__depends__ = {
    "0016_create_plate_stain"
}

steps = [
    step(
        "ALTER TABLE PLATE RENAME TO PLATE_OLD",
        None
    ),
    step(
        """
        CREATE TABLE PLATE (
            Id                 INTEGER  PRIMARY KEY AUTOINCREMENT,
            Date               DATETIME NOT NULL,
            Specimen           TEXT     NOT NULL,
            Plate              TEXT     NOT NULL UNIQUE,
            Reference          TEXT     NOT NULL UNIQUE,
            Notebook_Reference TEXT     NULL,
            Notes              TEXT     NULL,
            Species_Id         INTEGER  NULL,
            Objective_Id       INTEGER  NOT NULL,
            Camera_Id          INTEGER  NOT NULL,
            Location_Id        INTEGER  NULL,
            Investigation_Id   INTEGER  NOT NULL,
            Hidden             INTEGER  NOT NULL
                                DEFAULT 0
                                CHECK (Hidden IN (0, 1)),
            FOREIGN KEY (Species_Id) REFERENCES SPECIES (Id),
            FOREIGN KEY (Objective_Id) REFERENCES OBJECTIVE (Id),
            FOREIGN KEY (Camera_Id) REFERENCES CAMERA (Id),
            FOREIGN KEY (Location_Id) REFERENCES LOCATION (Id),
            FOREIGN KEY (Investigation_Id) REFERENCES INVESTIGATION (Id)
        )
        """,
        None
    ),
    step(
        """
        INSERT INTO PLATE (
            Id,
            Date,
            Specimen,
            Plate,
            Reference,
            Notebook_Reference,
            Notes,
            Species_Id,
            Objective_Id,
            Camera_Id,
            Location_Id,
            Investigation_Id,
            Hidden
        )
        SELECT
            Id,
            Date,
            Specimen,
            Plate,
            Reference,
            Notebook_Reference,
            Notes,
            Species_Id,
            Objective_Id,
            Camera_Id,
            Location_Id,
            Investigation_Id,
            Hidden
        FROM PLATE_OLD
        """,
        None
    ),
    step(
        "DROP TABLE PLATE_OLD",
        None
    )
]
