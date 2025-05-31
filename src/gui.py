import pygame
import chess
from engine import QuantumChessEngine

WIDTH, HEIGHT = 512, 512
SQ_SIZE = HEIGHT // 8
FPS = 15

class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Quantum Chess Engine")
        self.clock = pygame.time.Clock()
        self.images = self.load_images()
        self.board = chess.Board()
        self.engine = QuantumChessEngine()
        self.selected_square = None
        return

    def load_images(self):
        pieces = ['wP','wR','wN','wB','wQ','wK','bP','bR','bN','bB','bQ','bK']
        return {p: pygame.transform.scale(pygame.image.load(f"../assets/{p}.png"), (SQ_SIZE, SQ_SIZE)) for p in pieces}

    def draw_board(self):
        colors = [pygame.Color("white"), pygame.Color("gray")]
        for r in range(8):
            for c in range(8):
                color = colors[(r + c) % 2]
                pygame.draw.rect(self.screen, color, pygame.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        return

    def draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)
                piece_code = ('w' if piece.color == chess.WHITE else 'b') + piece.symbol().upper()
                self.screen.blit(self.images[piece_code], pygame.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        return

    def run(self):
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.MOUSEBUTTONDOWN and not self.board.is_game_over():
                    x, y = pygame.mouse.get_pos()
                    col, row = x // SQ_SIZE, 7 - (y // SQ_SIZE)
                    square = chess.square(col, row)
                    if self.selected_square is None:
                        self.selected_square = square
                    else:
                        move = chess.Move(self.selected_square, square)
                        if move in self.board.legal_moves:
                            self.board.push(move)
                            if not self.board.is_game_over():
                                qm = self.engine.select_quantum_move(self.board)
                                if qm:
                                    self.board.push(qm)
                        self.selected_square = None

            self.draw_board()
            self.draw_pieces()
            self.clock.tick(FPS)
            pygame.display.flip()
        pygame.quit()
        return
