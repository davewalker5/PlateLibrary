SELECT      o.Id,
            m.Description || ' | ' || o.Description || ' | ' || o.Magnification || 'x' AS Label,
            o.Description,
            o.Magnification,
            o.Microscope_Id,
            m.Description AS Microscope_Description,
            m.Manufacturer AS Microscope_Manufacturer
FROM        OBJECTIVE o
JOIN        MICROSCOPE m ON m.Id = o.Microscope_Id
ORDER BY    m.Description, o.Magnification, o.Description