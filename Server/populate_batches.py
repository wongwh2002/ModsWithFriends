from mod_db import mods_database

if __name__ == "__main__":
    db = mods_database()
    batch_size = 1150
    total_modules = 6900
    total_batches = 6
    for batch_num in range(5, total_batches):
        start = batch_num * batch_size
        end = start + batch_size
        print(batch_num)
        db._populate_modules_db(start=start, end=end)
    db.close()
