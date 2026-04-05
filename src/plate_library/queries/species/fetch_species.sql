SELECT      s.Id,
            CASE
                WHEN s.Common_Name IS NOT NULL AND s.Scientific_Name IS NOT NULL
                    THEN s.Common_Name || ' — ' || s.Scientific_Name
                WHEN s.Common_Name IS NOT NULL
                    THEN s.Common_Name
                WHEN s.Scientific_Name IS NOT NULL
                    THEN s.Scientific_Name
                ELSE '(Unnamed species record #' || s.Id || ')'
            END AS "Label"
FROM        SPECIES s
ORDER BY    CASE WHEN s.Common_Name IS NULL THEN 1 ELSE 0 END,
            s.Common_Name,
            s.Scientific_Name