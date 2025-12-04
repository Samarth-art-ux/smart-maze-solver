from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Tuple, Dict
from collections import deque
import uvicorn
import random

app = FastAPI()

# Serve static files (Frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

class Point(BaseModel):
    r: int
    c: int

class MazeData(BaseModel):
    grid: List[List[int]]  # 0: Empty, 1: Wall
    start: Point
    end: Point

class GenerateMazeRequest(BaseModel):
    rows: int
    cols: int

@app.post("/generate")
async def generate_maze(req: GenerateMazeRequest):
    rows, cols = req.rows, req.cols
    grid = [[1 for _ in range(cols)] for _ in range(rows)]

    # Recursive Backtracker
    start_r, start_c = 0, 0
    grid[start_r][start_c] = 0
    stack = [(start_r, start_c)]

    while stack:
        r, c = stack[-1]
        candidates = []
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                candidates.append((nr, nc, dr, dc))

        if candidates:
            nr, nc, dr, dc = random.choice(candidates)
            wr, wc = r + dr // 2, c + dc // 2
            grid[wr][wc] = 0
            grid[nr][nc] = 0
            stack.append((nr, nc))
        else:
            stack.pop()

    # Ensure End is reachable
    grid[rows-1][cols-1] = 0
    if rows > 1: grid[rows-2][cols-1] = 0
    if cols > 1: grid[rows-1][cols-2] = 0

    return {"grid": grid}

@app.post("/solve")
async def solve_maze(data: MazeData):
    grid = data.grid
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    start = (data.start.r, data.start.c)
    end = (data.end.r, data.end.c)

    if grid[start[0]][start[1]] == 1 or grid[end[0]][end[1]] == 1:
        raise HTTPException(status_code=400, detail="Start or End position is a wall")

    queue = deque([start])
    visited = {start}
    predecessors: Dict[Tuple[int, int], Tuple[int, int]] = {}
    visited_order = []

    found = False
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        current = queue.popleft()
        visited_order.append(current)

        if current == end:
            found = True
            break

        r, c = current
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and (nr, nc) not in visited:
                visited.add((nr, nc))
                predecessors[(nr, nc)] = current
                queue.append((nr, nc))

    path = []
    if found:
        curr = end
        while curr != start:
            path.append(curr)
            curr = predecessors.get(curr)
            if curr is None:
                break
        path.append(start)
        path.reverse()

    return {
        "found": found,
        "visited_order": visited_order,
        "path": path
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)