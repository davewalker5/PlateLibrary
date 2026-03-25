from yoyo import step

__depends__ = {
    "0008_seed_investigation"
}

steps = [
    step(
        "DROP VIEW IF EXISTS plate_view",
        "DROP VIEW IF EXISTS plate_view",
    ),
    step(
        """
        CREATE VIEW plate_view AS
        SELECT          p.Date,
                        sc.Code || ' ' || se.Name AS "Series",
                        sp.Scientific_Name AS "Scientific Name",
                        sp.Common_Name AS "Common Name",
                        p.Specimen,
                        p.Plate,
                        p.Reference,
                        i.Reference AS "Investigation",
                        m.Description AS "Microscope",
                        o.Description AS "Objective",
                        o.Magnification,
                        c.Description AS "Camera",
                        c.Lower_Effective_Magnification AS "Lower Effective Magnification",
                        c.Upper_Effective_Magnification AS "Upper Effective Magnification",
                        p.Notebook_Reference AS "Notebook Reference",
                        p.Notes
        FROM            PLATE p
        INNER JOIN      INVESTIGATION i ON i.Id = p.Investigation_Id
        INNER JOIN      SERIES se ON se.Id = i.Series_Id
        INNER JOIN      SCHEME sc ON sc.Id = se.Scheme_Id
        INNER JOIN      OBJECTIVE o ON o.Id = p.Objective_Id
        INNER JOIN      MICROSCOPE m ON m.Id = o.Microscope_Id
        INNER JOIN      CAMERA c ON c.Id = p.Camera_Id
        LEFT OUTER JOIN SPECIES sp ON sp.Id = p.Species_Id;
        """,
        "DROP VIEW IF EXISTS plate_view",
    ),
]