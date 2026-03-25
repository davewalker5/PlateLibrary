from yoyo import step

__depends__ = {
    "0005_seed_microscope"
}

steps = [
    step(
        """
        INSERT OR IGNORE INTO OBJECTIVE (Microscope_Id, Description, Magnification)
        VALUES (
            (SELECT Id FROM MICROSCOPE WHERE Serial_Number = '149811'),
            'No. 3',
            10
        )
        """,
        """
        DELETE FROM OBJECTIVE
        WHERE Microscope_Id = (SELECT Id FROM MICROSCOPE WHERE Serial_Number = '149811')
          AND Description = 'No. 3'
          AND Magnification = 10
        """
    ),
    step(
        """
        INSERT OR IGNORE INTO OBJECTIVE (Microscope_Id, Description, Magnification)
        VALUES (
            (SELECT Id FROM MICROSCOPE WHERE Serial_Number = '149811'),
            'No. 6',
            40
        )
        """,
        """
        DELETE FROM OBJECTIVE
        WHERE Microscope_Id = (SELECT Id FROM MICROSCOPE WHERE Serial_Number = '149811')
          AND Description = 'No. 6'
          AND Magnification = 40
        """
    ),
]