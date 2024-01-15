import fast8tube_gui
import sys

VERSION = '2024.01.15.1'

if __name__ == '__main__':

    if len(sys.argv) > 1 and (sys.argv[1] == '--version' or sys.argv[1] == '-v'):
        print(VERSION)
    else:
        fast8tube_gui.create_gui()
