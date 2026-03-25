from yoyo import step

__depends__ = {
    "0004_seed_species"
}

steps = [
    step(
        """
        INSERT OR IGNORE INTO MICROSCOPE
        (Description, Manufacturer, Manufactured, Serial_Number)
        VALUES (
            'Ernst Leitz, Wetzlar, 1912, Stand II',
            'Ernst Leitz',
            1912,
            '149811'
        )
        """,
        """
        DELETE FROM MICROSCOPE
        WHERE Serial_Number = '149811'
        """
    )
]