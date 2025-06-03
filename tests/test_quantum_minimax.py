import chess
from src.quantum_backend import select_best_quantum_move
import pytest

@pytest.mark.parametrize("depth", [1, 2, 3])
def test_quantum_minimax(depth):
    board = chess.Board()
    move = select_best_quantum_move(board, depth=depth)

    assert move is not None, f"No move returned at depth {depth}"
    assert move in board.legal_moves, f"Returned move {move} is not legal at depth {depth}"
    print(f"Depth {depth}: Selected move {board.san(move)}")