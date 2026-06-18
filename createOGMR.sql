
-- Bloqueio ao acesso a internet da porta x 
-- Desbloqueio ao acesso a internet da porta x
-- Desbloqueio ao acesso a internet da porta x (AUTOMÁTICO)
-- Avaliação de status das conexões
-- Consulta de informações do switch
CREATE SEQUENCE idAcao AS int INCREMENT BY 1; 
CREATE TYPE acao AS ENUM (
	'up',
	'down',
	'testing',
	'unknown',
	'dormant',
	'notPresent',
	'lowerLayerDown'
	);
CREATE TABLE acoes(
	idAcao INT NOT NULL PRIMARY KEY,
	idSala INT NOT NULL,
	porta INT NOT NULL,
	idProfessor INT NOT NULL,
	inicio TIMESTAMPTZ NOT NULL,
	fim TIMESTAMPTZ NOT NULL,
	tipoAcao acao NOT NULL
);

CREATE SEQUENCE idSala AS int INCREMENT BY 1;
CREATE TABLE salas(
	idSala INT PRIMARY KEY NOT NULL,
	nome VARCHAR(255) NOT NULL,
	gerente VARCHAR(17) NOT NULL
);

INSERT INTO salas VALUES (nextval('idSala'), 'F203')
I

CREATE SEQUENCE idPorta AS int INCREMENT BY 1;
CREATE TABLE portas(
	porta INT NOT NULL PRIMARY KEY,
	idSala INT REFERENCES salas (idSala)
);
SELECT * FROM portas;

CREATE SEQUENCE idProfessor AS int INCREMENT BY 1;
CREATE TABLE professores(
	idProfessor INT PRIMARY KEY NOT NULL,
	nomeProfessor VARCHAR(255) NOT NULL,
	senha VARCHAR(255) NOT NULL,
);

--DROP TABLE salas;