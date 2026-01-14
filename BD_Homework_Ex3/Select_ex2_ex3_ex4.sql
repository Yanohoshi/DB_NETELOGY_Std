-- ЗАДАНИЕ 2
-- 1. Название и продолжительность самого длительного трека
SELECT title, duration
FROM tracks
WHERE duration = (SELECT MAX(duration) FROM tracks);

-- 2. Название треков, продолжительность которых не менее 3,5 минут (210 секунд)
SELECT title, duration
FROM tracks
WHERE duration >= 210
ORDER BY duration;

-- 3. Названия сборников, вышедших в период с 2018 по 2020 год включительно
SELECT title, release_year
FROM collections
WHERE release_year BETWEEN 2018 AND 2020
ORDER BY release_year;

-- 4. Исполнители, чьё имя состоит из одного слова
SELECT name
FROM artists
WHERE name NOT LIKE '% %';

-- 5. Название треков, которые содержат слово «мой» или «ту»
SELECT title
FROM tracks
WHERE LOWER(title) LIKE '%мой%' OR LOWER(title) LIKE '%my%';


-- ЗАДАНИЕ 3
-- 1. Количество исполнителей в каждом жанре
SELECT g.name AS genre_name, COUNT(ag.artist_id) AS artist_count
FROM genres g
LEFT JOIN artistgenres ag ON g.id = ag.genre_id
GROUP BY g.id, g.name
ORDER BY artist_count DESC;

-- 2. Количество треков, вошедших в альбомы 2019–2020 годов
SELECT COUNT(t.id) AS track_count
FROM tracks t
JOIN albums a ON t.album_id = a.id
WHERE a.release_year BETWEEN 2019 AND 2020;

-- 3. Средняя продолжительность треков по каждому альбому
SELECT 
    a.title AS album_title,
    ROUND(AVG(t.duration), 2) AS avg_duration_seconds,
    CONCAT(
        FLOOR(AVG(t.duration)/60), ' мин ',
        ROUND(AVG(t.duration)%60), ' сек'
    ) AS avg_duration_formatted,
    COUNT(t.id) AS track_count
FROM albums a
JOIN tracks t ON a.id = t.album_id
GROUP BY a.id, a.title
ORDER BY avg_duration_seconds DESC;

-- 4. Все исполнители, которые не выпустили альбомы в 2020 году
SELECT DISTINCT ar.name AS artist_name
FROM artists ar
WHERE ar.id NOT IN (
    SELECT DISTINCT aa.artist_id
    FROM albumartists aa
    JOIN albums al ON aa.album_id = al.id
    WHERE al.release_year = 2020
)
ORDER BY ar.name;

-- 5. Названия сборников, в которых присутствует конкретный исполнитель
-- Выберем исполнителя "The Beatles" (id=1)
SELECT DISTINCT 
    c.title AS collection_title,
    c.release_year,
    ar.name AS artist_name
FROM collections c
JOIN collectiontracks ct ON c.id = ct.collection_id
JOIN tracks t ON ct.track_id = t.id
JOIN albums al ON t.album_id = al.id
JOIN albumartists aa ON al.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
WHERE ar.name = 'The Beatles'
ORDER BY c.release_year;


-- ЗАДАНИЕ 4
-- 1. Названия альбомов, в которых присутствуют исполнители более чем одного жанра
SELECT DISTINCT a.title AS album_title, ar.name AS artist_name
FROM albums a
JOIN albumartists aa ON a.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
WHERE ar.id IN (
    SELECT artist_id
    FROM artistgenres
    GROUP BY artist_id
    HAVING COUNT(DISTINCT genre_id) > 1
)
ORDER BY a.title;

-- 2. Наименования треков, которые не входят в сборники
SELECT t.title AS track_title, a.title AS album_title, ar.name AS artist_name
FROM tracks t
JOIN albums a ON t.album_id = a.id
JOIN albumartists aa ON a.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
WHERE t.id NOT IN (
    SELECT DISTINCT track_id FROM collectiontracks
)
ORDER BY t.title;

-- 3. Исполнитель или исполнители, написавшие самый короткий по продолжительности трек
SELECT '• ' || ar.name || ' (трек: "' || t.title || '", длительность: ' || 
    TO_CHAR((t.duration || ' seconds')::interval, 'MI:SS') || ')' as "Результат"
FROM tracks t
JOIN albums a ON t.album_id = a.id
JOIN albumartists aa ON a.id = aa.album_id
JOIN artists ar ON aa.artist_id = ar.id
WHERE t.duration = (SELECT MIN(duration) FROM tracks)
ORDER BY ar.name;

-- 4. Названия альбомов, содержащих наименьшее количество треков
SELECT 
    a.title AS album_title,
    COUNT(t.id) AS track_count,
    a.release_year
FROM albums a
JOIN tracks t ON a.id = t.album_id
GROUP BY a.id, a.title, a.release_year
HAVING COUNT(t.id) = (
    SELECT MIN(track_count)
    FROM (
        SELECT COUNT(id) AS track_count
        FROM tracks
        GROUP BY album_id
    ) AS album_tracks
)
ORDER BY a.title;