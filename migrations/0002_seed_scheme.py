from yoyo import step

__depends__ = {
    "0001_initial_schema"
}

steps = [
    step(
        """
        INSERT OR IGNORE INTO SCHEME (Name, Code)
        VALUES ('Scheme of Structural Investigations', 'SI')
        """,
        """
        DELETE FROM SCHEME
        WHERE Name = 'Scheme of Structural Investigations'
        """
    )
]