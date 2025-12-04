import requests
import json

def test_solve():
    url = "http://127.0.0.1:8000/solve"
    
    # Test Case 1: Solvable Maze (Empty Grid)
    grid_solvable = [[0 for _ in range(5)] for _ in range(5)]
    data_solvable = {
        "grid": grid_solvable,
        "start": {"r": 0, "c": 0},
        "end": {"r": 4, "c": 4}
    }
    
    try:
        response = requests.post(url, json=data_solvable)
        result = response.json()
        print("Test Case 1 (Solvable):", "PASSED" if result.get("found") else "FAILED")
        if not result.get("found"):
            print("Response:", result)
    except Exception as e:
        print("Test Case 1 Error:", e)

    # Test Case 2: Unsolvable Maze (Wall blocking path)
    grid_unsolvable = [[0 for _ in range(5)] for _ in range(5)]
    # Block the end
    grid_unsolvable[3][4] = 1
    grid_unsolvable[4][3] = 1
    
    data_unsolvable = {
        "grid": grid_unsolvable,
        "start": {"r": 0, "c": 0},
        "end": {"r": 4, "c": 4}
    }
    
    try:
        response = requests.post(url, json=data_unsolvable)
        result = response.json()
        print("Test Case 2 (Unsolvable):", "PASSED" if not result.get("found") else "FAILED")
        if result.get("found"):
            print("Response:", result)
    except Exception as e:
        print("Test Case 2 Error:", e)

def test_generate():
    url_gen = "http://127.0.0.1:8000/generate"
    url_solve = "http://127.0.0.1:8000/solve"
    
    data = {"rows": 20, "cols": 20}
    
    try:
        # Generate Maze
        resp_gen = requests.post(url_gen, json=data)
        grid = resp_gen.json().get("grid")
        
        if not grid:
            print("Test Case 3 (Generate): FAILED (No grid returned)")
            return

        # Verify dimensions
        if len(grid) != 20 or len(grid[0]) != 20:
             print(f"Test Case 3 (Generate): FAILED (Incorrect dimensions {len(grid)}x{len(grid[0])})")
             return

        # Solve Generated Maze
        data_solve = {
            "grid": grid,
            "start": {"r": 0, "c": 0},
            "end": {"r": 19, "c": 19}
        }
        
        resp_solve = requests.post(url_solve, json=data_solve)
        result = resp_solve.json()
        
        print("Test Case 3 (Generate & Solve):", "PASSED" if result.get("found") else "FAILED")
        if not result.get("found"):
             # Print a small part of grid to debug
             print("Grid start:", grid[0][:5])
             print("Grid end:", grid[19][15:])
             
    except Exception as e:
        print("Test Case 3 Error:", e)

if __name__ == "__main__":
    test_solve()
    test_generate()
