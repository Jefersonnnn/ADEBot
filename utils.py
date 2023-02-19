from datetime import datetime


def validate_date_and_convert(data_str: str, horario: str = None) -> datetime or datetime.date:
    try:
        if horario:
            data_obj = datetime.strptime(data_str + ' ' + horario, '%d/%m/%Y %H:%M')
        else:
            data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
        # Verifica se a data é uma data válida
        if data_obj.year < 1900 or data_obj.year > 2100:
            return False
        return data_obj
    except ValueError:
        # Se a conversão falhar, a string não está no formato correto
        return False
