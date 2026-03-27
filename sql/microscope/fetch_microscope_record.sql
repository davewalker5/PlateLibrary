SELECT  m.Id,
        m.Description,
        m.Manufacturer,
        m.Manufactured,
        m.Serial_Number
FROM    MICROSCOPE m
WHERE   m.Id = ?