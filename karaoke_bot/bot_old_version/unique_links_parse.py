import json
import csv


def load_links_by_user_id(file_name: str) -> dict:
    with open(file_name, 'r') as f:
        links_by_user_id = json.load(f)
    return links_by_user_id


def get_unique_links(file_name: str) -> set:
    unique_links = set()
    with open(file_name, 'r') as file:
        for row in csv.reader(file):
            link = row[1]
            unique_links.add(link)
    return unique_links
