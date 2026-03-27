SELECT      o.Id,
            o.Microscope_Id,
            m.Description AS Microscope_Description,
            m.Manufacturer AS Microscope_Manufacturer,
            o.Description,
            o.Magnification
FROM        OBJECTIVE o
JOIN        MICROSCOPE m ON m.Id = o.Microscope_Id
ORDER BY    m.Description, o.Magnification, o.Description
