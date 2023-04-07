import random
import json


def get_links_by_user_id(file_path):
    links_by_user_id = {}

    with open(file_path, 'r') as f:
        for line in f:
            user_id, link = line.strip().split(', ')
            user_id = int(user_id)

            if user_id not in links_by_user_id:
                links_by_user_id[user_id] = []

            links_by_user_id[user_id].append(link)

    return links_by_user_id


def save_links_by_user_id(links_by_user_id, output_file_name):
    with open(output_file_name, 'w') as f:
        json.dump(links_by_user_id, f, indent=2)


def load_links_by_user_id(input_file_name):
    with open(input_file_name, 'r') as f:
        links_by_user_id = json.load(f)
    return links_by_user_id


def display_dict_as_json(dictionary):
    json_dict = json.dumps(dictionary, indent=4)
    print(json_dict)


def get_unique_links(file_name):
    unique_links = set()
    with open(file_name, 'r') as f:
        for line in f:
            _, link = line.strip().split(', ')
            unique_links.add(link)
    return unique_links


def get_random_link(unique_links: set):
    return random.choice(list(unique_links))


if __name__ == "__main__":
    links_by_user_id = get_links_by_user_id('id_url_all.txt')
    display_dict_as_json(links_by_user_id)
    save_links_by_user_id(links_by_user_id, 'links_by_user_id.txt')