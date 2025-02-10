document.addEventListener("DOMContentLoaded", function () {
    const board = document.getElementById("board");
    const undoButton = document.getElementById("undo-btn");
    const passButton = document.getElementById("pass-btn");
    const resetButton = document.getElementById("reset-btn");

    undoButton.addEventListener("click", undoMove);
    passButton.addEventListener("click", passTurn);
    resetButton.addEventListener("click", resetGame);

    function createBoard(boardData = null) {
        board.innerHTML = "";
        for (let y = 0; y < 10; y++) {
            for (let x = 0; x < 10; x++) {
                const cell = document.createElement("div");
                cell.classList.add("cell");
                cell.dataset.x = x;
                cell.dataset.y = y;
                if (boardData && boardData[y][x] === "R") {
                    const redStone = document.createElement("div");
                    redStone.classList.add("stone", "red-stone");
                    cell.appendChild(redStone);
                } else if (boardData && boardData[y][x] === "B") {
                    const blueStone = document.createElement("div");
                    blueStone.classList.add("stone", "blue-stone");
                    cell.appendChild(blueStone);
                }
                cell.addEventListener("click", makeMove);
                board.appendChild(cell);
            }
        }
    }

    function makeMove(event) {
        const x = event.target.dataset.x;
        const y = event.target.dataset.y;
        fetch(`/move/${gameId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ x: x, y: y })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                createBoard(data.board);
            } else {
                alert("このマスには駒を置けません！");
            }
        });
    }

    function resetGame() {
        fetch(`/reset/${gameId}`, { method: "POST" })
        .then(response => response.json())
        .then(data => {
            console.log("Board data from server:", data);
            createBoard(data.board);
            document.getElementById("captured-red").textContent = data.captured_red;
            document.getElementById("captured-blue").textContent = data.captured_blue;
        });
        .catch(error => console.error('Error:', error));
    }

    resetGame();
});


