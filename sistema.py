import banco_do_sistema
import sqlite3
import hashlib
from datetime import date

# -------------------------------
# Classe para gerenciar o Banco
# -------------------------------
class DatabaseManager:
    def __init__(self):
        self.db_name = banco_do_sistema

    def connect(self):
        return banco_do_sistema.conectar()

# -------------------------------
# Auth: registro e login
# -------------------------------
class Auth:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.usuario_logado = None  # dict: {id, tipo, ref}

    def hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def registrar_usuario(self, username, senha, tipo, referencia_id=None):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        senha_hash = self.hash_senha(senha)
        try:
            cursor.execute("""
                INSERT INTO usuarios (username, senha, tipo, referencia_id)
                VALUES (?, ?, ?, ?)
            """, (username, senha_hash, tipo, referencia_id))
            conn.commit()
            print(f"✅ Usuário '{username}' cadastrado como {tipo}.")
        except sqlite3.IntegrityError:
            print("⚠️ Nome de usuário já existe.")
        finally:
            conn.close()

    def login(self, username, senha):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        senha_hash = self.hash_senha(senha)
        cursor.execute("SELECT id, tipo, referencia_id FROM usuarios WHERE username=? AND senha=?",
                       (username, senha_hash))
        result = cursor.fetchone()
        conn.close()
        if result:
            self.usuario_logado = {"id": result[0], "tipo": result[1], "ref": result[2]}
            print(f"🔐 Logado como {result[1].upper()}.")
            return True
        else:
            print("❌ Usuário ou senha incorretos.")
            return False

    def logout(self):
        self.usuario_logado = None
        print("🚪 Sessão encerrada.")


# -------------------------------
# Vagas: controle de capacidade
# -------------------------------
class Vagas:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def vagas_disponiveis(self, curso):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT total_vagas, vagas_ocupadas FROM vagas WHERE curso=?", (curso,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return max(0, row[0] - row[1])
        return 0

    def ocupar_vaga(self, curso):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE vagas SET vagas_ocupadas = vagas_ocupadas + 1 WHERE curso=? AND vagas_ocupadas < total_vagas",
                       (curso,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected == 1  # True se vaga ocupada

    def liberar_vaga(self, curso):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE vagas SET vagas_ocupadas = vagas_ocupadas - 1 WHERE curso=? AND vagas_ocupadas > 0",
                       (curso,))
        conn.commit()
        conn.close()

    def listar_vagas(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT curso, total_vagas, vagas_ocupadas FROM vagas")
        dados = cursor.fetchall()
        conn.close()
        print("\n📊 Vagas por curso:")
        for c in dados:
            disponiveis = c[1] - c[2]
            print(f"- {c[0]}: {disponiveis} vagas disponíveis de {c[1]} (ocupadas: {c[2]})")

    def ajustar_vagas(self, curso, novo_total):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE vagas SET total_vagas=? WHERE curso=?", (novo_total, curso))
        conn.commit()
        conn.close()
        print(f"✅ Total de vagas para {curso} atualizado para {novo_total}.")

# -------------------------------
# Aluno: cadastro, listagens, etc.
# -------------------------------
class Aluno:
    def __init__(self, db_manager, vagas_manager=None):
        self.db_manager = db_manager
        self.vagas_manager = vagas_manager

    def cadastrar_aluno(self, nome, data_nascimento, genero, bairro, numero_bilhete, turma, curso, media_certificado):
        """
        Regista o aluno na tabela alunos e retorna o id gerado.
        Não faz operações sobre usuarios; isso fica para quem chamar (Auth.registrar_usuario).
        """
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO alunos (nome, data_nascimento, genero, bairro, numero_bilhete, turma, curso)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome, data_nascimento, genero, bairro, numero_bilhete, turma, curso))
            conn.commit()
            aluno_id = cursor.lastrowid
            print("✅ Aluno cadastrado com sucesso.")
            return aluno_id
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Erro ao cadastrar aluno: {e}")
            return None
        finally:
            conn.close()

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, turma, curso FROM alunos")
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            print("📭 Nenhum aluno cadastrado.")
            return
        print("\n📋 Lista de alunos:")
        for r in rows:
            print(f"Id: {r[0]} | Nome: {r[1]} | Turma: {r[2]} | Curso: {r[3]}")

    def obter_por_id(self, aluno_id):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE id=?", (aluno_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def obter_por_bilhete(self, numero_bilhete):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM alunos WHERE numero_bilhete=?", (numero_bilhete,))
        row = cursor.fetchone()
        conn.close()
        return row

    def ver_meus_dados(self, aluno_id):
        a = self.obter_por_id(aluno_id)
        if a:
            print("\n📌 Meus dados:")
            print(f"Id: {a[0]} | Nome: {a[1]} | Nascimento: {a[2]} | Gênero: {a[3]} | Bairro: {a[4]} | Bilhete: {a[5]} | Turma: {a[6]} | Curso: {a[7]}")
        else:
            print("⚠️ Aluno não encontrado.")


    def listar_alunos_de_um_curso(self,curso_id,turma_id):
        conn=self.db_manager.connect()
        cursor=conn.cursor()

        cursor.execute("SELECT id,nome FROM alunos WHERE curso=? AND turma=?",(curso_id,turma_id))
        registro=cursor.fetchall()

        print(f"📌Lista dos alunos da turma de {turma_id} no curso de {curso_id}")
        for i in registro:
            print(f"Id: {i[0]}| Nome: {i[1]}")
        conn.close()


    def atualizar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        print("1.Atualizar nome do aluno\n2.Atualizar curso do aluno\n3.Atualizar turma do aluno")
        opcao = int(input("Digite a sua opção: "))

        if opcao == 1:
            aluno.listar()
            aluno_id = int(input("Digite o id do aluno a ser atualizado: "))
            nome = input("Digite o novo nome do aluno: ").title()
            cursor.execute("UPDATE alunos SET nome=? WHERE id=?", (nome, aluno_id))

        elif opcao == 2:
            aluno.listar()
            aluno_id = int(input("Digite o id do aluno a  ser atualizado: "))
            curso = input("Digite o novo curso do aluno: ").title()
            cursor.execute("UPDATE alunos SET curso=? WHERE id=?", (curso, aluno_id))

        elif opcao == 3:
            aluno.listar()
            aluno_id = int(input("Digite o id do aluno a  ser atualizado: "))
            turma = input("Digite a nova turma do aluno: ").upper()
            cursor.execute("UPDATE alunos SET turma=? WHERE id=?", (turma, aluno_id))

        conn.commit()
        conn.close()
        print("✏️ Dados do aluno atualizados!")

    def deletar(self, aluno_id):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE nome=?", (aluno_id,))
        conn.commit()
        conn.close()
        print("🗑️ Aluno removido!")


# -------------------------------
# Professor
# -------------------------------
class Professor:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, nome, especialidade, telefone, email):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO professores (nome, especialidade, telefone, email)
                VALUES (?, ?, ?, ?)
            """, (nome, especialidade, telefone, email))
            conn.commit()
            print("✅ Professor cadastrado.")
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Erro: {e}")
        finally:
            conn.close()

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, especialidade FROM professores")
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            print("📭 Nenhum professor cadastrado.")
            return
        print("\n📋 Professores:")
        for r in rows:
            print(f"Id: {r[0]} | Nome: {r[1]} | Especialidade: {r[2]}")

    def obter_por_id(self, id_prof):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM professores WHERE id=?", (id_prof,))
        r = cursor.fetchone()
        conn.close()
        return r

    def listar_por_especialidade(self, especialidade_id):
        conn = self.db_manager.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT nome FROM professores WHERE especialidade=?", (especialidade_id,))
        registro = cursor.fetchall()

        print(f"📌Lista do professores da disciplina de {especialidade_id}")
        for i in registro:
            print(f"Nome: {i}")
        conn.close()

    def deletar(self, id_prof):
        conn = self.db_manager.connect()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM professores WHERE id=?", (id_prof,))
        conn.commit()
        conn.close()
        print("🗑️ Aluno removido!")



# -------------------------------
# Disciplina
# -------------------------------
class Disciplina:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, nome, curso, classe):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO disciplinas (nome, curso, classe) VALUES (?, ?, ?)", (nome, curso, classe))
        conn.commit()
        conn.close()
        print("✅ Disciplina adicionada.")

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, curso, classe FROM disciplinas")
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            print("📭 Nenhuma disciplina cadastrada.")
            return
        print("\n📚 Disciplinas:")
        for r in rows:
            print(f"Id: {r[0]} | Nome: {r[1]} | Curso: {r[2]} | Classe: {r[3]}")

    def listar_informatica(self, ):
        conn = self.db_manager.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM disciplinas WHERE curso== 'Informatica' ")
        disciplinas = cursor.fetchall()
        print("📌 Lista das Disciplinas do curso de Informatica")
        for i in disciplinas:
            print(f"Id: {i[0]}| Nome: {i[1]}| Curso: {i[2]}")
        conn.close()

    def listar_contabilidade(self, ):
        conn = self.db_manager.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM disciplinas WHERE curso== 'Contabilidade' ")
        disciplinas = cursor.fetchall()
        print("📌 Lista das Disciplinas do curso de Contabilidade")
        for i in disciplinas:
            print(f"Id: {i[0]}| Nome: {i[1]}| Curso: {i[2]}")
        conn.close()


# -------------------------------
# Matrícula
# -------------------------------
class Matricula:
    def __init__(self, db_manager, vagas_manager=None):
        self.db_manager = db_manager
        self.vagas_manager = vagas_manager

    def adicionar(self, aluno_id, curso, ano_letivo):
        # Verificar vaga antes
        if self.vagas_manager:
            disponiveis = self.vagas_manager.vagas_disponiveis(curso)
            if disponiveis <= 0:
                print(f"⚠️ Não há vagas disponíveis no curso {curso}.")
                return False

        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO matriculas (aluno_id, curso, ano_letivo) VALUES (?, ?, ?)",
                       (aluno_id, curso, ano_letivo))
        conn.commit()
        conn.close()
        # ocupar vaga
        if self.vagas_manager:
            ok = self.vagas_manager.ocupar_vaga(curso)
            if ok:
                print("✅ Matrícula feita e vaga reservada.")
            else:
                print("⚠️ Matrícula feita, mas não foi possível ocupar a vaga (concorrência).")
        else:
            print("✅ Matrícula feita.")
        return True

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, a.nome, m.curso, m.ano_letivo
            FROM matriculas m
            JOIN alunos a ON m.aluno_id = a.id
        """)
        rows = cursor.fetchall()
        conn.close()
        print("\n📋 Matrículas:")
        for r in rows:
            print(f"Id: {r[0]} | Aluno: {r[1]} | Curso: {r[2]} | Ano: {r[3]}")

    def listar_por_curso(self, curso):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, a.nome, m.curso
            FROM matriculas m
            JOIN alunos a ON m.aluno_id = a.id
            WHERE m.curso = ?
        """, (curso,))
        rows = cursor.fetchall()
        conn.close()
        print(f"\n📋 Matrículas em {curso}:")
        for r in rows:
            print(f"Id: {r[0]} | Aluno: {r[1]} | Curso: {r[2]}")


# -------------------------------
# Classe Notas
# -------------------------------
class Nota:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, aluno_id, disciplina_id, trimestre, nota_valor):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notas (aluno_id, disciplina_id, trimestre, nota)
            VALUES (?, ?, ?, ?)
        """, (aluno_id, disciplina_id, trimestre, nota_valor))
        conn.commit()
        conn.close()
        print("✅ Nota registrada.")

    def listar_por_aluno(self, aluno_id):
        self.gerar_boletim(aluno_id)

    def calcular_media_trimestre(self, aluno_id, trimestre):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(n.nota)
            FROM notas n
            WHERE n.aluno_id=? AND n.trimestre=?
        """, (aluno_id, trimestre))
        media = cursor.fetchone()[0]
        conn.close()
        return round(media, 2) if media else None

    def calcular_media_final(self, aluno_id):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT AVG(n.nota)
            FROM notas n
            WHERE n.aluno_id=?
        """, (aluno_id,))
        media = cursor.fetchone()[0]
        conn.close()
        return round(media, 2) if media else None

    def gerar_boletim(self, aluno_id):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.nome, n.trimestre, n.nota
            FROM notas n
            JOIN disciplinas d ON n.disciplina_id = d.id
            WHERE n.aluno_id=?
            ORDER BY d.nome, n.trimestre
        """, (aluno_id,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("\n📘 Nenhuma nota encontrada.")
            return

        # Agrupar notas por disciplina
        boletim = {}
        for disciplina, trimestre, nota in rows:
            boletim.setdefault(disciplina, {}).setdefault(trimestre, []).append(nota)

        print("\n📊 BOLETIM ESCOLAR")
        print("-" * 60)
        print(f"{'Disciplina':20s} {'1º Tri':>8} {'2º Tri':>8} {'3º Tri':>8} {'Média':>8}")
        print("-" * 60)

        for disc, notas_tris in boletim.items():
            medias_tris = []
            for t in ["1º", "2º", "3º"]:
                notas = notas_tris.get(t, [])
                media_t = sum(notas) / len(notas) if notas else 0
                medias_tris.append(media_t)
            media_final_disc = round(sum(medias_tris) / len([m for m in medias_tris if m > 0]), 2) if any(medias_tris) else 0
            print(f"{disc:20s} {medias_tris[0]:8.1f} {medias_tris[1]:8.1f} {medias_tris[2]:8.1f} {media_final_disc:8.1f}")

        print("-" * 60)
        media_final_geral = self.calcular_media_final(aluno_id)
        print(f"{'Média Final Geral:':40s} {media_final_geral:8.2f}")
        situacao = "🟢 Aprovado" if media_final_geral >= 10 else "🔴 Reprovado"
        print(f"{'Situação:':40s} {situacao}")
        print("-" * 60)


# -------------------------------
# Presenças
# -------------------------------
class Presenca:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def registrar(self, aluno_id, disciplina_id, data_aula, presente_bool):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO presencas (aluno_id, disciplina_id, data, presente)
            VALUES (?, ?, ?, ?)
        """, (aluno_id, disciplina_id, data_aula, int(bool(presente_bool))))
        conn.commit()
        conn.close()
        print("✅ Presença registrada.")

    def listar_todas(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.nome, d.nome, p.data, p.presente
            FROM presencas p
            JOIN alunos a ON p.aluno_id = a.id
            JOIN disciplinas d ON p.disciplina_id = d.id
        """)
        rows = cursor.fetchall()
        conn.close()
        print("\n📗 Presenças:")
        for r in rows:
            status = "Presente" if r[3] else "Faltou"
            print(f"Aluno: {r[0]} | Disciplina: {r[1]} | Data: {r[2]} | {status}")

    def listar_por_aluno(self, aluno_id):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.nome, p.data, p.presente
            FROM presencas p
            JOIN disciplinas d ON p.disciplina_id = d.id
            WHERE p.aluno_id=?
        """, (aluno_id,))
        rows = cursor.fetchall()
        conn.close()
        print("\n📗 Minhas presenças:")
        for r in rows:
            status = "Presente" if r[2] else "Faltou"
            print(f"Disciplina: {r[0]} | Data: {r[1]} | {status}")



# -------------------------------
# Utilitários: validações
# -------------------------------
def validar_idade_e_media(ano_nascimento, media):
    idade = date.today().year - ano_nascimento
    # regras: entre 15 e 18 (14<idade<=18) e média entre 12 e 20
    if 14 < idade <= 18 and 12 <= media <= 20:
        return True, idade
    return False, idade


# -------------------------------
# Inicialização e menu principal
# -------------------------------
def main():
    banco_do_sistema.criar_tabelas()

    db = DatabaseManager()
    vagas = Vagas(db)
    auth = Auth(db)

    aluno_model = Aluno(db, vagas)
    professor_model = Professor(db)
    disciplina_model = Disciplina(db)
    matricula_model = Matricula(db, vagas)
    nota_model = Nota(db)
    presenca_model = Presenca(db)

    print("===== SISTEMA ESCOLAR =====")
    print("1. Login")
    print("2. Registrar-se como ALUNO")
    print("3. Registrar Diretor (apenas 1x manual)")
    opc = input("Escolha: ").strip()

    if opc == "1":
        user = input("Usuário: ").strip()
        pwd = input("Senha: ").strip()
        if not auth.login(user, pwd):
            return

    elif opc == "2":
        # Auto-cadastro do aluno com validações e controle de vagas
        print("\n--- Cadastro de Aluno (auto) ---")
        nome = input("Nome completo: ").title()
        data_nasc = input("Data de nascimento (AAAA-MM-DD): ").strip()
        genero = input("Gênero (M/F): ").upper().strip()
        bairro = input("Bairro: ").title()
        bilhete = input("Número do bilhete: ").upper().strip()
        turma = input("Turma desejada: ").upper().strip()
        curso = input("Curso (Informatica/Contabilidade/Finanças): ").capitalize().strip()
        try:
            ano = int(data_nasc.split("-")[0])
        except Exception:
            print("⚠️ Data inválida.")
            return
        try:
            media = float(input("Média do certificado: ").strip())
        except Exception:
            print("⚠️ Média inválida.")
            return

        valido, idade = validar_idade_e_media(ano, media)
        if not valido:
            print(f"⚠️ Rejeitado: idade={idade} e média={media}. Regras: 15-18 anos e média 12-20.")
            return

        # Verificar vagas
        disponiveis = vagas.vagas_disponiveis(curso)
        if disponiveis <= 0:
            print(f"⚠️ Sem vagas no curso {curso}. Tente outro curso mais tarde.")
            return

        # Cadastrar aluno
        aluno_id = aluno_model.cadastrar_aluno(nome, data_nasc, genero, bairro, bilhete, turma, curso, media)
        if not aluno_id:
            return

        # Criar credenciais para o aluno (username = bilhete, senha definida pelo aluno)
        username = input("Escolha um nome de usuário (ex: seu bilhete): ").strip()
        senha = input("Escolha uma senha segura: ").strip()
        auth.registrar_usuario(username, senha, "aluno", referencia_id=aluno_id)

        # Matricular aluno automaticamente e ocupar vaga
        ano_letivo = input("Ano letivo para matrícula (ex: 2025): ").strip()
        matricula_ok = matricula_model.adicionar(aluno_id, curso, ano_letivo)
        if matricula_ok:
            print("🎉 Cadastro e matrícula concluídos! Faça login com seu usuário.")
        return

    elif opc == "3":
        # Registrar diretor — operação manual inicial
        print("\n--- Registrar Diretor ---")
        username = input("Usuário do diretor: ").strip()
        senha = input("Senha do diretor: ").strip()
        auth.registrar_usuario(username, senha, "diretor")
        print("✅ Diretor criado. Faça login.")
        return

    else:
        print("⚠️ Opção inválida.")
        return

    # Após login, direcionar por tipo
    tipo = auth.usuario_logado["tipo"]
    ref = auth.usuario_logado["ref"]  # para aluno/ professor ligação

    # ---------- MENU PARA DIRETOR ----------
    if tipo == "diretor":
        while True:
            print("\n=== MENU DIRETOR ===")
            print("1. Gerenciar Alunos")
            print("2. Gerenciar Professores")
            print("3. Gerenciar Disciplinas")
            print("4. Gerenciar Matrículas")
            print("5. Gerenciar Notas")
            print("6. Gerenciar Presenças")
            print("7. Gerenciar Vagas")
            print("8. Criar usuário (professor/aluno)")
            print("9. Sair")
            escolha = input("Escolha: ").strip()

            if escolha == "1":
                while True:
                    print("\n-- Alunos --")
                    print("1. Listar alunos")
                    print("2. Ver dados do aluno por ID")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        aluno_model.listar()
                    elif s == "2":
                        aid = int(input("ID do aluno: "))
                        aluno_model.ver_meus_dados(aid)
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "2":
                while True:
                    print("\n-- Professores --")
                    print("1. Cadastrar professor")
                    print("2. Listar professores")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        nome = input("Nome: ").title()
                        esp = input("Especialidade: ").title()
                        tel = input("Telefone: ")
                        email = input("Email: ")
                        professor_model.adicionar(nome, esp, tel, email)
                    elif s == "2":
                        professor_model.listar()
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "3":
                while True:
                    print("\n-- Disciplinas --")
                    print("1. Cadastrar disciplina")
                    print("2. Listar disciplinas")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        nome = input("Nome da disciplina: ").title()
                        curso = input("Curso: ").title()
                        classe = input("Classe: ").upper()
                        disciplina_model.adicionar(nome, curso, classe)
                    elif s == "2":
                        disciplina_model.listar()
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "4":
                while True:
                    print("\n-- Matrículas --")
                    print("1. Listar matrículas")
                    print("2. Matricular aluno manualmente")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        matricula_model.listar()
                    elif s == "2":
                        aluno_model.listar()
                        aid = int(input("ID do aluno: "))
                        curso = input("Curso: ").title()
                        ano = input("Ano letivo: ").strip()
                        matricula_model.adicionar(aid, curso, ano)
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "5":
                while True:
                    print("\n-- Notas --")
                    print("1. Adicionar nota")
                    print("2. Listar todas as notas")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        aluno_model.listar()
                        aid = int(input("ID do aluno: "))
                        disciplina_model.listar()
                        did = int(input("ID da disciplina: "))
                        tri = input("Trimestre: ")
                        val = float(input("Nota (0-20): "))
                        nota_model.adicionar(aid, did, tri, val)
                    elif s == "2":
                        aluno_model.listar()
                        aid = int(input("ID do aluno: "))
                        nota_model.listar_por_aluno(aid)
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "6":
                while True:
                    print("\n-- Presenças --")
                    print("1. Registrar presença")
                    print("2. Listar presenças")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        aluno_model.listar()
                        aid = int(input("ID do aluno: "))
                        disciplina_model.listar()
                        did = int(input("ID da disciplina: "))
                        data_aula = input("Data (AAAA-MM-DD): ")
                        falta = input("Faltou? (S/N): ").upper()
                        presenca_model.registrar(aid, did, data_aula, False if falta == "S" else True)
                    elif s == "2":
                        presenca_model.listar_todas()
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "7":
                while True:
                    print("\n-- Vagas --")
                    print("1. Listar vagas")
                    print("2. Ajustar total de vagas por curso")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        vagas.listar_vagas()
                    elif s == "2":
                        curso = input("Curso: ").title()
                        novo = int(input("Novo total de vagas: "))
                        vagas.ajustar_vagas(curso, novo)
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "8":
                # Criar usuário professor/aluno (diretor cria credenciais)
                print("\nCriar usuário:")
                tipo_u = input("Tipo (professor/aluno): ").strip().lower()
                if tipo_u not in ["professor", "aluno"]:
                    print("⚠️ Tipo inválido.")
                else:
                    if tipo_u == "aluno":
                        # deve existir aluno previamente (ou criar)
                        aluno_model.listar()
                        aid = int(input("ID do aluno (ou 0 para cancelar): "))
                        if aid == 0:
                            continue
                        username = input("Username: ").strip()
                        senha = input("Senha: ").strip()
                        auth.registrar_usuario(username, senha, "aluno", referencia_id=aid)
                    else:
                        # professor - sem referência
                        username = input("Username: ").strip()
                        senha = input("Senha: ").strip()
                        auth.registrar_usuario(username, senha, "professor")
            elif escolha == "9":
                print("👋 Saindo...")
                auth.logout()
                break
            else:
                print("⚠️ Opção inválida.")

    # ---------- MENU PARA PROFESSOR ----------
    elif tipo == "professor":
        while True:
            print("\n=== MENU PROFESSOR ===")
            print("1. Listar alunos")
            print("2. Gerenciar notas")
            print("3. Gerenciar presenças")
            print("4. Sair")
            escolha = input("Escolha: ").strip()

            if escolha == "1":
                aluno_model.listar()

            elif escolha == "2":
                while True:
                    print("\n-- Notas (Professor) --")
                    print("1. Adicionar nota")
                    print("2. Listar todas as notas")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        aluno_model.listar()
                        aid = int(input("ID do aluno: "))
                        disciplina_model.listar()
                        did = int(input("ID da disciplina: "))
                        tri = input("Trimestre: ")
                        val = float(input("Nota (0-20): "))
                        nota_model.adicionar(aid, did, tri, val)
                    elif s == "2":
                        nota_model.listar_todas()
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "3":
                while True:
                    print("\n-- Presenças (Professor) --")
                    print("1. Registrar presença")
                    print("2. Listar presenças")
                    print("3. Voltar")
                    s = input("Escolha: ").strip()
                    if s == "1":
                        aluno_model.listar()
                        aid = int(input("ID do aluno: "))
                        disciplina_model.listar()
                        did = int(input("ID da disciplina: "))
                        data_aula = input("Data (AAAA-MM-DD): ")
                        falta = input("Faltou? (S/N): ").upper()
                        presenca_model.registrar(aid, did, data_aula, False if falta == "S" else True)
                    elif s == "2":
                        presenca_model.listar_todas()
                    elif s == "3":
                        break
                    else:
                        print("⚠️ Opção inválida.")

            elif escolha == "4":
                auth.logout()
                break
            else:
                print("⚠️ Opção inválida.")

    # ---------- MENU PARA ALUNO ----------
    elif tipo == "aluno":
        # ref contém o id do aluno (referencia_id) preenchido ao criar o usuário
        aluno_id = ref
        if not aluno_id:
            print("⚠️ Conta de aluno sem referência a registro. Contata um administrador.")
            return

        while True:
            print("\n=== MENU ALUNO ===")
            print("1. Ver meus dados")
            print("2. Ver minhas notas")
            print("3. Ver minhas presenças")
            print("4. Sair")
            escolha = input("Escolha: ").strip()

            if escolha == "1":
                aluno_model.ver_meus_dados(aluno_id)
            elif escolha == "2":
                nota_model.listar_por_aluno(aluno_id)
            elif escolha == "3":
                presenca_model.listar_por_aluno(aluno_id)
            elif escolha == "4":
                auth.logout()
                break
            else:
                print("⚠️ Opção inválida.")

    else:
        print("⚠️ Tipo de usuário desconhecido. Contata o administrador.")


if __name__ == "__main__":
    main()

