"""
Скрипт для генерации DataSet huggingface.co
Dmitriy007/restor_punct_Lenta2

wget https://github.com/yutkin/Lenta.Ru-News-Dataset/releases/download/v1.1/lenta-ru-news.csv.bz2
"""

from corus import load_lenta2
import pandas as pd
import json
import re
from tqdm import tqdm


def pd2json():
    """
  1. DataSet Lenta2 -> pandas.DataFrame
  2. pandas.DataFrame -> data.csv
  """
    path = r'c:\Users\D.Vetrov\Downloads\lenta-ru-news.csv.bz2'
    records = load_lenta2(path)
    # records --> DataFrame
    df = pd.DataFrame(records)
    # Удаление столбцов. Оставляем столбец № 2
    new_df = df.drop(df.columns[[0, 1, 3, 4, 5]], axis=1)
    # Переименовывание столбца
    new_df.columns = ['text']
    # new_df = new_df[:10]
    return new_df


def cls_text(text):
    # Очистка текста
    text = text.replace('\n', '')
    text = text.replace('...', '. ')
    text = text.replace('(', '')
    text = text.replace(')', '')
    text = text.replace('«', '')
    text = text.replace('»', '')
    text = text.replace('\\', '')
    text = text.replace('"', '')
    # text +='.' if not text[-1] in ['.', '!', '?'] else text
    text += '.' if not text.endswith('.') else text
    # Исправление ситуации "точка внутри" -- "шифрованные депеши.Журнал «Нива» №37"
    match = re.search(r'\w{2}[.]{1}\w{2}', text, re.U | re.I)
    if match != None:
        start = match.regs[0][0] + 2
        stop = match.regs[0][1] - 2
        text = text[:start] + '. ' + text[stop:]
    return text


def open_json():
    """ Загрузка CSV в DataFrame
  Returns: DataFrame
  """
    df = pd.read_csv('./data.csv')
    return df


def te(s):
    """
    Для каждого слова формируется признак пунктуации
    L  L.  L!  L?  B  B. N N.
    Args:
        s: str -- слов

    Returns: tuple -- (слов, 'L', 0)
    """

    if s.isnumeric():
        return s, 'N', 9
    elif s[:-1].isnumeric() and s.endswith('.'):
        return s, 'N.', 10
    elif s == '-':
        return s, 'T', 8
    elif s.islower() and s[-1:] not in ['.', '!', '?', ',']:
        return s, 'L', 0
    elif s.islower() and s.endswith('.'):
        return s, 'L.', 1
    elif s.islower() and s.endswith('!'):
        return s, 'L!', 2
    elif s.islower() and s.endswith('?'):
        return s, 'L?', 3
    elif s.islower() and s.endswith(','):
        return s, 'L,', 4
    elif not s.islower() and s[-1:] not in ['.', '!', '?']:
        return s, 'B', 5
    elif not s.islower() and s.endswith('.'):
        return s, 'B.', 6
    elif not s.islower() and s.endswith('!'):
        return s, 'B!', 7
    else:
        return s, 'No', 11


def del_pun(word):
    """
  1. перевод слов в ниж. рег.
  2. удаление знаков пунктуации
  3. удаление пробелов

  Args:
    word: str

  Returns: str
  """
    return word.lower().replace('.', '').replace('!', '').replace('?', '').replace(',', '').strip()


def main(df_text):
    """
    1. DataFrame({'text':[0 '....'] [1 '...'] ..}) -> DataFrame({'words':[..] [..], 'labels':[..] [..], 'labels_id':[..] [..]})
    2. DataFrame({'words':[..] [..], 'labels':[..] [..], 'labels_id':[..] [..]} -> output.jsonl
    """
    # df = open_json()
    df2hf = pd.DataFrame(columns=['words', 'labels', 'labels_id'])
    for i in tqdm(range(len(df_text))):
        st = df_text.values[i][0]
        # print(st)
        st = cls_text(st)
        ls_word = st.split()
        # print(ls_word)
        ls = list(map(te, ls_word))
        # print(ls_word)
        # print(ls)
        ls_1 = [s[0] for s in ls]
        ls_2 = [s[1] for s in ls]
        ls_3 = [s[2] for s in ls]
        ls_1 = list(map(del_pun, ls_1))
        # df2hf.loc[len(df2hf)] = [ls_1, ls_2, ls_3]
        dc = {'words': ls_1, 'labels': ls_2, 'labels_id': ls_3}
        # print(dc)
        with open('output_test.jsonl', 'a') as fl:
            json.dump(dc, fl)
            fl.write('\n')

if __name__ == '__main__':
    df = pd2json()
    main(df)
