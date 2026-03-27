SELECT      c.Id,
            CASE
                WHEN c.Lower_Effective_Magnification IS NOT NULL AND c.Upper_Effective_Magnification IS NOT NULL
                    THEN Description || ' | eff. ' || c.Lower_Effective_Magnification || 'x–' || c.Upper_Effective_Magnification || 'x'
                WHEN Lower_Effective_Magnification IS NOT NULL
                    THEN Description || ' | eff. from ' || c.Lower_Effective_Magnification || 'x'
                WHEN Upper_Effective_Magnification IS NOT NULL
                    THEN Description || ' | eff. to ' || c.Upper_Effective_Magnification || 'x'
                ELSE c.Description
            END AS Label
FROM        CAMERA c
ORDER BY    c.Description