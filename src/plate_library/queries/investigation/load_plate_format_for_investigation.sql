SELECT      i.Series_Id AS Series_Id,
            sc.Code AS Scheme_Code,
            se.Code AS Series_Code,
            COALESCE(se.Plate_Format, 'simple') AS Plate_Format
FROM        INVESTIGATION i
INNER JOIN  SERIES se ON se.Id = i.Series_Id
INNER JOIN  SCHEME sc ON sc.Id = se.Scheme_Id
WHERE       i.Id = ?