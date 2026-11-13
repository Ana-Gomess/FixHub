from werkzeug.security import generate_password_hash

class Usuario: 
    def __init__(self, nome: str, email: str, senha: str, perfil: str) -> None:
        self.nome = nome
        self.email = email
        self.senha_hash = generate_password_hash(senha) 
        if perfil not in ("morador", "administrador"):
            raise ValueError("O perfil deve ser morador ou administrador.")

        self.perfil = perfil