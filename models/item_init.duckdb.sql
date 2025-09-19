drop table if exists item;
CREATE or replace SEQUENCE seq_item_id START 1;
CREATE TABLE item (
        id INTEGER PRIMARY KEY DEFAULT NEXTVAL('seq_item_id'),
        titre VARCHAR NOT NULL unique,
        auteur VARCHAR,
        annee INTEGER,
        type VARCHAR(5) NOT NULL,
        genre VARCHAR,
        note INTEGER,
        other json,
)

insert into item (titre, auteur, annee, type, genre, note)
values
('Dream Team', 'Ludovic Girodon', 2024, 'LIVRE', 'Entreprise', 5),
('Fundamentals of Data Engineering', 'Joe Reis', 2023, 'LIVRE', 'Entreprise', 4)
;