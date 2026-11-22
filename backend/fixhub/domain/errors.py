"""Erros de validação do domínio FixHub."""


class ErroDominio(Exception):
    """Classe base para erros de regra de negócio."""


class DadosInvalidos(ErroDominio):
    """Indica que os dados não atendem às regras do domínio."""


class EmailDuplicado(ErroDominio):
    """Indica que já existe uma conta usando o e-mail informado."""


class CredenciaisInvalidas(ErroDominio):
    """Indica que o e-mail ou a senha não correspondem a uma conta."""


class SemPermissao(ErroDominio):
    """Indica que o perfil não pode executar a operação solicitada."""


class RecursoNaoEncontrado(ErroDominio):
    """Indica que o registro solicitado não existe mais."""


class TransicaoInvalida(DadosInvalidos):
    """Indica uma mudança de estado não permitida para o chamado."""
