from datetime import datetime
import chess
import chess.svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import os
import json
import discord
import datetime
import uuid
import firebase_admin
from firebase_admin import db



cred_obj = firebase_admin.credentials.Certificate('firebaseKey.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://goosebot-304321-default-rtdb.firebaseio.com/'
	})


async def challenge(ctx, challenger):
    ref = db.reference('/chess_games')

    id = uuid.uuid4()
    id = str(id)[:6]
    id = id.upper()

    challenger =  challenger.replace('@', '').replace('!', '').replace('<', '').replace('>', '')

    expires = datetime.datetime.now().strftime("%c")
    days = datetime.timedelta(days = 2)
    expires = expires + days

    fen = {
		"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "turn": "white",
		"white": ctx.author.id,
		"black": challenger,
        "expires": expires,
        "accepted": "false"
	}
    
    ref.child(id).set(fen)

    embed=discord.Embed(title=f"{ctx.author} challenges {challenger}", description=f"To accept the challenge, type !chess accept {id}", color=0xffc800)
    embed.add_field(name="Expires:", value=expires, inline=True)
    embed.add_field(name="Game ID:", value=id, inline=True)

    await ctx.send(embed = embed)
    return

    

async def accept(ctx, client, gameid):
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

    await ctx.send(f'<@!{black}> accepted the challenge!, <@!{white}> goes first as the white pieces.')
    await view(ctx, client, gameid)
    return

async def move(ctx, client, movefrom, moveto, gameid):
    ref = db.reference(f'/chess_games/{gameid}')
    fen = ref.child('fen').get()
    board = chess.Board(fen)
    
    turn = ref.child('turn').get()
    player = ref.child(turn).get()
    
    
    move = chess.Move.from_uci(movefrom + moveto)

    if turn == 'black':
        board.turn = False
    else:
        board.turn = True

    print(type(player))
    print(type(ctx.author.id))
    if int(player) != ctx.author.id:
        await ctx.send(f'**It is <@!{player}>\'s turn to move a {turn} piece...**')

    if move in board.legal_moves:
        board.push(move)
    else:
        await ctx.send('**INVALID MOVE**')

    if turn == 'black':
        ref.child('turn').set("white")
        nextplayer = ref.child("white").get()
    else:
        ref.child('turn').set("black")
        nextplayer = ref.child("black").get()

    save(board)
    ref.child('fen').set(board.board_fen())

    embed=discord.Embed(title=f"{await client.fetch_user(player)} vs {awaitclient.fetch_user(nextplayer)}", description=f'It is now <@!{nextplayer}>' + "'s turn, use !chess move {from} {to} {gameid}", color=0xffc800)
    embed.add_field(name="Player:", value=f'<@!{player}>', inline=True)
    embed.add_field(name="Color:", value=turn, inline=True)
    embed.add_field(name="Piece:", value=chess.piece_name(board.piece_type_at(chess.parse_square(moveto))), inline=True)
    embed.add_field(name="Moved:", value=f'From {movefrom} to {moveto}', inline=True)
    embed.add_field(name="Is Checked:", value="False", inline=True)
    embed.add_field(name="Game ID:", value={gameid}, inline=True)
    
    await ctx.send(embed = embed)
    await ctx.send(file = discord.File("chess.png"))
    return

def concede(ctx):
    print('placeholder')
async def list(ctx, client, player):
    ref = db.reference(f'/chess_games/')

    player =  player.replace('@', '').replace('!', '').replace('<', '').replace('>', '')

    embed=discord.Embed(title=f"Games that {await client.fetch_user(player)} are playing")
    for games in ref.get():
        white = ref.child(games).child("white").get()
        black = ref.child(games).child("black").get()
        if white == player or black == player:
            embed.add_field(name=games, value=f'{await client.fetch_user(white)}(white) VS {await client.fetch_user(black)}(black):', inline=True)

    await ctx.send(embed = embed)
    return   

def save(board):
    with open('chess.svg', 'w') as file:
        file.write(chess.svg.board(board, size=1500))  
        file.close()
    rlgboard = svg2rlg('chess.svg')
    renderPM.drawToFile(rlgboard, 'chess.png', fmt='PNG')
    return

async def view(ctx, client, gameid):
    ref = db.reference(f'/chess_games/{gameid}')
    fen = ref.child('fen').get()
    board = chess.Board(fen)
    save(board)

    turn = ref.child('turn').get()
    player = ref.child(turn).get()

    expires = ref.child('expires').get()

    if turn == 'black':
        ref.child('turn').set("white")
        nextplayer = ref.child("white").get()
    else:
        ref.child('turn').set("black")
        nextplayer = ref.child("black").get()

    embed=discord.Embed(title=f"{client.fetch_user(player)} vs {client.fetch_user(nextplayer)}", description=f'It is now <@!{player}>' + "'s turn, use !chess move {from} {to} {gameid}", color=0xffc800)
    embed.add_field(name="Player:", value=f'<@!{player}>', inline=True)
    embed.add_field(name="Color:", value=turn, inline=True)
    embed.add_field(name="Expires:", value=expires, inline=True)
    embed.add_field(name="Game ID:", value=gameid, inline=True)

    await ctx.send(embed = embed)
    await ctx.send(file = discord.File("chess.png"))
    return
