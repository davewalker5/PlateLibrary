SELECT      p.Plate,
            p.Reference
FROM        PLATE p
INNER JOIN  INVESTIGATION i ON i.Id = p.Investigation_Id
WHERE       i.Series_Id = ?