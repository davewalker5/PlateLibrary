from yoyo import step

__depends__ = {
    "0011_seed_locations"
}

steps = [
    step(
        """
        ALTER TABLE PLATE
        ADD COLUMN Hidden INTEGER NOT NULL DEFAULT 0 CHECK (Hidden IN (0, 1))
        """,
        """
        -- Irreversible on SQLite without rebuilding the table
        """
    )
]