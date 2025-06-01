import pygame
import chess
from engine import QuantumChessEngine

WIDTH, HEIGHT = 512, 512
SQ_SIZE = HEIGHT // 8
FPS = 30

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
        self.reset_game()
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
    
    def reset_game(self):
        self.board = chess.Board()
        self.selected_square = None
        self.game_over = False
        self.play_as_white = self.ask_player_color()
        # Quantum engine plays first if player chose black
        if not self.play_as_white:
            ai_move = self.engine.select_quantum_move(self.board)
            if ai_move:
                self.board.push(ai_move)
        return
    
    
    def ask_player_color(self):
        font = pygame.font.SysFont(None, 32)
        white_rect = pygame.Rect(WIDTH//4 - 60, HEIGHT//2 - 25, 120, 50)
        black_rect = pygame.Rect(3*WIDTH//4 - 60, HEIGHT//2 - 25, 120, 50)

        while True:
            self.screen.fill((30, 30, 30))
            txt = font.render("Choose your color:", True, pygame.Color("white"))
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//4))

            pygame.draw.rect(self.screen, pygame.Color("white"), white_rect)
            pygame.draw.rect(self.screen, pygame.Color("black"), black_rect)
            w_txt = font.render("White", True, pygame.Color("black"))
            b_txt = font.render("Black", True, pygame.Color("white"))
            self.screen.blit(w_txt, (white_rect.centerx - w_txt.get_width()//2, white_rect.centery - w_txt.get_height()//2))
            self.screen.blit(b_txt, (black_rect.centerx - b_txt.get_width()//2, black_rect.centery - b_txt.get_height()//2))

            pygame.display.flip()
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if white_rect.collidepoint(event.pos):
                        return True
                    elif black_rect.collidepoint(event.pos):
                        return False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if white_rect.collidepoint(event.pos):
                        return True
                    elif black_rect.collidepoint(event.pos):
                        return False
        return
    

    def prompt_promotion_choice(self):
        pygame.event.clear()  # 🔁 Flush pending events to avoid auto-dismissal
        font = pygame.font.SysFont(None, 28)
        options = [(chess.QUEEN, "Queen"), (chess.ROOK, "Rook"), (chess.BISHOP, "Bishop"), (chess.KNIGHT, "Knight")]
        buttons = []
        box = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 75, 300, 150)

        for i, (_, label) in enumerate(options):
            rect = pygame.Rect(box.left + 10 + i * 70, box.centery - 20, 60, 40)
            buttons.append((rect, label))

        while True:
            self.draw_board()
            self.draw_pieces()
            pygame.draw.rect(self.screen, pygame.Color("black"), box)
            pygame.draw.rect(self.screen, pygame.Color("white"), box, 2)

            txt = font.render("Choose promotion:", True, pygame.Color("white"))
            self.screen.blit(txt, (box.centerx - txt.get_width() // 2, box.top + 10))

            for i, (rect, label) in enumerate(buttons):
                pygame.draw.rect(self.screen, pygame.Color("gray"), rect)
                label_surface = font.render(label, True, pygame.Color("black"))
                self.screen.blit(label_surface, (rect.centerx - label_surface.get_width()//2, rect.centery - label_surface.get_height()//2))

            pygame.display.flip()
            self.clock.tick(FPS)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    for i, (rect, _) in enumerate(buttons):
                        if rect.collidepoint(e.pos):
                            return options[i][0]
            return

    def run(self):
        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False

                if self.game_over:
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_r:
                            self.reset_game()
                        elif e.key == pygame.K_q:
                            running = False
                    continue

                elif e.type == pygame.MOUSEBUTTONDOWN and not self.board.is_game_over():
                    x, y = pygame.mouse.get_pos()
                    col, row = x // SQ_SIZE, 7 - (y // SQ_SIZE)
                    square = chess.square(col, row)
                    if self.selected_square is None:
                        self.selected_square = square
                    else:
                        move = chess.Move(self.selected_square, square)

                        # Handle promotion
                        if (self.board.piece_at(self.selected_square) and
                            self.board.piece_at(self.selected_square).piece_type == chess.PAWN and
                            chess.square_rank(square) in [0, 7]):
                            promo_piece = self.prompt_promotion_choice()
                            move = chess.Move(self.selected_square, square, promotion=promo_piece)

                        if move in self.board.legal_moves:
                            self.board.push(move)
                            if not self.board.is_game_over():
                                ai_move = self.engine.select_quantum_move(self.board)
                                if ai_move:
                                    self.board.push(ai_move)
                        self.selected_square = None

            self.draw_board()
            self.draw_pieces()

            if self.board.is_checkmate():
                self.game_over = True
                winner = "White" if self.board.turn == chess.BLACK else "Black"
                self.show_endgame_message(f"Checkmate! {winner} wins.")
            elif self.board.is_stalemate():
                self.game_over = True
                self.show_endgame_message("Stalemate! Game drawn.")

            self.clock.tick(FPS)
            pygame.display.flip()

        pygame.quit()
        return
    
    def show_endgame_message(self, message):
        font = pygame.font.SysFont(None, 36)
        box_width, box_height = 400, 150
        box_rect = pygame.Rect(WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2, box_width, box_height)

        # Draw background rectangle
        pygame.draw.rect(self.screen, pygame.Color("black"), box_rect)
        pygame.draw.rect(self.screen, pygame.Color("white"), box_rect, 2)

        msg = font.render(message, True, pygame.Color("red"))
        play_again_txt = font.render("Press R to restart or Q to quit", True, pygame.Color("white"))
        self.screen.blit(msg, (box_rect.centerx - msg.get_width() // 2, box_rect.top + 30))
        self.screen.blit(play_again_txt, (box_rect.centerx - play_again_txt.get_width() // 2, box_rect.top + 80))
        return
