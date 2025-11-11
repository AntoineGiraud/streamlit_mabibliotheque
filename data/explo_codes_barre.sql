

summarize from read_csv('C:\Users\antoi\Documents\data/open4goods-isbn-dataset.csv', sample_size=100000); --, encoding="latin-1");


----------------------------------------------------------------------------------------
-- isbn : codes barre des livres & BD
----------------------------------------------------------------------------------------
summarize from "C:\Users\antoi\Documents\data\codes_barre/isbn.parquet";

copy (
	select
	  isbn,
	  trim(title, '"') as title,
	  trim(editeur, '[]') as editeur,
	  format,
	  nb_page,
	  classification_decitre_1, classification_decitre_2, classification_decitre_3, souscategorie, souscategorie2,
	  --* exclude(isbn, title, editeur, format, nb_page)
	from "C:\Users\antoi\Documents\data\codes_barre/isbn.parquet"
	where classification_decitre_1 ilike 'bd%'
	-- order by 1
	order by classification_decitre_1, classification_decitre_2, title, editeur, isbn
) to "C:\Users\antoi\Documents\data\codes_barre/isbn_nudger_BD.parquet"

summarize "C:\Users\antoi\Documents\data\codes_barre/isbn_slim.parquet"


select
  isbn,
  title,
  editeur,
  format,
  nb_page,
  -- classification_decitre_1, classification_decitre_2, classification_decitre_3, souscategorie, souscategorie2,
  * exclude(isbn, title, editeur, format, nb_page,
  	last_updated, offers_count, min_price, min_price_compensation, currency, url)
from "C:\Users\antoi\Documents\data\codes_barre/isbn.parquet"
where isbn in (
  -- 3558380098027, -- jeu de société
  9782728928354,
  9782213028323,
  9782213717845,
  -- 8717418357423, -- dvd
  9782070386390,
  9781250784261, -- anglais
  9782204060639,
  9791033615293,
  9782234018778,
  9782728923847,
  -- BD
  9782808511650,
  9782884715249
)
order by 1;


-- explo des catégories
summarize
select classification_decitre_1, count(1) nb, min(isbn) isbn_min, max(isbn) isbn_max, count(1) nb
from "C:\Users\antoi\Documents\data\codes_barre/isbn.parquet"
where lower(classification_decitre_1) like 'bd%'
group by all
order by 1


----------------------------------------------------------------------------------------
-- gtin : codes barre divers hors livres
----------------------------------------------------------------------------------------

from "C:\Users\antoi\Documents\data\codes_barre/gtin.parquet" limit 10;

from "C:\Users\antoi\Documents\data\codes_barre/gtin.parquet"
where gtin in (
  3558380098027, -- jeu de société
  9782728928354, -- livre
  8717418357423, -- dvd
)
order by 1

-- explo des catégories
summarize
select categories, count(1) nb, min(gtin) gtin_min, max(gtin) gtin_max, count(1) nb
from "C:\Users\antoi\Documents\data\codes_barre/gtin.parquet"
where lower(categories) like '%jeu de societe%'
--where left(gtin::string, 4) = '3558'
group by all
order by 1

-- extrait jeux de société
copy (
	select gtin, brand, model, name, gs1_country, gtinType, categories
	from "C:\Users\antoi\Documents\data\codes_barre/gtin.parquet"
	where categories ilike '%jeu_ de societe%'
) to "C:\Users\antoi\Documents\data\codes_barre/gtin_jeuxDeSociete.parquet"
