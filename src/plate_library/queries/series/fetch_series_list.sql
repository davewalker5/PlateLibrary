SELECT      s.Id,
            s.Name,
            s.Code,
            s.Plate_Format,
            s.Scheme_Id,
            sc.Code AS Scheme_Code,
            sc.Name AS Scheme_Name
FROM        SERIES s
INNER JOIN  SCHEME sc ON sc.Id = s.Scheme_Id
ORDER BY    sc.Code, s.Code, s.Name