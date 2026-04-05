SELECT  i.Id,
        i.Reference,
        i.Title,
        i.Series_Id
FROM    INVESTIGATION i
WHERE   i.Id = ?