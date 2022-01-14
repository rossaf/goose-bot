from datetime import datetime
import chess
import chess.svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os
import json
import datetime
import uuid
import firebase_admin
from firebase_admin import db



cred_obj = firebase_admin.credentials.Certificate('firebaseKey.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://goosebot-304321-default-rtdb.firebaseio.com/'
	})


def challenge(ctx, challenger):
    ref = db.reference('/chess_games')

    id = uuid.uuid4()
    id = str(id)[:6]
    id = id.upper()

    challenger =  challenger.replace('@', '').replace('!', '').replace('<', '').replace('>', '')

    expires = datetime.datetime.now().strftime("%c")

    fen = {
		"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "turn": "white",
		"white": ctx.author.id,
		"black": challenger,
        "expires": expires,
        "accepted": "false"
	}
    
    ref.child(id).set(fen)

    return [f'**{ctx.author} challenges <@!{challenger}> to chess**', f'This challenge will expire: {expires}',f'Type !chess accept {id}']

def accept(gameid):
    try:
        ref = db.reference(f'/chess_games/{gameid}')
    except:
        return ['Game not found.']

    if ref.child('accepted').get() == "false":
        ref.child('users').set("true")
    else:
        return ['Game not found.']

    black = ref.child('black').get()
    white = ref.child('white').get()

    
    view(gameid)
    return [f'<@!{black}> accepted the challenge!', f'<@!{white}> goes first as the white pieces.', 'Use !chess move {to} {from} {gameID} to move','~discord.File("chess.png")']

def move(ctx, movefrom, moveto, gameid):
    ref = db.reference(f'/chess_games/{gameid}')
    fen = ref.child('fen').get()
    board = chess.Board(fen)
    
    turn = ref.child('turn').get()
    player = ref.child(turn).get()
    
    
    move = chess.Move.from_uci(movefrom + moveto)

    print(type(player))
    print(type(ctx.author.id))
    if int(player) != ctx.author.id:
        return [f'**It is <@!{player}>\'s turn to move a {turn} piece...**']
    
    if turn == 'black':
        board.turn = False
    else:
        board.turn = True

    if move in board.legal_moves:
        board.push(move)
    else:
        return ['**INVALID MOVE**']

    
    if turn == 'black':
        ref.child('turn').set("white")
        nextplayer = ref.child("white")
    else:
        ref.child('turn').set("black")
        nextplayer = ref.child("black")

    save(board)
    ref.child('fen').set(board.board_fen())

    return [f'**It is <@!{player}>\' moved from {movefrom} to {moveto}**', f'**It is <@!{nextplayer}>\'s turn to move a {turn} piece...**', '~discord.File("chess.png")']

def concede(ctx):
    print('placeholder')

def save(board):
    with open('chess.svg', 'w') as file:
        file.write(chess.svg.board(board, size=1500))  
        file.close()
    rlgboard = svg2rlg('chess.svg')
    renderPM.drawToFile(rlgboard, 'chess.png', fmt='PNG')

def view(gameid):
    fen = db.reference(f'/chess_games/{gameid}/fen')
    board = chess.Board(fen.get())
    save(board)
    
