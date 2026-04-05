SELECT  l.Id,
        l.Name,
        l.Grid_Reference,
        l.Coordinate_System,
        l.Latitude,
        l.Longitude
FROM    LOCATION l
WHERE   l.Id = ?