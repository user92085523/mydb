utf8.pyはencoderとdecoder関連の関数

ファイルが違う場合でも同じテーブル名は不可
テーブルaの1番目のカラム名は 'tablename_id' で固定、自動的に１からの連番が割り振られる

#データベース操作関数

# mydb.db_create('テーブル名', 'カラムの名前', 'value', "カラムの名前", 'value')
# mydb.db_update('テーブル名', 'n番目のレコード', 'カラムnの名前', 'value', 'カラムnの名前', 'value', ...)
# mydb.db_delete('テーブル名', 'n番目のレコード')


#データ表示

# data = mydb.db_read_by_tables_and_p_keys(['テーブル名a', 'テーブル名b'], [[テーブルaのn番目, ...x番目, ...y番目],[テーブルbのn番目, ...x番目, ...y番目, ...]])
