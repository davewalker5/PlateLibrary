from yoyo import step

__depends__ = {
    "0007_seed_camera"
}

investigations = [
    ("IN-2026-000", "Method and Basic Discipline With the Microscope", "0 - Elementary Discipline in the use of the Microscope"),
    ("IN-2026-001", "Common Cleavers (Galium aparine) — Stem (T.S.)", "II - Support and Conduction"),
    ("IN-2026-002", "Dandelion (Taraxacum officinale) — Stem (T.S.)", "II - Support and Conduction"),
    ("IN-2026-003", "Common Orange Lichen (Xanthoria parietina) — Whole Mount (W.M.)", "I - Dormant and Elementary Forms"),
    ("IN-2026-004", "Cypress-leaved Plait-moss (Hypnum cupressiforme) — Whole Mount (W.M.)", "II - Support and Conduction"),
    ("IN-2026-005", "House Fly (Musca domestica) — Wing (W.M.)", "VI - Minor Animal Structure"),
    ("IN-2026-006", "Common Ivy (Hedera helix) — Stem (T.S.)", "II - Support and Conduction"),
    ("IN-2026-007", "Pussy Willow (Salix caprea) — Pollen (W.M.)", "III - Reproductive Elements")
]

steps = [
    step(
        f"""
        INSERT OR IGNORE INTO INVESTIGATION (Reference, Title, Series_Id)
        VALUES (
            '{reference}',
            '{title}',
            (SELECT Id FROM SERIES WHERE Name = '{series_name}')
        )
        """,
        f"""
        DELETE FROM INVESTIGATION
        WHERE Reference = '{reference}'
        """
    )
    for reference, title, series_name in investigations
]