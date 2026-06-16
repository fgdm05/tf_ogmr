CREATE SEQUENCE idCon AS int INCREMENT BY 1;

CREATE SEQUENCE idRegistro AS int INCREMENT BY 1;
CREATE TABLE registros(
	idRegistro INT PRIMARY KEY NOT NULL,
	inicio TIMESTAMPTZ NOT NULL,
	fim TIMESTAMPTZ NOT NULL,
	idCon INT NOT NULL REFERENCES conexoes (idCon)
	acao VARCHAR(255) NOT NULL
);
-- Bloqueio ao acesso a internet da porta x 
-- Desbloqueio ao acesso a internet da porta x
-- Desbloqueio ao acesso a internet da porta x (AUTOMÁTICO)
-- Avaliação de status das conexões
-- Consulta de informações do switch



CREATE SEQUENCE idSala AS int INCREMENT BY 1;
CREATE TABLE salas(
	idSala INT PRIMARY KEY NOT NULL,
	nome VARCHAR(255) NOT NULL
);

CREATE SEQUENCE idPorta AS int INCREMENT BY 1;
CREATE TABLE portas(
	porta INT NOT NULL PRIMARY KEY,
	idSala INT REFERENCES salas (idSala)
);

CREATE TABLE conexoes(
	idCon INT PRIMARY KEY NOT NULL,
	porta INT NOT NULL REFERENCES portas (porta),
	ip VARCHAR(15) NOT NULL,
	mac VARCHAR(17) NOT NULL
);

CREATE TABLE gerenciamento(
	idGerenciamento INT NOT NULL PRIMARY KEY,
	idSala INT NOT NULL,
	idProfessor INT NOT NULL
);

CREATE SEQUENCE idProfessor AS int INCREMENT BY 1;
CREATE TABLE professores(
	idProfessor INT PRIMARY KEY NOT NULL,
	nomeProfessor VARCHAR(255) NOT NULL,
	idSala INT REFERENCES salas (idSala)
);

--DROP TABLE salas;