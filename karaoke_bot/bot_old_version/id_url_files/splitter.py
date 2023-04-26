with open('id_url_26_04_2023.csv', 'r', encoding='utf-8') as file:
    rows = file.readlines()

with open('rec_id_url_26_04_2023', 'w', encoding='utf-8') as file:
    for row in rows:
        if row.startswith('rec'):
            file.write(row.replace('rec: ', ''))
