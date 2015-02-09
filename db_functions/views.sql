
CREATE OR REPLACE VIEW latest_instruments AS
	SELECT i.*, document, processed_document FROM instruments  i
	JOIN  (SELECT govt_id, max(version) as version FROM instruments GROUP BY govt_id) s ON s.govt_id = i.govt_id and i.version = s.version
	JOIN documents d on d.id = i.id;


CREATE OR REPLACE VIEW titles AS
	SELECT trim(title) as name, id, type  from latest_instruments
	UNION
	SELECT trim(full_citation) as name, id, 'case' as type from cases;