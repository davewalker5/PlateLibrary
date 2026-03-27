SELECT      i.Id,
            i.Reference,
            i.Title,
            sc.Code || '-' || se.Code || ' ' || se.Name AS Series,
            (
                SELECT COUNT(*)
                FROM PLATE p
                WHERE p.Investigation_Id = i.Id

            ) AS Plate_Count
FROM        INVESTIGATION i
INNER JOIN  SERIES se ON se.Id = i.Series_Id
INNER JOIN  SCHEME sc ON sc.Id = se.Scheme_Id
ORDER BY    i.Reference