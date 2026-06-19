
-- Bloqueio ao acesso a internet da porta x 
-- Desbloqueio ao acesso a internet da porta x
-- Desbloqueio ao acesso a internet da porta x (AUTOMÁTICO)
-- Avaliação de status das conexões
-- Consulta de informações do switch


CREATE SEQUENCE idSala AS int INCREMENT BY 1;
CREATE TABLE salas(
	idSala INT PRIMARY KEY NOT NULL,
	nome VARCHAR(255) NOT NULL,
	gerente VARCHAR(17) NOT NULL
);
SELECT * FROM salas;
INSERT INTO salas VALUES (nextval('idSala'), 'F203')
INSERT INTO salas VALUES (nextval('idSala'), 'F301')

CREATE SEQUENCE idPorta AS int INCREMENT BY 1;
CREATE TABLE portas(
	porta INT NOT NULL PRIMARY KEY,
	idSala INT REFERENCES salas (idSala),
	fechavel INT NOT NULL
);
SELECT * FROM portas;

CREATE SEQUENCE idProfessor AS int INCREMENT BY 1;
CREATE TABLE professores(
	idProfessor INT PRIMARY KEY NOT NULL,
	nomeProfessor VARCHAR(255) NOT NULL,
	senha VARCHAR(255) NOT NULL,
);

CREATE SEQUENCE idAcao AS int INCREMENT BY 1; 
CREATE TABLE acoes(
	idAcao INT NOT NULL PRIMARY KEY,
	acao INT NOT NULL,
	porta INT NOT NULL REFERENCES portas (porta),
	inicio TIMESTAMPTZ NOT NULL,
	fim TIMESTAMPTZ,
	idProfessor INT NOT NULL REFERENCES professores(idProfessor),
	idSala INT NOT NULL REFERENCES salas(idSala)
);