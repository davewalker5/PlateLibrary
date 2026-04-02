from yoyo import step

__depends__ = {
    "0019_add_coordinate_system"
}

steps = [
    step(
        "DROP VIEW IF EXISTS species_view",
        "DROP VIEW IF EXISTS species_view"
    ),

    step(
        """
        CREATE VIEW     species_view AS
        SELECT          s.Id,
                        s.Scientific_Name,
                        s.Common_Name,
                        CASE
                            WHEN s.Common_Name IS NOT NULL AND s.Scientific_Name IS NOT NULL
                                THEN s.Common_Name || ' (' || s.Scientific_Name || ')'
                            ELSE COALESCE(s.Common_Name, s.Scientific_Name)
                        END AS "Label"
        FROM            SPECIES s
        """,
        "DROP VIEW IF EXISTS species_view"
    ),
]