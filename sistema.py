import banco_do_sistema

# -------------------------------
# Classe para gerenciar o Banco
# -------------------------------
class DatabaseManager:
    def __init__(self):
        self.db_name = banco_do_sistema

    def connect(self):
        return banco_do_sistema.conectar()


# -------------------------------
# Classe Aluno
# -------------------------------
class Aluno:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, nome, data_nascimento, genero, bairro, numero_bilhete, turma, curso):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO alunos (nome, data_nascimento, genero, bairro, numero_bilhete, turma, curso)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, data_nascimento, genero, bairro, numero_bilhete, turma, curso))
        conn.commit()
        conn.close()
        print("✅ Aluno cadastrado!")

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id,nome,turma,curso FROM alunos")
        alunos = cursor.fetchall()

        print("📌Lista de alunos da escola")
        for i in alunos:
            print(f"Id: {i[0]}|Nome: {i[1]}| Turma: {i[2]}|Curso: {i[3]}")
        conn.close()
    
    def listar_alunos_de_um_curso(self,curso_id,turma_id):
        conn=self.db_manager.connect()
        cursor=conn.cursor()

        cursor.execute("SELECT id,nome FROM alunos WHERE curso=? AND turma=?",(curso_id,turma_id))
        registro=cursor.fetchall()

        print(f"Lista dos alunos da turma de {turma_id} no curso de {curso_id}")
        for i in registro:
            print(f"Id: {i[0]}| Nome: {i[1]}")
        conn.close()


    def atualizar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        print("1.Atualizar nome do aluno\n2.Atualizar curso do aluno\n3.Atualizar turma do aluno")
        opcao=int(input("Digite a sua opção: "))

        if opcao==1:
            aluno.listar()
            aluno_id=int(input("Digite o id do aluno a ser atualizado: "))
            nome=input("Digite o novo nome do aluno: ").title()
            cursor.execute("UPDATE alunos SET nome=? WHERE id=?", (nome, aluno_id))

        elif opcao==2:
            aluno.listar()
            aluno_id=int(input("Digite o id do aluno a  ser atualizado: "))
            curso=input("Digite o novo curso do aluno: ").title()
            cursor.execute("UPDATE alunos SET curso=? WHERE id=?", (curso, aluno_id))
        
        elif opcao==3:
            aluno.listar()
            aluno_id=int(input("Digite o id do aluno a  ser atualizado: "))
            turma=input("Digite a nova turma do aluno: ").upper()
            cursor.execute("UPDATE alunos SET turma=? WHERE id=?", (turma, aluno_id))
        
        conn.commit()
        conn.close()
        print("✏️ Dados do aluno atualizados!")

    def deletar(self, aluno_id):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alunos WHERE id=?", (aluno_id,))
        conn.commit()
        conn.close()
        print("🗑️ Aluno removido!")


# -------------------------------
# Classe Professor
# -------------------------------
class Professor:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, nome, especialidade, telefone, email):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO professores (nome, especialidade, telefone, email)
            VALUES (?, ?, ?, ?)
        """, (nome, especialidade, telefone, email))
        conn.commit()
        conn.close()
        print("✅ Professor cadastrado!")

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM professores")
        professores = cursor.fetchall()
        conn.close()
        return professores


# -------------------------------
# Classe Disciplina
# -------------------------------
class Disciplina:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, nome, curso):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO disciplinas (nome, curso)
            VALUES (?, ?)
        """, (nome, curso))
        conn.commit()
        conn.close()
        print("✅ Disciplina cadastrada!")

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM disciplinas")
        disciplinas = cursor.fetchall()
        conn.close()
        return disciplinas


# -------------------------------
# Classe Matrícula
# -------------------------------
class Matricula:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, aluno_id, curso, ano_letivo):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO matriculas (aluno_id, curso, ano_letivo)
            VALUES (?, ?, ?)
        """, (aluno_id, curso, ano_letivo))
        conn.commit()
        conn.close()
        print("✅ Matrícula efetuada!")

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, a.nome, m.curso, m.ano_letivo
            FROM matriculas m
            JOIN alunos a ON m.aluno_id = a.id
        """)
        matriculas = cursor.fetchall()
        conn.close()
        return matriculas


# -------------------------------
# Classe Notas
# -------------------------------
class Nota:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def adicionar(self, aluno_id, disciplina_id, trimestre, nota):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notas (aluno_id, disciplina_id, trimestre, nota)
            VALUES (?, ?, ?, ?)
        """, (aluno_id, disciplina_id, trimestre, nota))
        conn.commit()
        conn.close()
        print("✅ Nota registrada!")

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT n.id, a.nome, d.nome, n.trimestre, n.nota
            FROM notas n
            JOIN alunos a ON n.aluno_id = a.id
            JOIN disciplinas d ON n.disciplina_id = d.id
        """)
        notas = cursor.fetchall()
        conn.close()
        return notas


# -------------------------------
# Classe Presença
# -------------------------------
class Presenca:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def registrar(self, aluno_id, disciplina_id, data, presente):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO presencas (aluno_id, disciplina_id, data, presente)
            VALUES (?, ?, ?, ?)
        """, (aluno_id, disciplina_id, data, presente))
        conn.commit()
        conn.close()
        print("✅ Presença registrada!")

    def listar(self):
        conn = self.db_manager.connect()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, a.nome, d.nome, p.data, p.presente
            FROM presencas p
            JOIN alunos a ON p.aluno_id = a.id
            JOIN disciplinas d ON p.disciplina_id = d.id
        """)
        presencas = cursor.fetchall()
        conn.close()
        return presencas


# -------------------------------
# Testando tudo
# -------------------------------
banco_do_sistema.criar_tabbelas()

if __name__ == "__main__":
    db = DatabaseManager()

    aluno = Aluno(db)
    professor = Professor(db)
    disciplina = Disciplina(db)
    matricula = Matricula(db)
    nota = Nota(db)
    presenca = Presenca(db)

    print("""===BENVINDO AO INSTIUTO POLITECNICO KUNDI PAIHAMA Nº266===\n
    ===AQUI NOS LECIONAMOS VARIOS CURSOS TECNICOS E FOCADOS NA TECNOLOGIA===""")

    print("================MENU DE OPÇÕES================")
    print("1.Gerenciar alunos\n2.Gerencimento de professores\n3.Gerenciar Disciplina")
    print("4.Gerenciar Matriculas de alunos\n5.Gerenciar Notas\n6.Gerenciar presenças\n7.Sair do sistema")

    opcao=int(input("Digite a sua opção: "))
    match opcao:
        # Criando registros
        case 1:
            from datetime import date

            while True:
                print("1.Cadastrar alunos\n2.Litar alunos\n3.Listar alunos de um curso")
                print("4.Atualizar um aluno\n5.Deletar um aluno\n6.Sair")
                opcao=int(input("Digite a sua opção: "))

                if opcao==1:
                    nome=input("Digite o seu nome: ").title()
                    data_nascimento=input("Digite a sua data de nascimento (Ano-Mes-Dia): ")
                    genero=input("Digite o seu genero (M/F): ").upper()
                    bairro=input("Digite o seu bairro: ").title()
                    bilhete=input("Digite o seu numero de bilhete: ").upper()
                    ano=int(input("Digite o ano do seu nascimento de novo: "))
                    media=float(input("Digite a media do seu certificado: "))

                    idade=date.today().year-ano
                    if 14<idade<18 and 12<=media<=20:
                        curso = input("Digite o curso que ques fazer (Informatica/Contabilidade/Finanças): ").capitalize()
                        if curso in ["Informatica","Contabilidade","Finanças"]:
                            turma=input("Digite a turma do aluno: ").upper()
                            aluno.adicionar(nome, data_nascimento, genero, bairro, bilhete, turma, curso)
                        else:
                            print("Curso invalido. Tente novamente")
                    else:
                        print("Idade ou media fora da regra de acesso a escola")

                elif opcao==2:
                    aluno.listar()

                elif opcao==3:
                    print("Ques ver alunos de que curso?: ")
                    print("1.Informatica\n2.Contabilidade\n3.Finanças")
                    opcao=int(input("Digite a sua opção: "))

                    if opcao==1:
                        turma_id=input("Digite o numero da turma para ver os alunos: ").upper()
                        curso_id="Informatica"
                        aluno.listar_alunos_de_um_curso(curso_id,turma_id)
                    
                    elif opcao==2:
                        turma_id=input("Digite o numero da turma para ver os alunos: ").upper()
                        curso_id="Contabilidade"
                        aluno.listar_alunos_de_um_curso(curso_id,turma_id)
                    
                    elif opcao==3:
                        turma_id=input("Digite o numero da turma para ver os alunos: ").upper()
                        curso_id="Finanças"
                        aluno.listar_alunos_de_um_curso(curso_id,turma_id)
                    
                    else:
                        print("Opção invalida")
                
                elif opcao==4:
                    aluno.atualizar()        

                    
                elif opcao==6:
                    break
        
        case 2:

            professor.adicionar("Maria Gomes", "Português", "923987654", "maria@email.com")
            disciplina.adicionar("Português", "Línguas")

            # Matrícula
            matricula.adicionar(1, "Informática", "2025")
            # Nota
            nota.adicionar(1, 1, "1º Trimestre", 15)
            # Presença
            presenca.registrar(1, 1, "2025-09-21", True)

    # Listando
    print("📌 Professores:", professor.listar())
    print("📌 Disciplinas:", disciplina.listar())
    print("📌 Matrículas:", matricula.listar())
    print("📌 Notas:", nota.listar())
    print("📌 Presenças:", presenca.listar())
