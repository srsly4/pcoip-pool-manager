

def process_pool_description_row(row):
    for i in range(len(row)):
        row[i] = row[i].replace('\n', ' ')
    row[2] = int(row[2])
    row[3] = True if row[3] == "true" else False
    return tuple(row)
