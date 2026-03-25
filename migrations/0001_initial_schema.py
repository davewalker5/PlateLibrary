from yoyo import step

__depends__ = {}

steps = [
    step(
        "CREATE TABLE SCHEME (Id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL, Code NOT NULL UNIQUE)",
        "DROP TABLE IF EXISTS SCHEME"
    ),

    step(
        "CREATE TABLE SERIES (Id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL UNIQUE, Scheme_Id INTEGER NOT NULL REFERENCES SCHEME(Id))",
        "DROP TABLE IF EXISTS SERIES"
    ),

    step(
        "CREATE INDEX IX_SERIES_Scheme_Id ON SERIES(Scheme_Id)",
        "DROP INDEX IF EXISTS IX_SERIES_Scheme_Id"
    ),

    step(
        "CREATE TABLE SPECIES (Id INTEGER PRIMARY KEY AUTOINCREMENT, Scientific_Name TEXT NULL UNIQUE, Common_Name TEXT NULL UNIQUE)",
        "DROP TABLE IF EXISTS SPECIES"
    ),

    step(
        "CREATE TABLE MICROSCOPE (Id INTEGER PRIMARY KEY AUTOINCREMENT, Description TEXT NOT NULL UNIQUE, Manufacturer TEXT NOT NULL, Manufactured INTEGER NOT NULL, Serial_Number TEXT NOT NULL)",
        "DROP TABLE IF EXISTS MICROSCOPE"
    ),

    step(
        "CREATE TABLE OBJECTIVE (Id INTEGER PRIMARY KEY AUTOINCREMENT, Microscope_Id INTEGER NOT NULL, Description TEXT NOT NULL, Magnification INTEGER NOT NULL, FOREIGN KEY (Microscope_Id) REFERENCES MICROSCOPE(Id))",
        "DROP TABLE IF EXISTS OBJECTIVE"
    ),

    step(
        "CREATE INDEX IX_OBJECTIVE_Microscope_Id ON OBJECTIVE(Microscope_Id)",
        "DROP INDEX IF EXISTS IX_OBJECTIVE_Microscope_Id"
    ),

    step(
        "CREATE TABLE CAMERA (Id INTEGER PRIMARY KEY AUTOINCREMENT, Description TEXT NOT NULL UNIQUE, Lower_Effective_Magnification INTEGER NULL, Upper_Effective_Magnification INTEGER NULL)",
        "DROP TABLE IF EXISTS CAMERA"
    ),

    step(
        "CREATE TABLE STAIN (Id INTEGER PRIMARY KEY AUTOINCREMENT, Description TEXT NOT NULL)",
        "DROP TABLE IF EXISTS STAIN"
    ),

    step(
        "CREATE TABLE LOCATION (Id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT NOT NULL UNIQUE, Grid_Reference TEXT NULL)",
        "DROP TABLE IF EXISTS LOCATION"
    ),

    step(
        "CREATE TABLE INVESTIGATION (Id INTEGER PRIMARY KEY AUTOINCREMENT, Reference TEXT NOT NULL UNIQUE, Title TEXT NOT NULL, Series_Id INTEGER NOT NULL REFERENCES SERIES(Id))",
        "DROP TABLE IF EXISTS INVESTIGATION"
    ),

    step(
        "CREATE INDEX IX_INVESTIGATION_Series_Id ON INVESTIGATION(Series_Id)",
        "DROP INDEX IF EXISTS IX_INVESTIGATION_Series_Id"
    ),

    step(
        """CREATE TABLE PLATE (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Date DATETIME NOT NULL,
            Specimen TEXT NOT NULL,
            Plate TEXT NOT NULL UNIQUE,
            Reference TEXT NOT NULL UNIQUE,
            Notebook_Reference TEXT NULL,
            Notes TEXT NULL,
            Species_Id INTEGER NULL,
            Objective_Id INTEGER NOT NULL,
            Camera_Id INTEGER NOT NULL,
            Stain_Id INTEGER NULL,
            Location_Id INTEGER NULL,
            Investigation_Id INTEGER NOT NULL,
            FOREIGN KEY (Species_Id) REFERENCES SPECIES(Id),
            FOREIGN KEY (Objective_Id) REFERENCES OBJECTIVE(Id),
            FOREIGN KEY (Camera_Id) REFERENCES CAMERA(Id),
            FOREIGN KEY (Stain_Id) REFERENCES STAIN(Id),
            FOREIGN KEY (Location_Id) REFERENCES LOCATION(Id),
            FOREIGN KEY (Investigation_Id) REFERENCES INVESTIGATION(Id)
        )""",
        "DROP TABLE IF EXISTS PLATE"
    ),

    step(
        "CREATE INDEX IX_PLATE_Species_Id ON PLATE(Species_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_Species_Id"
    ),

    step(
        "CREATE INDEX IX_PLATE_Objective_Id ON PLATE(Objective_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_Objective_Id"
    ),

    step(
        "CREATE INDEX IX_PLATE_Camera_Id ON PLATE(Camera_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_Camera_Id"
    ),

    step(
        "CREATE INDEX IX_PLATE_Stain_Id ON PLATE(Stain_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_Stain_Id"
    ),

    step(
        "CREATE INDEX IX_PLATE_Location_Id ON PLATE(Location_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_Location_Id"
    ),

    step(
        "CREATE INDEX IX_PLATE_Investigation_Id ON PLATE(Investigation_Id)",
        "DROP INDEX IF EXISTS IX_PLATE_Investigation_Id"
    ),
]