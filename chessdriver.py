from datetime import datetime
import chess
import chess.svg
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import discord
import datetime
import uuid
import firebase_admin
from firebase_admin import db



cred_obj = firebase_admin.credentials.Certificate('firebaseKey.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://goosebot-304321-default-rtdb.firebaseio.com/'
	})


async def challenge(ctx, client, challenger):
    ref = db.reference('/chess_games')

    id = uuid.uuid4()
    id = str(id)[:6]
    id = id.upper()

    challenger =  challenger.replace('@', '').replace('!', '').replace('<', '').replace('>', '')

    expires = datetime.datetime.now()
    days = datetime.timedelta(days = 2)
    expires = expires + days

    fen = {
		"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
        "turn": "white",
		"white": ctx.author.id,
		"black": challenger,
        "expires": expires.strftime("%c"),
        "accepted": "false"
	}
    
    ref.child(id).set(fen)

    embed=discord.Embed(title=f"{ctx.author} challenges {await client.fetch_user(challenger)}", description=f"To accept the challenge, type !chess accept {id}", color=0xffc800)
    embed.add_field(name="Expires:", value=expires, inline=True)
    embed.add_field(name="Game ID:", value=id, inline=True)

    await ctx.send(embed = embed)
    return

    

async def accept(ctx, client, gameid):
    try:
        ref = db.reference(f'/chess_games/{gameid}')
    except:
        await ctx.send('**ERROR**: GameID not found.')
        return

    if ref.child('accepted').get() == 'false':
        ref.child('accepted').set("true")
    else:
        await ctx.send('**ERROR**: This Game ID is already active (!chess move {move_from} {move_to} {game_id}).')
        return

    black = ref.child('black').get()
    white = ref.child('white').get()

    await ctx.send(f'<@!{black}> accepted the challenge!, <@!{white}> goes first as the white pieces.')
    await view(ctx, client, gameid)
    return

async def move(ctx, client, movefrom, moveto, gameid):
    try:
        ref = db.reference(f'/chess_games/{gameid}')
    except:
        await ctx.send('**ERROR**: GameID not found. (!chess list {@player})')
        return

    if ref.child('accepted').get() == "false":
        await ctx.send('**ERROR**: The opponent has to first accept the challenge (!chess accept {game_id}).')
        return
        

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
        return
 
    if move in board.legal_moves:
        board.push(move)
    elif board.is_castling(move):
        pieceto = board.piece_type_at(chess.parse_square(moveto))
        piecefrom = board.piece_type_at(chess.parse_square(movefrom))
        board.set_piece_at(chess.parse_square(movefrom), chess.Piece(pieceto, board.turn), False)
        board.set_piece_at(chess.parse_square(moveto), chess.Piece(piecefrom, board.turn), False)
    else:
        if board.is_check():
            await ctx.send('**INVALID MOVE**: You must remove yourself from check...')
        else:
            await ctx.send('**INVALID MOVE**: The ' + chess.piece_name(board.piece_type_at(chess.parse_square(movefrom))) + ' cannot move that way.')
        return
    
    if turn == 'black':
        ref.child('turn').set("white")
        nextplayer = ref.child("white").get()
    else:
        ref.child('turn').set("black")
        nextplayer = ref.child("black").get()
        

    save(board)
    ref.child('fen').set(board.board_fen())

    embed=discord.Embed(title=f"{await client.fetch_user(player)} vs {await client.fetch_user(nextplayer)}", description=f'It is now <@!{nextplayer}>' + "'s turn, use !chess move {from} {to} {gameid}", color=0xffc800)
    embed.add_field(name="Player:", value=f'<@!{player}>', inline=True)
    embed.add_field(name="Color:", value=turn, inline=True)
    embed.add_field(name="Piece:", value=chess.piece_name(board.piece_type_at(chess.parse_square(moveto))), inline=True)
    embed.add_field(name="Moved:", value=f'From {movefrom} to {moveto}', inline=True)
    embed.add_field(name="Is Checked:", value=board.is_check(), inline=True)
    embed.add_field(name="Game ID:", value={gameid}, inline=True)
    
    await ctx.send(embed = embed)
    await ctx.send(file = discord.File("chess.png"))
    
    if board.is_stalemate() or board.is_insufficient_material() or board.is_checkmate():
        embed=discord.Embed(title="Game Over! ", description=f'<@!{player}> has defeated <!{nextplayer}> through checkmate!', color=0xffc800)
        await ctx.send(embed=embed)
    elif board.is_stalemate():
        embed=discord.Embed(title="Game Over! ", description=f'<@!{player}> vs <!{nextplayer}> is a stalemate!', color=0xffc800)
        await ctx.send(embed=embed)
    elif board.is_insufficient_material():
        embed=discord.Embed(title="Game Over! ", description=f'<@!{player}> vs <!{nextplayer}> is has insufficient material!', color=0xffc800)
        await ctx.send(embed=embed)
    return

async def concede(ctx, gameid):
    try:
        ref = db.reference(f'/chess_games/{gameid}')
    except:
        await ctx.send('**ERROR**: GameID not found. (!chess list {@player})')
        return

    if ref.child('accepted').get() == "false":
        await ctx.send('**ERROR**: The opponent has to first accept the challenge (!chess accept {game_id}).')
        return

    if int(ref.child('white').get()) != ctx.author.id and int(ref.child('black').get()) != ctx.author.id:
        await ctx.send(f'**It is <@!{player}>\'s turn to move a {turn} piece...**')
        return

    await ctx.send("Player Conceded")
    ref.set({})
    return

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
    try:
        ref = db.reference(f'/chess_games/{gameid}')
    except:
        await ctx.send('**ERROR**: GameID not found. (!chess list {@player})')
        return
    if ref.child('accepted').get() == "false":
        await ctx.send('**ERROR**: The opponent has to first accept the challenge (!chess accept {game_id}).')
        return
        
    fen = ref.child('fen').get()
    board = chess.Board(fen)
    save(board)

    turn = ref.child('turn').get()
    player = ref.child(turn).get()

    expires = ref.child('expires').get()

    if turn == 'black':
        nextplayer = ref.child("white").get()
    else:
        nextplayer = ref.child("black").get()

    embed=discord.Embed(title=f"{await client.fetch_user(player)} vs {await client.fetch_user(nextplayer)}", description=f'It is now <@!{player}>' + "'s turn, use !chess move {from} {to} {gameid}", color=0xffc800)
    embed.add_field(name="Player:", value=f'<@!{player}>', inline=True)
    embed.add_field(name="Color:", value=turn, inline=True)
    embed.add_field(name="Expires:", value=expires, inline=True)
    embed.add_field(name="Game ID:", value=gameid, inline=True)

    await ctx.send(embed = embed)
    await ctx.send(file = discord.File("chess.png"))
    return
