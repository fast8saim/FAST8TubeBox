import fast8tube_gui as f8gui
import fast8tube_db as f8db


if __name__ == '__main__':
    f8db.check_db()
    f8gui.create_gui()
