SELECT      s.Id,
            s.Code || ' | ' || s.Name AS Label,
            s.Name,
            s.Code
FROM        SCHEME s
ORDER BY    s.Code