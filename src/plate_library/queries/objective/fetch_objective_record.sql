SELECT  o.Id,
        o.Microscope_Id,
        o.Description,
        o.Magnification
FROM    OBJECTIVE o
WHERE   o.Id = ?