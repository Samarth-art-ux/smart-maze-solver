const rows = 20;
const cols = 20;
let grid = [];
let start = { r: 0, c: 0 };
let end = { r: rows - 1, c: cols - 1 };
let isMouseDown = false;
let isSolving = false;

const gridContainer = document.getElementById('grid-container');
const generateBtn = document.getElementById('generateBtn');
const clearWallsBtn = document.getElementById('clearWallsBtn');
const solveBtn = document.getElementById('solveBtn');
const resetBtn = document.getElementById('resetBtn');

// Initialize Grid
function initGrid() {
    gridContainer.style.gridTemplateColumns = `repeat(${cols}, 25px)`;
    gridContainer.innerHTML = '';
    grid = [];

    for (let r = 0; r < rows; r++) {
        let row = [];
        for (let c = 0; c < cols; c++) {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.dataset.r = r;
            cell.dataset.c = c;

            if (r === start.r && c === start.c) cell.classList.add('start');
            else if (r === end.r && c === end.c) cell.classList.add('end');

            cell.addEventListener('mousedown', () => {
                isMouseDown = true;
                toggleWall(r, c, cell);
            });
            cell.addEventListener('mouseenter', () => {
                if (isMouseDown) toggleWall(r, c, cell);
            });
            cell.addEventListener('mouseup', () => isMouseDown = false);

            gridContainer.appendChild(cell);
            row.push(0); // 0: Empty, 1: Wall
        }
        grid.push(row);
    }
}

document.addEventListener('mouseup', () => isMouseDown = false);

function toggleWall(r, c, cell) {
    if (isSolving) return;
    if ((r === start.r && c === start.c) || (r === end.r && c === end.c)) return;

    if (grid[r][c] === 0) {
        grid[r][c] = 1;
        cell.classList.add('wall');
    } else {
        grid[r][c] = 0;
        cell.classList.remove('wall');
    }
}

function clearVisualization() {
    const cells = document.querySelectorAll('.cell');
    cells.forEach(cell => {
        cell.classList.remove('visited', 'path');
    });
}

function clearWalls() {
    if (isSolving) return;
    clearVisualization();
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === 1) {
                grid[r][c] = 0;
                const cell = document.querySelector(`.cell[data-r='${r}'][data-c='${c}']`);
                cell.classList.remove('wall');
            }
        }
    }
}

async function generateRandomMaze() {
    if (isSolving) return;
    clearWalls();
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rows, cols })
        });
        const data = await response.json();

        // Update Grid
        grid = data.grid;
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const cell = document.querySelector(`.cell[data-r='${r}'][data-c='${c}']`);
                if (grid[r][c] === 1) {
                    cell.classList.add('wall');
                } else {
                    cell.classList.remove('wall');
                }
            }
        }
    } catch (error) {
        console.error('Error generating maze:', error);
        alert('Failed to generate maze.');
    } finally {
        generateBtn.disabled = false;
        generateBtn.textContent = 'Generate Random Maze';
    }
}

async function solveMaze() {
    if (isSolving) return;
    isSolving = true;
    clearVisualization();
    solveBtn.disabled = true;
    solveBtn.textContent = 'Solving...';

    try {
        const response = await fetch('/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ grid, start, end })
        });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        await animateSearch(data.visited_order);
        if (data.found) {
            await animatePath(data.path);
        } else {
            alert('No path found!');
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to solve maze.');
    } finally {
        isSolving = false;
        solveBtn.disabled = false;
        solveBtn.textContent = 'Start BFS Visualization';
    }
}

function animateSearch(visitedOrder) {
    return new Promise(resolve => {
        let i = 0;
        function step() {
            if (i >= visitedOrder.length) {
                resolve();
                return;
            }
            const [r, c] = visitedOrder[i];
            if (!((r === start.r && c === start.c) || (r === end.r && c === end.c))) {
                const cell = document.querySelector(`.cell[data-r='${r}'][data-c='${c}']`);
                cell.classList.add('visited');
            }
            i++;
            requestAnimationFrame(step); // Fast animation
        }
        step();
    });
}

function animatePath(path) {
    return new Promise(resolve => {
        let i = 0;
        function step() {
            if (i >= path.length) {
                resolve();
                return;
            }
            const [r, c] = path[i];
            if (!((r === start.r && c === start.c) || (r === end.r && c === end.c))) {
                const cell = document.querySelector(`.cell[data-r='${r}'][data-c='${c}']`);
                cell.classList.add('path');
            }
            i++;
            setTimeout(step, 50); // Slower animation for path
        }
        step();
    });
}

generateBtn.addEventListener('click', generateRandomMaze);
clearWallsBtn.addEventListener('click', clearWalls);
solveBtn.addEventListener('click', solveMaze);
resetBtn.addEventListener('click', () => {
    if (isSolving) return;
    clearWalls();
});

initGrid();
