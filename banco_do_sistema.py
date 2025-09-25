import sqlite3

def conectar():
    return sqlite3.connect("banco_escolar.db")

def criar_tabbelas():
    conn=conectar()
    cursor=conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data_nascimento DATE NOT NULL,
            genero TEXT CHECK(genero IN ('M', 'F')),
            bairro TEXT,
            numero_bilhete TEXT UNIQUE,
            turma TEXT,
            curso TEXT
        )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especialidade TEXT,
            telefone TEXT,
            email TEXT UNIQUE
        )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            curso TEXT
        )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS matriculas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            curso TEXT NOT NULL,
            ano_letivo TEXT NOT NULL,
            FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            trimestre TEXT NOT NULL,
            nota REAL CHECK(nota >= 0 AND nota <= 20),
            FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY(disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""CREATE TABLE IF NOT EXISTS presencas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            data DATE NOT NULL,
            presente BOOLEAN NOT NULL CHECK (presente IN (0,1)),
            FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY(disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()



