SELECT  s.Id,
        s.Name,
        s.Scheme_Id,
        s.Code,
        s.Plate_Format
FROM    SERIES s
WHERE   s.Id = ?