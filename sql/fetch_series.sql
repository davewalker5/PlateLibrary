
SELECT      se.Id,
            sc.Code || '-' || se.Code || ' ' || se.Name AS Label
FROM        SERIES se
INNER JOIN  SCHEME sc ON sc.Id = se.Scheme_Id
ORDER BY    sc.Code, se.Name