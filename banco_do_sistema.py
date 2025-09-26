import sqlite3

def conectar():
    return sqlite3.connect("banco_escolar.db")


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    # Tabela de alunos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
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

    # Tabela de professores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS professores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            especialidade TEXT,
            telefone TEXT,
            email TEXT UNIQUE
        )
    """)

    # Tabela de disciplinas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            curso TEXT,
            classe TEXT
        )
    """)

    # Tabela de matrículas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matriculas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            curso TEXT NOT NULL,
            ano_letivo TEXT NOT NULL,
            FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE
        )
    """)

    # Tabela de notas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            trimestre TEXT NOT NULL,
            nota REAL CHECK(nota >= 0 AND nota <= 20),
            FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY(disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
        )
    """)

    # Tabela de presenças
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS presencas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            disciplina_id INTEGER NOT NULL,
            data DATE NOT NULL,
            presente BOOLEAN NOT NULL CHECK (presente IN (0,1)),
            FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
            FOREIGN KEY(disciplina_id) REFERENCES disciplinas(id) ON DELETE CASCADE
        )
    """)

    # Tabela de vagas (controle de capacidade por curso)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vagas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            curso TEXT UNIQUE NOT NULL,
            total_vagas INTEGER NOT NULL,
            vagas_ocupadas INTEGER DEFAULT 0
        )
    """)

    # Inserir cursos padrão, se ainda não existirem
    cursos = [("Informatica", 80), ("Contabilidade", 80), ("Finanças", 80)]
    for c, v in cursos:
        cursor.execute("INSERT OR IGNORE INTO vagas (curso, total_vagas) VALUES (?, ?)", (c, v))

    # Tabela de usuários (login)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('aluno', 'professor', 'diretor')) NOT NULL,
            referencia_id INTEGER
        )
    """)

    conn.commit()
    conn.close()
print("✅ Banco e tabelas criados com sucesso!")

