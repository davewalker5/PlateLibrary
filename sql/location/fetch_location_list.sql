SELECT      l.Id,
            l.Name,
            l.Grid_Reference,
            l.Latitude,
            l.Longitude,
            (
                SELECT COUNT(*)
                FROM PLATE p
                WHERE p.Location_Id = l.Id
            ) AS Plate_Count
FROM        LOCATION l
ORDER BY    l.Name