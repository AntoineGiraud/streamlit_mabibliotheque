-- drop table if exists item;
CREATE TABLE item (
    id INTEGER PRIMARY KEY,
    barcode VARCHAR,
    titre VARCHAR NOT NULL,
    auteur VARCHAR,
    annee INTEGER,
    type VARCHAR(5) NOT NULL,
    genre VARCHAR,
    note INTEGER,
    other json,
    UNIQUE(type, titre, auteur) ON CONFLICT FAIL,
    unique(type, barcode) ON CONFLICT FAIL
);

insert into item (titre, auteur, annee, type, genre, note)
values
('Dream Team', 'Ludovic Girodon', 2024, 'LIVRE', 'Entreprise', 5),
('Fundamentals of Data Engineering', 'Joe Reis', 2023, 'LIVRE', 'Entreprise', 4)
;

select * from item;
