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
        p.Stain_Id,
        p.Location_Id,
        p.Investigation_Id
FROM    PLATE p
WHERE   p.Id = ?