import datetime
import decimal
import json


def default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, datetime.datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(obj, datetime.date):
        return obj.strftime("%Y-%m-%d")


def loads(s):
    """
    :param s:
    :return:
    """
    return json.loads(s)


def load(path):
    """
    :param path:
    :return:
    """
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def dumps(da):
    """
    :param da:
    :return:
    """
    return json.dumps(da, ensure_ascii=False).encode('utf8').decode('utf-8')


def dump(da, path):
    """
    :param da:
    :param path:
    :return:
    """
    with open(path, "w", encoding="utf-8") as f:
        # json.dump(da, f) # 写为一行
        json.dump(da, f, indent=2, sort_keys=True, ensure_ascii=False, default=default)  # 写为多行