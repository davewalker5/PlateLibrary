SELECT      i.Reference,
            sc.Name AS "Scheme",
            se.Name AS "Series",
            i.Title
FROM        INVESTIGATION i
INNER JOIN  SERIES se ON se.Id = i.Series_Id
INNER JOIN  SCHEME sc ON sc.Id = se.Scheme_Id
ORDER BY    i.Reference ASC;
