


class ErroDominio(Exception):
    pass


class DadosInvalidos(ErroDominio):
    pass


class EmailDuplicado(ErroDominio):
    pass


class CredenciaisInvalidas(ErroDominio):
    pass


class SemPermissao(ErroDominio):
    pass


class RecursoNaoEncontrado(ErroDominio):
    pass


class TransicaoInvalida(DadosInvalidos):
    pass
