SELECT      c.Id,
            c.Description,
            c.Lower_Effective_Magnification,
            c.Upper_Effective_Magnification
FROM        CAMERA c
ORDER BY    c.Description