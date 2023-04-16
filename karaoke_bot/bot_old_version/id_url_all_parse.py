import json
import csv
import os


def get_links_by_user_id(file_path):
    links_by_user_id = {}

    with open(file_path, 'r') as file:
        for row in csv.reader(file):
            user_id = int(row[0])
            link = row[1]

            if user_id not in links_by_user_id:
                links_by_user_id[user_id] = []

            links_by_user_id[user_id].append(link)

    return links_by_user_id


def save_links_by_user_id(links_by_user_id, output_file_name):
    with open(output_file_name, 'w') as f:
        json.dump(links_by_user_id, f, indent=2)


def display_dict_as_json(dictionary):
    json_dict = json.dumps(dictionary, indent=4)
    print(json_dict)


if __name__ == '__main__':

    folder_path = 'id_url_files'
    filename_output = 'id_url_all.csv'
    with open(filename_output, 'w', encoding='utf-8', newline='') as file_output:
        writer = csv.writer(file_output, delimiter=',')

        for filename in os.listdir(folder_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(folder_path, filename)

                with open(file_path, 'r', encoding='utf-8') as file_input:
                   reader = csv.reader(file_input, delimiter=',')
                   for row in reader:
                       writer.writerow(row)

    links_by_user_id = get_links_by_user_id(filename_output)
    save_links_by_user_id(links_by_user_id, 'links_by_user_id.txt')
