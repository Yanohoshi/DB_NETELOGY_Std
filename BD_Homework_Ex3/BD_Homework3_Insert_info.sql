-- TRUNCATE TABLE collectiontracks, collections, albumartists, artistgenres, tracks, albums, artists, genres CASCADE;

INSERT INTO genres (id, name) 
VALUES (1, 'Rock'),
(2, 'Pop'),
(3, 'Hip-Hop'),
(4, 'Jazz'),
(5, 'Electronic');

INSERT INTO artists (id, name) 
VALUES (1, 'The Beatles'),
(2, 'Queen'),
(3, 'Madonna'),
(4, 'Eminem'),
(5, 'Miles Davis'),
(6, 'Daft Punk');

INSERT INTO albums  (id, title, release_year) 
VALUES (1, 'Abbey Road', 1969),
(2, 'A Night at the Opera', 1975),
(3, 'Like a Prayer', 1989),
(4, 'The Marshall Mathers LP', 2000),
(5, 'Kind of Blue', 1959),
(6, 'Random Access Memories', 2013),
(7, 'Revolver', 1966),
(8, 'New Album 2019', 2019),
(9, 'Latest Hits 2020', 2020);

INSERT INTO tracks  (id, title, duration, album_id) 
VALUES (1, 'Come Together', 259, 1),
(2, 'Something', 182, 1),
(3, 'Bohemian Rhapsody', 354, 2),
(4, 'Youre My Best Friend', 172, 2),
(5, 'Like a Prayer', 339, 3),
(6, 'Express Yourself', 280, 3),
(7, 'The Real Slim Shady', 284, 4),
(8, 'Stan', 404, 4),
(9, 'So What', 312, 5),
(10, 'Freddie Freeloader', 587, 5),
(11, 'Get Lucky', 369, 6),
(12, 'Instant Crush', 337, 6),
(13, 'Tomorrow Never Knows', 180, 7),
(14, 'Eleanor Rigby', 208, 7),
(15, 'Yellow Submarine', 157, 7),
(16, 'Here Comes the Sun', 185, 1),
(17, 'Summer Song', 240, 8),
(18, 'Winter Blues', 210, 8),
(19, 'Spring Fever', 195, 9),
(20, 'Autumn Leaves', 225, 9),
(21, 'My Mom', 259, 4);

INSERT INTO collections  (id, title, release_year) 
VALUES (1, 'Best of 60s', 2000),
(2, 'Rock Classics', 2010),
(3, 'Pop Hits 80s-90s', 2005),
(4, 'Hip-Hop Essentials', 2015),
(5, 'Jazz Masterpieces', 1995),
(6, 'Electronic Dance Music', 2020),
(7, 'All Time Greatest Hits', 2022),
(8, 'Legends Collection', 2018);

INSERT INTO artistgenres  (artist_id, genre_id) 
VALUES (1, 1),
(1, 2),
(2, 1),
(3, 2),
(4, 3),
(5, 4),
(6, 5),
(6, 2);

INSERT INTO albumartists (album_id, artist_id) 
VALUES (1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 1);

INSERT INTO collectiontracks (collection_id, track_id) 
VALUES
-- Best of 60s
(1, 1),
(1, 2),
(1, 13),
(1, 14),
(1, 16),  
-- Rock Classics
(2, 1),
(2, 3),
(2, 4),
(2, 13), 
-- Pop Hits 80s-90s
(3, 5),
(3, 6),
(3, 2),
-- Hip-Hop Essentials   
(4, 7),
(4, 8),
(4, 21),
-- Jazz Masterpieces    
(5, 9),
(5, 10),
-- Electronic Dance Music    
(6, 11),
(6, 12),
-- All Time Greatest Hits
(7, 1),
(7, 3),
(7, 5),
(7, 7),
(7, 11),
-- Legends Collection
(8, 1),
(8, 3),
(8, 9),
(8, 11);