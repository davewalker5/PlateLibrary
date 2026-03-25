from yoyo import step

__depends__ = {
    "0002_seed_scheme"
}

series_data = [
    "0 - Elementary Discipline in the use of the Microscope",
    "I - Dormant and Elementary Forms",
    "II - Support and Conduction",
    "III - Reproductive Elements",
    "IV - Surface and Exchange",
    "V - Aquatic Microscopic Life",
    "VI - Minor Animal Structure",
    "VII - Senescence and Decomposition",
    "VIII - Review and Redrawing",
]

steps = [
    step(
        f"""
        INSERT OR IGNORE INTO SERIES (Name, Scheme_Id)
        VALUES (
            '{name}',
            (SELECT Id FROM SCHEME WHERE Name = 'Scheme of Structural Investigations')
        )
        """,
        f"""
        DELETE FROM SERIES
        WHERE Name = '{name}'
        """
    )
    for name in series_data
]