-- ============================================================
--   NETFLIX CONTENT ANALYSIS — SQL Queries (PostgreSQL)
--   Database : netflix_analysis
--   Table    : netflix
-- ============================================================


-- PREVIEW TABLE
SELECT * FROM netflix LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- Q1. What is the total number of Movies vs TV Shows?
-- ─────────────────────────────────────────────────────────────
SELECT
    type,
    COUNT(*) AS total_titles,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM netflix
GROUP BY type
ORDER BY total_titles DESC;


-- ─────────────────────────────────────────────────────────────
-- Q2. Which are the Top 10 countries with the most content?
-- ─────────────────────────────────────────────────────────────
SELECT
    primary_country,
    COUNT(*) AS total_titles,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM netflix), 2) AS percentage
FROM netflix
WHERE primary_country IS NOT NULL
GROUP BY primary_country
ORDER BY total_titles DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- Q3. How has Netflix content grown year over year? (2010–2021)
-- ─────────────────────────────────────────────────────────────
SELECT
    year_added,
    COUNT(*) AS titles_added,
    SUM(COUNT(*)) OVER (ORDER BY year_added) AS cumulative_total
FROM netflix
WHERE year_added >= 2010
GROUP BY year_added
ORDER BY year_added;


-- ─────────────────────────────────────────────────────────────
-- Q4. What are the Top 10 genres on Netflix?
-- ─────────────────────────────────────────────────────────────
SELECT
    primary_genre,
    COUNT(*) AS total_titles
FROM netflix
GROUP BY primary_genre
ORDER BY total_titles DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- Q5. What is the content rating breakdown?
--     Which rating has the most titles?
-- ─────────────────────────────────────────────────────────────
SELECT
    rating,
    COUNT(*) AS total_titles,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM netflix), 2) AS percentage
FROM netflix
WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY total_titles DESC;


-- ─────────────────────────────────────────────────────────────
-- Q6. Who are the Top 10 directors with the most titles?
-- ─────────────────────────────────────────────────────────────
SELECT
    director,
    COUNT(*) AS total_titles,
    COUNT(CASE WHEN type = 'Movie'   THEN 1 END) AS movies,
    COUNT(CASE WHEN type = 'TV Show' THEN 1 END) AS tv_shows
FROM netflix
WHERE director != 'Unknown'
GROUP BY director
ORDER BY total_titles DESC
LIMIT 10;


-- ─────────────────────────────────────────────────────────────
-- Q7. What is the average movie duration?
--     And how many movies are above/below average?
-- ─────────────────────────────────────────────────────────────
SELECT
    ROUND(AVG(duration_value)::numeric, 2)                                        AS avg_movie_duration_mins,
    COUNT(CASE WHEN duration_value > (SELECT AVG(duration_value) FROM netflix WHERE type = 'Movie') THEN 1 END) AS above_average,
    COUNT(CASE WHEN duration_value < (SELECT AVG(duration_value) FROM netflix WHERE type = 'Movie') THEN 1 END) AS below_average
FROM netflix
WHERE type = 'Movie';

-- ─────────────────────────────────────────────────────────────
-- Q8. Which month sees the most content added to Netflix?
-- ─────────────────────────────────────────────────────────────
SELECT
    month_name,
    month_added,
    COUNT(*) AS titles_added
FROM netflix
WHERE month_added IS NOT NULL
GROUP BY month_name, month_added
ORDER BY month_added;


-- ─────────────────────────────────────────────────────────────
-- Q9. What are the Top 3 genres for Movies vs TV Shows?
--     (Window Function)
-- ─────────────────────────────────────────────────────────────
WITH genre_rank AS (
    SELECT
        type,
        primary_genre,
        COUNT(*) AS total_titles,
        RANK() OVER (PARTITION BY type ORDER BY COUNT(*) DESC) AS genre_rank
    FROM netflix
    GROUP BY type, primary_genre
)
SELECT
    type,
    genre_rank,
    primary_genre,
    total_titles
FROM genre_rank
WHERE genre_rank <= 3
ORDER BY type, genre_rank;


-- ─────────────────────────────────────────────────────────────
-- Q10. Which countries produce the most content per type?
--      Show top 5 countries for Movies and TV Shows separately.
--      (CTE + Window Function)
-- ─────────────────────────────────────────────────────────────
WITH country_type AS (
    SELECT
        primary_country,
        type,
        COUNT(*) AS total_titles,
        ROW_NUMBER() OVER (PARTITION BY type ORDER BY COUNT(*) DESC) AS country_rank
    FROM netflix
    WHERE primary_country IS NOT NULL
    GROUP BY primary_country, type
)
SELECT
    type,
    country_rank,
    primary_country,
    total_titles
FROM country_type
WHERE country_rank <= 5
ORDER BY type, country_rank;