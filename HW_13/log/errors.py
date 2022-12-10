class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class ResponseCodeError(Exception):
    def __init(self, code):
        self.code = code

    def __str__(self):
        return 'Response code {} is not correct'.format(self.code)


class ResponseCodeLenError(ResponseCodeError):
    def __str__(self):
        return 'Response code {} length is not correct'.format(self.code)


class IncorrectDataRecivedError(Exception):
    def __str__(self):
        return 'Принято некорректное сообщение от удалённого компьютера.'


class NonDictInputError(Exception):
    def __str__(self):
        return 'Аргумент функции должен быть словарём.'


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}.'

