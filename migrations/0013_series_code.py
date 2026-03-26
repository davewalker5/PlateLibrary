from yoyo import step

__depends__ = {
    "0012_hidden_plate"
}

steps = [
    step(
        "ALTER TABLE SERIES ADD COLUMN Code TEXT",
        "-- SQLite may not support DROP COLUMN; leaving as no-op",
    ),

    step(
        "UPDATE SERIES SET Code = '0' WHERE Id = 1",
        "UPDATE SERIES SET Code = NULL WHERE Id = 1",
    ),
    step(
        "UPDATE SERIES SET Code = 'I' WHERE Id = 2",
        "UPDATE SERIES SET Code = NULL WHERE Id = 2",
    ),
    step(
        "UPDATE SERIES SET Code = 'II' WHERE Id = 3",
        "UPDATE SERIES SET Code = NULL WHERE Id = 3",
    ),
    step(
        "UPDATE SERIES SET Code = 'III' WHERE Id = 4",
        "UPDATE SERIES SET Code = NULL WHERE Id = 4",
    ),
    step(
        "UPDATE SERIES SET Code = 'IV' WHERE Id = 5",
        "UPDATE SERIES SET Code = NULL WHERE Id = 5",
    ),
    step(
        "UPDATE SERIES SET Code = 'V' WHERE Id = 6",
        "UPDATE SERIES SET Code = NULL WHERE Id = 6",
    ),
    step(
        "UPDATE SERIES SET Code = 'VI' WHERE Id = 7",
        "UPDATE SERIES SET Code = NULL WHERE Id = 7",
    ),
    step(
        "UPDATE SERIES SET Code = 'VII' WHERE Id = 8",
        "UPDATE SERIES SET Code = NULL WHERE Id = 8",
    ),
    step(
        "UPDATE SERIES SET Code = 'VIII' WHERE Id = 9",
        "UPDATE SERIES SET Code = NULL WHERE Id = 9",
    ),
    step(
        "UPDATE SERIES SET Code = 'I' WHERE Id = 10",
        "UPDATE SERIES SET Code = NULL WHERE Id = 10",
    ),

    step(
        "CREATE INDEX IF NOT EXISTS idx_series_scheme_code ON SERIES (Scheme_Id, Code)",
        "DROP INDEX IF EXISTS idx_series_scheme_code",
    ),
]