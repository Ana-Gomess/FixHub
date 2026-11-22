"""Erros de validação do domínio FixHub."""


class ErroDominio(Exception):
    """Classe base para erros de regra de negócio."""


class DadosInvalidos(ErroDominio):
    """Indica que os dados não atendem às regras do domínio."""


class SemPermissao(ErroDominio):
    """Indica que o perfil não pode executar a operação solicitada."""


class TransicaoInvalida(DadosInvalidos):
    """Indica uma mudança de estado não permitida para o chamado."""
