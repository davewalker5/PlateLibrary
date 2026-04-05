SELECT          p.Id,
                p.Date,
                sc.Code || '-' || se.Code || ' ' || se.Name AS "Series",
                sp.Scientific_Name AS "Scientific Name",
                sp.Common_Name AS "Common Name",
                p.Specimen,
                st.Stain AS "Stain",
                CASE
                    WHEN l.Id IS NULL THEN NULL
                    WHEN l.Grid_Reference IS NOT NULL THEN l.Grid_Reference
                    WHEN l.Latitude IS NOT NULL AND l.Longitude IS NOT NULL
                        THEN l.Latitude || ', ' || l.Longitude
                    ELSE l.Name
                END AS "Location",
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
LEFT OUTER JOIN SPECIES sp ON sp.Id = p.Species_Id
LEFT OUTER JOIN LOCATION l ON l.Id = p.Location_Id
LEFT OUTER JOIN (   SELECT  Plate_Id,
                            group_concat(Description, ' | ') AS Stain
                    FROM (
                        SELECT  ps.Plate_Id,
                                s.Description
                        FROM    PLATE_STAIN ps
                        INNER JOIN STAIN s ON s.Id = ps.Stain_Id
                        ORDER BY ps.Plate_Id, s.Description
                    )
                    GROUP BY Plate_Id
                ) st ON st.Plate_Id = p.Id
WHERE           p.Hidden = 0
ORDER BY        p.Plate