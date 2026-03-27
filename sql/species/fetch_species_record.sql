SELECT  s.Id,
        s.Scientific_Name,
        s.Common_Name
FROM    SPECIES s
WHERE   s.Id = ?