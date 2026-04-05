SELECT      l.Id,
            CASE
                WHEN l.Grid_Reference IS NOT NULL AND TRIM(l.Grid_Reference) <> ''
                    THEN l.Name || ' | ' || l.Grid_Reference || ' (' || l.Coordinate_System || ')'
                ELSE l.Name
            END AS Label
FROM        LOCATION l
ORDER BY    l.Name