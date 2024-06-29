var socketio = io();

var game = new Chess()

function onDragStart (source, piece, position, orientation) {
    // do not pick up pieces if the game is over
    if (game.game_over()) return false
  
    // only pick up pieces for the side to move
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
      return false
    }
}

function onDrop (source, target) {
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen (for simplicity)
  })

  // illegal move
  if (move === null) return 'snapback'

  SendFen(game.fen());
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
  board.position(game.fen())
}

var config = {
    draggable: true,
    pieceTheme: "/static/pieces/wikipedia/{piece}.png",
    position: 'start',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd
}

var board = Chessboard('board', config)

const SetFen = (fen) => {
    game.load(fen);
    board.position(fen);
}

socketio.on("message", (data) => {
    if (data.tag=="announcement") {
        console.log(data.message);
        return;
    }
    SetFen(data.fen);
});

const SendFen = (fen) => {
    socketio.emit("move", {tag: "fen", fen: fen});
};