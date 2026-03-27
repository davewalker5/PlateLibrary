SELECT      i.Id,
            sc.Code || '-' || se.Code || ' ' || se.Name || ' | ' || i.Reference || ' | ' || i.Title AS Label
FROM        INVESTIGATION i
INNER JOIN  SERIES se ON se.Id = i.Series_Id
INNER JOIN  SCHEME sc ON sc.Id = se.Scheme_Id
ORDER BY    sc.Code, se.Name, i.Reference