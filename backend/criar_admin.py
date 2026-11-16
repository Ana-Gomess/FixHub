from database import conectar_banco
from werkzeug.security import generate_password_hash

conexao = conectar_banco()
senha_criptografada = generate_password_hash("admin123")

conexao.execute(
    "INSERT OR IGNORE INTO usuarios (nome, email, senha_hash, perfil) VALUES (?, ?, ?, ?)",
    ("Administrador FixHub", "admin@fixhub.com", senha_criptografada, "administrador")
)

conexao.commit()
conexao.close()
print("Administrador criado com sucesso!")