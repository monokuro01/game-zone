from flask import Flask, render_template, request, jsonify, redirect, url_for
import uuid
import copy

app = Flask(__name__)

# 定数定義
BOARD_SIZE = 10
RED = "R"
BLUE = "B"
EMPTY = None

games = {}

class ZoneGame:
    def __init__(self):
        self.board = [[EMPTY] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = RED
        self.history = []
        self.captured_red = 0
        self.captured_blue = 0
        self.captured_history = []  # 取った駒の数の履歴も追加

    def save_state(self):
        """現在の盤面を履歴に保存"""
        self.history.append(copy.deepcopy(self.board))
        self.captured_history.append((self.captured_red, self.captured_blue))  # 取った駒の数も保存

    def undo(self):
        """1手前の状態に戻す"""
        if self.history:
            self.board = self.history.pop()
            self.captured_red, self.captured_blue = self.captured_history.pop()  # 取った駒の数を1手戻す
            self.turn = BLUE if self.turn == RED else RED
            return True
        return False

    def pass_turn(self):
        """手番をパスする"""
        self.turn = BLUE if self.turn == RED else RED

    def can_place_piece(self, x, y):
        """駒を置けるか判定"""
        if self.board[x][y] is not None:
            print(f"Position ({x}, {y}) is already occupied.")
            return False

        opponent = BLUE if self.turn == RED else RED

        if (y > 0 and self.board[x][y-1] == opponent) and (y < BOARD_SIZE - 1 and self.board[x][y+1] == opponent):
            return False

        if (x > 0 and self.board[x-1][y] == opponent) and (x < BOARD_SIZE - 1 and self.board[x+1][y] == opponent):
            return False

        return True

    def check_and_remove_opponent_stones(self, x, y):
        opponent = BLUE if self.turn == RED else RED
        captured_count = 0
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE and self.board[nx][ny] == opponent:
                ux, uy = nx + dx, ny + dy
                if 0 <= ux < BOARD_SIZE and 0 <= uy < BOARD_SIZE and self.board[ux][uy] == self.turn:
                    self.board[nx][ny] = EMPTY
                    captured_count += 1
        if self.turn == RED:
            self.captured_red += captured_count
        else:
            self.captured_blue += captured_count

    def has_valid_move(self):
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if self.can_place_piece(x, y):
                    return True
        return False

    def game_end(self):
        red_count = sum(row.count(RED) for row in self.board)
        blue_count = sum(row.count(BLUE) for row in self.board)
        if red_count > blue_count:
            return f"Winner: Red\nRed: {red_count}, Blue: {blue_count}"
        elif blue_count > red_count:
            return f"Winner: Blue\nRed: {red_count}, Blue: {blue_count}"
        else:
            if self.captured_red > self.captured_blue:
                return f"Winner: Red (Captured More)\nCaptured - Red: {self.captured_red}, Blue: {self.captured_blue}"
            elif self.captured_blue > self.captured_red:
                return f"Winner: Blue (Captured More)\nCaptured - Red: {self.captured_red}, Blue: {self.captured_blue}"
            else:
                return f"Winner: Blue (Default Rule)\nCaptured - Red: {self.captured_red}, Blue: {self.captured_blue}"

    def next_move(self, x, y):
        if self.can_place_piece(x, y):
            self.save_state()
            self.board[x][y] = self.turn
            self.check_and_remove_opponent_stones(x, y)
            response = {"success": True, "board": self.board, "captured_red": self.captured_red, "captured_blue": self.captured_blue, "result": None}
            self.turn = "B" if self.turn == "R" else "R"
            if not self.has_valid_move():
                self.turn = BLUE if self.turn == RED else RED
                if not self.has_valid_move():
                    result = self.game_end()
                    response["result"] = result
                    return response
            return response
        return {"success": False, "board": self.board, "turn": self.turn, "captured_red": self.captured_red, "captured_blue": self.captured_blue}

@app.route("/")
def index():
    game_id = str(uuid.uuid4())
    return redirect(url_for('game', game_id=game_id))

@app.route("/game/<game_id>")
def game(game_id):
    if game_id not in games:
        games[game_id] = ZoneGame()
    return render_template("index.html", game_id=game_id)

@app.route("/move/<game_id>", methods=["POST"])
def make_move(game_id):
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404
    game = games[game_id]
    data = request.json
    x, y = data["x"], data["y"]
    response = game.next_move(x, y)
    return jsonify(response)

@app.route("/undo/<game_id>", methods=["POST"])
def undo(game_id):
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404
    success = games[game_id].undo()
    return jsonify({"board": games[game_id].board, "turn": games[game_id].turn, "success": success, "captured_red": games[game_id].captured_red, "captured_blue": games[game_id].captured_blue})

@app.route("/pass/<game_id>", methods=["POST"])
def pass_turn(game_id):
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404
    games[game_id].pass_turn()
    return jsonify({"turn": games[game_id].turn})

@app.route("/reset/<game_id>", methods=["POST"])
def reset_game(game_id):
    if game_id in games:
        games[game_id] = ZoneGame()
    game = games[game_id]
    print(f"Resetting game {game_id}, board: {game.board}")
    return jsonify({
        "board": games[game_id].board,
        "turn": games[game_id].turn,
        "captured_red": games[game_id].captured_red,
        "captured_blue": games[game_id].captured_blue
    })

if __name__ == "__main__":
    app.run(debug=False)

