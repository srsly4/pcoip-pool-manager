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
            'end_date': datetime.datetime.strptime(row[2], "%Y-%m-%d").date(),
            'start_time': datetime.datetime.strptime(row[3], "%H:%M:%S").time(),
            'end_time': datetime.datetime.strptime(row[4], "%H:%M:%S").time(),
            'slot_count': int(row[5]),
            'period': int(row[6])}


def make_JSON(reservation):
    js = {"pool_id": reservation.pool.pool_id,
          "slot_count": reservation.slot_count,
          "start_datetime": str(reservation.start_datetime),
          "end_datetime": str(reservation.end_datetime)}
    return js
