
SELECT      o.Id,
            m.Description || ' | ' || o.Description || ' | ' || o.Magnification || 'x' AS Label
FROM        OBJECTIVE o
INNER JOIN  MICROSCOPE m ON m.Id = o.Microscope_Id
ORDER BY    m.Description, o.Magnification, o.Description