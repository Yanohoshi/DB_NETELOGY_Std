create table if not exists Genres (
id serial primary key not null,
name varchar(100) not null
);

create table if not exists Artists (
	id serial primary key not null,
	name varchar(100) not null 
);

create table if not exists Albums (
	id serial primary key not null,
	title varchar(100) not null,
	release_year integer not null
);

create table if not exists Tracks (
	id serial primary key not null,
	title varchar(100) not null,
	duration integer not null,
	album_id integer not null references Albums(id)
);

create table if not exists Collections(
	id serial primary key not null,
	title varchar(100) not null,
	release_year integer not null
);

create table if not exists ArtistGenres (
	genre_id integer not null references Genres(id),
	artist_id integer not null references Artists(id),
	constraint ag primary key (genre_id, artist_id)
);

create table if not exists AlbumArtists (
	artist_id integer not null references Artists(id),
	album_id integer not null references Albums(id),
	constraint aa primary key (artist_id, album_id)
);

create table if not exists CollectionTracks (
	colletion_id integer not null references Collections(id),
	track_id integer not null references Tracks(id),
	constraint ct primary key (colletion_id, track_id)
);