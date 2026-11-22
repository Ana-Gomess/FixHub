"""Erros de validação do domínio FixHub."""


class ErroDominio(Exception):
    """Classe base para erros de regra de negócio."""


class DadosInvalidos(ErroDominio):
    """Indica que os dados não atendem às regras do domínio."""
