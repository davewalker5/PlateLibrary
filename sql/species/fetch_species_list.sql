SELECT      s.Id,
            CASE
                WHEN s.Scientific_Name IS NOT NULL AND s.Common_Name IS NOT NULL
                    THEN s.Scientific_Name || ' | ' || s.Common_Name
                WHEN Scientific_Name IS NOT NULL
                    THEN s.Scientific_Name
                WHEN Common_Name IS NOT NULL
                    THEN s.Common_Name
                ELSE '[Unnamed species]'
            END AS Label,
            s.Scientific_Name,
            s.Common_Name
FROM        SPECIES s
ORDER BY    COALESCE(s.Scientific_Name, s.Common_Name), s.Id