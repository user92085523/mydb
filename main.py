import mydb
import random

mydb.init()


#データ作成用

# for i in range(100):
#    name = 'user'
#    password = ''
#    for i in range(3):
#        name += str(random.randint(0,9))
#    for i in range(16):
#        password += chr(random.randint(97, 122))
#    mydb.db_create('Users', 'name', name, 'password', password)


#データベース操作関数

# mydb.db_create('Users', 'name', 123, "password", "abcdef")
# data = mydb.db_read_by_tables_and_p_keys(['Users'], [[i for i in range(100)]])
# mydb.db_update('Users', '2', 'user_id', 123, 'password', 'dd', 'name', 'あああ')
# mydb.db_delete('Users', 3)


#データ表示

# data = mydb.db_read_by_tables_and_p_keys(['Users'], [[i for i in range(100)]])
# for i in range(1, len(data['Users'])):
#     print(data['Users'][i])