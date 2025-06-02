import chess


# Piece-square tables (simplified)
PSQT = {
    chess.PAWN:   [0, 5, 5, 0, 5, 10, 50, 0],
    chess.KNIGHT: [-50, -40, -30, -30, -30, -30, -40, -50],
    chess.BISHOP: [-20, -10, -10, -10, -10, -10, -10, -20],
    chess.ROOK:   [0, 0, 5, 10, 10, 5, 0, 0],
    chess.QUEEN:  [-20, -10, -10, 0, 0, -10, -10, -20],
    chess.KING:   [-30, -40, -40, -50, -50, -40, -40, -30],
}

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}

def evaluate_position(board: chess.Board) -> int:
    '''
    Evaluates a board position using Stockfish-inspired heuristics.
    '''

    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            rank = chess.square_rank(square) if piece.color == chess.WHITE else 7 - chess.square_rank(square)
            psqt_bonus = PSQT.get(piece.piece_type, [0]*8)[rank]
            modifier = 1 if piece.color == chess.WHITE else -1
            score += modifier * (value + psqt_bonus)

    # Add mobility bonus
    # Material score + mobility; more available moves = better position generally; 
    # weighted to not outweight score of a single pawn
    score += 5 * (len(list(board.legal_moves))) * (1 if board.turn else -1)
    return score