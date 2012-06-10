import sys, re, os
from PyQt4.QtGui import QApplication, QMainWindow
from PyQt4.QtCore import SIGNAL
from mainwindow import Ui_MainWindow
from subprocess import PIPE, Popen

letters = ['A','B','C','D','E','F','G','H','J']
sgf_letters = ['','a','b','c','d','e','f','g','h','i']
moves = []

def read_proc_stdout():
    l = proc.stdout.readline()
    r = l
    while l.strip():
        l = proc.stdout.readline()
        r += l
    return r

def make_gnugo_command(c):
    proc.stdin.write(c + '\n')
    return read_proc_stdout().replace('=','').strip()

def set_label(s):
    ui.label.setText(s)

def gen_w_move():
    white_mv = make_gnugo_command('genmove w')
    if white_mv.lower().find('pass') >= 0:
        moves.append(';W[]')
        set_label('pass')
    elif white_mv.lower().find('resign') >= 0:
        set_label('resign')
    else:
        w_x = letters.index(white_mv[0]) + 1
        w_y = white_mv[1]
        sgf_white_mv = ';W[' + sgf_letters[w_x] + sgf_letters[int(w_y)] + ']'
        moves.append(sgf_white_mv)
        set_label(str(w_x) + ',' + w_y)


def play_move():
    inc_move = ui.lineEdit.text()
    move_fmt = re.compile('^\d,\d$')

    if move_fmt.match(inc_move):
        raw_mv = inc_move.split(',')
        mv_x = int(raw_mv[0])
        mv_y = int(raw_mv[1])

        if mv_x == 0 or mv_y == 0:
            set_label('Non-zero move please :)')
        else:
            mv = letters[mv_x - 1] + str(mv_y)
            results = make_gnugo_command('play b ' + mv)
            if results:
                set_label(results)
            else:
                sgf_mv = ';B[' + sgf_letters[mv_x] + sgf_letters[mv_y] + ']'
                moves.append(sgf_mv)
                gen_w_move()
    elif str(inc_move).lower() == 'pass':
        moves.append(';B[]')
        gen_w_move()
    else:
        set_label('Enter \'pass\' or moves in the form #,#')

def save_sgf():
    raw_sgf = '''(;GM[1]FF[4]CA[UTF-8]AP[OstrichGo]ST[2]
RU[Japanese]SZ[9]KM[0.00]
PW[White]PB[Black]'''
    for move in moves:
        raw_sgf += move
    raw_sgf += ')'
    sgf_path = ui.lineEdit_2.text()
    sgf_handle = open(sgf_path,'w')
    sgf_handle.write(raw_sgf)
    sgf_handle.close()

# kick off child gnugo process
proc = Popen(['./gnugo-3.8', '--mode', 'gtp'], stdout=PIPE, stdin=PIPE)
make_gnugo_command('boardsize 9')

# init ui
app = QApplication(sys.argv)
MainWindow = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
ui.lineEdit_2.setText(os.environ['HOME'] + '/Documents/ostrich.sgf')

# hook up listeners
MainWindow.connect(ui.pushButton, SIGNAL('clicked()'), play_move)
MainWindow.connect(ui.pushButton_2, SIGNAL('clicked()'), save_sgf)

# show ui
MainWindow.show()
sys.exit(app.exec_())
