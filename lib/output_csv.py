import csv


def gen_one_csv(csv_filename: str, url_list: list):
    test_list = []
    for site_status_info in url_list:
        site_status_info = site_status_info.split('|')
        test_list.append(site_status_info)

    headers = ['url', 'status code', 'title']
    with open('{}.csv'.format(csv_filename), 'w', newline='', encoding='utf-8')as f:
        f_csv = csv.writer(f)
        f_csv.writerow(headers)
        f_csv.writerows(test_list)
