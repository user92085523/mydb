import utf8
import json

db_struct = json.load(open('db.json', 'r'))
db = {}
header_size = 8


def db_create(t_name, *args, append=True):
    db_name = get_db_by_table_name(t_name)
    if not db_name:
        print(f'db:"{db_name}" does not exist')
        return
    columns = get_columns(db_name, t_name)
    if not columns:
        print(f'db:{db_name} | table:{t_name} | "columns" does not exist')
        return
    p_key_name = get_primary_key_col_name(db_name, t_name)
    if not p_key_name:
        print(f'db:{db_name} | table:{t_name} | "primary_key" does not exist')
        return
    sizes = get_columns_size(db_name, t_name)
    if not sizes:
        print(f'db:{db_name} | table:{t_name} | "sizes" does not exist')
        return
    col_total_size = get_col_total_size(db_name, t_name)
    if not col_total_size:
        print(f'db:{db_name} | table:{t_name} | "col_total_size" does not exist')
        return
    t_num = get_table_num(db_name, t_name)
    if not t_num:
        print(f'db:{db_name} | table:{t_name} | "table_num" does not exist')
        return
    records_num = db[db_name][t_name]['records_num']
    buff_args = assign_args_create(columns, args, p_key_name, records_num)

    #機能拡張用
    header = '|header|'

    binarys = get_filled_binary_create(buff_args, sizes, header)
    write_pos = 0
    if append:
        write_pos = get_write_pos(db[db_name][t_name]['start'], col_total_size + header_size, records_num)
    #header拡張用　使われなくなったレコードの再利用など
    else:
        pass
    f_seek(db_name, write_pos)
    f_write(db_name, binarys)
    update_records_num(db_name, t_name, t_num, records_num)


#p_keysは昇順リスト
def db_read_by_tables_and_p_keys(t_names, list_p_keys):
    if len(t_names) != len(list_p_keys):
        return
    records = {}
    buff = []
    for t_name in t_names:
        for p_keys in list_p_keys:
            buff = []
            prev_key = 0
            for p_key in p_keys:
                db_name = get_db_by_table_name(t_name)
                size = get_col_total_size(db_name, t_name) + header_size
                if prev_key == 0:
                    f_seek(db_name, db[db_name][t_name]['start'] + (p_key - 1) * size)
                elif prev_key + 1 < p_key:
                    f_seek(db_name, db[db_name]['pos'] + (p_key - 1 - prev_key) * size)
                binary = f_read(db_name, size)
                buff.append([p_key, binary])
                prev_key = p_key
            records[t_name] = buff
    return records


def db_update(t_name, p_key, *args):
    db_name = get_db_by_table_name(t_name)
    columns_name = get_columns(db_name, t_name)
    l_arg = assign_args_update(columns_name, args)
    columns_size = get_columns_size(db_name, t_name)
    l_binary = get_filled_binary_update(l_arg, columns_size)
    start = db[db_name][t_name]['start']
    record_size = get_col_total_size(db_name, t_name) + header_size
    write_pos = get_write_pos(start, record_size, int(p_key) - 1)
    #header更新
    f_seek(db_name, write_pos)
    f_write(db_name, b'|header|')

    for i in range(len(l_binary)):
        if l_binary[i] == None:
            f_seek(db_name, db[db_name]['pos'] + columns_size[i])
            continue
        f_write(db_name, l_binary[i])


def db_delete(t_name, p_key):
    db_name = get_db_by_table_name(t_name)
    start = db[db_name][t_name]['start']
    column_name = get_columns(db_name, t_name)
    column_total_size = get_col_total_size(db_name, t_name) + header_size
    columns_size = get_columns_size(db_name, t_name)
    header = utf8.encode('!DELETED')
    write_pos = get_write_pos(start, column_total_size, int(p_key) - 1)
    f_seek(db_name, write_pos)
    f_write(db_name, header)
    for i in range(len(column_name)):
        if '_id' in column_name[i]:
            f_seek(db_name, db[db_name]['pos'] + columns_size[i])
            continue
        f_write(db_name, utf8.fill(b'', columns_size[i]))


def get_filled_binary_update(l_arg, columns_size):
    for i in range(len(l_arg)):
        if l_arg[i] == None:
            continue
        l_arg[i] = utf8.fill(utf8.encode(l_arg[i]), columns_size[i])
    return l_arg


def assign_args_update(columns_name, args):
    buff = [None] * len(columns_name)
    for i in range(len(columns_name)):
        if '_id' in columns_name[i]:
            continue
        for j in range(len(args) - 1):
            if columns_name[i] == args[j]:
                buff[i] = str(args[j + 1])
    return buff


def init():
    load()


def load():
    for db_name in db_struct:
        load_db_fobj(db_name)
        load_db_index(db_name)


def load_db_fobj(db_name):
    db[db_name] = {}
    db[db_name]['f'] = open(db_name, 'rb+')
    db[db_name]['pos'] = 0


def load_db_index(db_name):
    cur_db = db_struct[db_name]
    buff = [[]] * len(cur_db)
    for t_name in cur_db:
        buff[cur_db[t_name]['table_num'] - 1] = [t_name, cur_db[t_name]['index_digit']]
    for i in range(len(buff)):
        t_name = buff[i][0]
        digit = buff[i][1]
        db[db_name][t_name] = {}
        for j in range(3):
            index = int_lstrip0(utf8.decode(f_read(db_name, digit)))
            if j == 0:
                db[db_name][t_name]['start'] = index
            if j == 1:
                db[db_name][t_name]['stop'] = index
            if j == 2:
                db[db_name][t_name]['records_num'] = index


def f_read(db_name, size):
    buff = db[db_name]['f'].read(size)
    db[db_name]['pos'] += size
    return buff


def f_write(db_name, binarys):
    size = len(binarys)
    db[db_name]['f'].write(binarys)
    db[db_name]['pos'] += size


def f_seek(db_name, num):
    db[db_name]['f'].seek(num)
    db[db_name]['pos'] = num


def int_lstrip0(string):
    buff = string.lstrip('0')
    if not buff:
        return 0
    return int(string.lstrip('0'))


def get_db_by_table_name(t_name):
    for db_name in db_struct:
        if t_name in db_struct[db_name].keys():
            return db_name
    return None


def get_columns(db_name, t_name):
    if 'columns' in db_struct[db_name][t_name].keys():
        return db_struct[db_name][t_name]['columns']
    return None


def get_primary_key_col_name(db_name, t_name):
    if 'primary_key' in db_struct[db_name][t_name].keys():
        return db_struct[db_name][t_name]['primary_key']
    return None


def get_columns_size(db_name, t_name):
    if 'sizes' in db_struct[db_name][t_name].keys():
        return db_struct[db_name][t_name]['sizes']
    return None


def get_col_total_size(db_name, t_name):
    if 'col_total_size' in db_struct[db_name][t_name].keys():
        return db_struct[db_name][t_name]['col_total_size']
    return None


def get_table_num(db_name, t_name):
    if 'table_num' in db_struct[db_name][t_name].keys():
        return db_struct[db_name][t_name]['table_num']
    return None


def get_filled_binary_create(args, sizes, header):
    buff = utf8.encode(header)
    for i in range(len(args)):
        buff += utf8.fill(utf8.encode(args[i]), sizes[i])
    return buff


def get_write_pos(start_pos, record_size, records_num):
    return start_pos + record_size * records_num


def get_records_num_write_pos(db_name, t_name, t_num):
    pos = 0
    for t_name in db_struct[db_name].keys():
        table = db_struct[db_name][t_name]
        digit = table['index_digit']
        if table['table_num'] < t_num:
            pos += digit * 3
        elif table['table_num'] == t_num:
            pos += digit * 2
    return pos


def assign_args_create(columns, args, p_key_name, records_num):
    buff = [''] * len(columns)
    for i in range(len(columns)):
        if columns[i] == p_key_name:
            buff[i] = str(records_num + 1)
            continue
        for j in range(len(args) - 1):
            if columns[i] == args[j]:
                buff[i] = str(args[j + 1])
    return buff


def update_records_num(db_name, t_name, t_num, records_num):
    pos = get_records_num_write_pos(db_name, t_name, t_num)
    digit = db_struct[db_name][t_name]['index_digit']
    f_seek(db_name, pos)
    f_write(db_name, utf8.lfill_0(utf8.encode(str(records_num + 1)), digit))
    db[db_name][t_name]['records_num'] += 1