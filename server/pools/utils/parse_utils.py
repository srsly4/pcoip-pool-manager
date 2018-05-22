import datetime


def process_pool_description_row(row):
    for i in range(len(row)):
        row[i] = row[i].replace('\n', ' ')
    row[2] = int(row[2])
    row[3] = True if row[3] == "true" else False
    return tuple(row)


def process_reservation_row(row):
    for i in range(len(row)):
        row[i] = row[i].replace('\n', ' ')
    return {'pool_id': row[0],
            'start_date': datetime.datetime.strptime(row[1], "%Y-%m-%d").date(),
            'end_date': datetime.datetime.strptime(row[4], "%h-%m").time(),
            'start_time': datetime.datetime.strptime(row[3], "%h-%m").time(),
            'slot_count': int(row[5]),
            'period': int(row[6])}
