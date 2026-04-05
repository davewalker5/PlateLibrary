SELECT      m.Id,
            m.Description,
            m.Manufacturer,
            m.Manufactured,
            m.Serial_Number
FROM        MICROSCOPE m
ORDER BY    m.Manufacturer, m.Description
