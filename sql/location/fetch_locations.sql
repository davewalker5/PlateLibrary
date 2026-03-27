SELECT      l.Id,
            CASE
                WHEN l.Grid_Reference IS NOT NULL AND TRIM(l.Grid_Reference) <> ''
                    THEN l.Name || ' | ' || l.Grid_Reference
                ELSE Name
            END AS Label
FROM        LOCATION l
ORDER BY    l.Name