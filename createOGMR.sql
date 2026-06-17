
-- Bloqueio ao acesso a internet da porta x 
-- Desbloqueio ao acesso a internet da porta x
-- Desbloqueio ao acesso a internet da porta x (AUTOMÁTICO)
-- Avaliação de status das conexões
-- Consulta de informações do switch



CREATE SEQUENCE idSala AS int INCREMENT BY 1;
CREATE TABLE salas(
	idSala INT PRIMARY KEY NOT NULL,
	nome VARCHAR(255) NOT NULL,
	gerente VARCHAR(17) -- MAC-ADDR
);

INSERT INTO salas VALUES (nextval('idSala'), 'F203');
INSERT INTO salas VALUES (nextval('idSala'), 'F301');
ALTER TABLE salas ADD COLUMN gerente VARCHAR(17);
SELECT * FROM salas;

CREATE SEQUENCE idPorta AS int INCREMENT BY 1;
CREATE TABLE portas(
	porta INT NOT NULL PRIMARY KEY,
	idSala INT REFERENCES salas (idSala)
);



INSERT INTO portas VALUES (nextval('idPorta'), 2);
SELECT * FROM portas;

CREATE SEQUENCE idProfessor AS int INCREMENT BY 1;
CREATE TABLE professores(
	idProfessor INT PRIMARY KEY NOT NULL,
	nomeProfessor VARCHAR(255) NOT NULL,
	senha VARCHAR(255) NOT NULL
);
SELECT * FROM professores;

ALTER TABLE professores DROP COLUMN mac;
INSERT INTO professores VALUES
	(nextval('idProfessor'), 'Cristiano', 'cristiano')

--DROP TABLE salas;