from yoyo import step

__depends__ = {
    "0006_seed_objectives"
}

steps = [
    step(
        """
        INSERT OR IGNORE INTO CAMERA
        (Description, Lower_Effective_Magnification, Upper_Effective_Magnification)
        VALUES (
            'AmScope MD35',
            49,
            62
        )
        """,
        """
        DELETE FROM CAMERA
        WHERE Description = 'AmScope MD35'
        """
    ),

    step(
        """
        INSERT OR IGNORE INTO CAMERA
        (Description, Lower_Effective_Magnification, Upper_Effective_Magnification)
        VALUES (
            'Nikon D5600',
            NULL,
            NULL
        )
        """,
        """
        DELETE FROM CAMERA
        WHERE Description = 'AmScope MD35'
        """
    ),

    step(
        """
        INSERT OR IGNORE INTO CAMERA
        (Description, Lower_Effective_Magnification, Upper_Effective_Magnification)
        VALUES (
            'Swift EC5R',
            26,
            39
        )
        """,
        """
        DELETE FROM CAMERA
        WHERE Description = 'Swift EC5R'
        """
    )
]