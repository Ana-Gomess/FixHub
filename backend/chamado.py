class Chamado:
    def __init__(
            self,
            titulo: str,
            descricao: str,
            localizacao: str,
            morador_id: int,
            estado: str = "Aberto",
    ) -> None:
        self.titulo = titulo
        self.descricao = descricao
        self.localizacao = localizacao
        self.estado = estado
        self.morador_id = morador_id