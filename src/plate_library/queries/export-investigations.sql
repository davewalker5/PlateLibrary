SELECT DISTINCT i.Reference,
                sc.Name AS "Scheme",
                se.Name AS "Series",
                i.Title,
                (
                    SELECT
                        x.Label ||
                        CASE
                            WHEN EXISTS (
                                SELECT 1
                                FROM (
                                    SELECT DISTINCT p3.Species_Id
                                    FROM            PLATE p3
                                    WHERE           p3.Investigation_Id = i.Id
                                    AND             p3.Species_Id IS NOT NULL
                                ) d
                                WHERE d.Species_Id != x.Species_Id
                            )
                            THEN ' et al.'
                            ELSE ''
                        END
                    FROM (
                        SELECT DISTINCT p2.Species_Id, sv2.Label
                        FROM            PLATE p2
                        LEFT JOIN       SPECIES_VIEW sv2 ON sv2.Id = p2.Species_Id
                        WHERE           p2.Investigation_Id = i.Id
                        AND             sv2.Label IS NOT NULL
                        ORDER BY        sv2.Label
                        LIMIT 1
                    ) x
                ) AS "Subject"
FROM            INVESTIGATION i
INNER JOIN      SERIES se ON se.Id = i.Series_Id
INNER JOIN      SCHEME sc ON sc.Id = se.Scheme_Id
LEFT OUTER JOIN PLATE p ON p.Investigation_Id = i.Id
LEFT OUTER JOIN SPECIES_VIEW sv ON sv.Id = p.Species_Id
ORDER BY        i.Reference ASC;