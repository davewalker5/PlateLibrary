SELECT  p.Id,
        p.Date,
        p.Specimen,
        p.Plate,
        p.Reference,
        p.Notebook_Reference,
        p.Notes,
        p.Species_Id,
        p.Objective_Id,
        p.Camera_Id,
        group_concat(ps.Stain_Id) AS Stain_Ids,
        p.Location_Id,
        p.Investigation_Id
FROM    PLATE p
LEFT OUTER JOIN PLATE_STAIN ps
        ON ps.Plate_Id = p.Id
WHERE   p.Id = ?
GROUP BY
        p.Id,
        p.Date,
        p.Specimen,
        p.Plate,
        p.Reference,
        p.Notebook_Reference,
        p.Notes,
        p.Species_Id,
        p.Objective_Id,
        p.Camera_Id,
        p.Location_Id,
        p.Investigation_Id