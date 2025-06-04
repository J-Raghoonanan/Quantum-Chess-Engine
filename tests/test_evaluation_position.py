import pytest
import chess
from src.classical_evaluation import evaluate_position

def test_starting_position_evaluation():
    board = chess.Board()
    score = evaluate_position(board)
    print(f"Starting position score: {score}")
    assert isinstance(score, int), "Score should be an integer"
    return

def test_material_advantage_white():
    board = chess.Board()
    board.remove_piece_at(chess.E7)  # Remove black pawn
    score = evaluate_position(board)
    print(f"White material advantage score: {score}")
    assert score > 0, "White should be ahead in material"
    return

def test_material_advantage_black():
    board = chess.Board()
    board.remove_piece_at(chess.D1)  # Remove white queen
    score = evaluate_position(board)
    print(f"Black material advantage score: {score}")
    assert score < 0, "Black should be ahead in material"
    return

def test_material_advantage_black_2():
    board = chess.Board()
    board.remove_piece_at(chess.F2)  # Remove white pawn
    score = evaluate_position(board)
    print(f"Black material advantage score: {score}")
    assert score < 0, "Black should be ahead in material"
    return

def test_checkmate_detection():
    # Fool's mate (white is checkmated)
    board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 0 3")
    assert board.is_checkmate(), "Board should be in checkmate"
    score = evaluate_position(board)
    print(f"Checkmate evaluation score: {score}")
    assert score == -99999, "Checkmate should return extreme negative value for losing side"
    return