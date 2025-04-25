import random
import heapq
import tkinter as tk
from tkinter import ttk, messagebox

# BACKTRACKING SEARCH
def solve_n_queens_backtracking(n):
    solutions = []

    def is_safe(board, row, col):
        for i in range(row):
            if board[i] == col or abs(board[i] - col) == abs(i - row):
                return False
        return True

    def backtrack(board, row):
        if row == n:
            solutions.append(board[:])
            return
        for col in range(n):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(board, row + 1)

    backtrack([-1] * n, 0)
    return solutions

# BEST-FIRST SEARCH
def solve_n_queens_best_first(n):
    def heuristic(board):
        conflicts = 0
        for i in range(len(board)):
            for j in range(i + 1, len(board)):
                if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                    conflicts += 1
        return conflicts

    heap = []
    board = [-1] * n
    heapq.heappush(heap, (0, board))

    while heap:
        _, current = heapq.heappop(heap)
        row = current.count(-1)
        if row == 0:
            return current
        next_row = n - row
        for col in range(n):
            new_board = current[:]
            new_board[next_row] = col
            heapq.heappush(heap, (heuristic(new_board), new_board))

# HILL-CLIMBING SEARCH
def solve_n_queens_hill_climbing(n):
    def heuristic(board):
        conflicts = 0
        for i in range(n):
            for j in range(i + 1, n):
                if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                    conflicts += 1
        return conflicts

    board = [random.randint(0, n - 1) for _ in range(n)]
    current_score = heuristic(board)

    while True:
        neighbor = None
        neighbor_score = current_score

        for row in range(n):
            for col in range(n):
                if board[row] != col:
                    new_board = board[:]
                    new_board[row] = col
                    score = heuristic(new_board)
                    if score < neighbor_score:
                        neighbor = new_board
                        neighbor_score = score

        if neighbor_score >= current_score:
            return board if current_score == 0 else None

        board = neighbor
        current_score = neighbor_score

# GENETIC ALGORITHM
def solve_n_queens_genetic(n, population_size=100, generations=500):
    def fitness(board):
        non_attacking = 0
        for i in range(n):
            for j in range(i + 1, n):
                if board[i] != board[j] and abs(board[i] - board[j]) != abs(i - j):
                    non_attacking += 1
        return non_attacking

    def crossover(parent1, parent2):
        idx = random.randint(0, n-1)
        return parent1[:idx] + parent2[idx:]

    def mutate(board):
        idx = random.randint(0, n-1)
        board[idx] = random.randint(0, n-1)

    population = [[random.randint(0, n-1) for _ in range(n)] for _ in range(population_size)]

    for _ in range(generations):
        population = sorted(population, key=lambda x: -fitness(x))
        if fitness(population[0]) == n * (n-1) // 2:
            return population[0]

        next_gen = population[:10]
        while len(next_gen) < population_size:
            parent1 = random.choice(population[:50])
            parent2 = random.choice(population[:50])
            child = crossover(parent1, parent2)
            if random.random() < 0.3:
                mutate(child)
            next_gen.append(child)
        population = next_gen

    return population[0]

# GUI Functions
def draw_board(canvas, board):
    canvas.delete("all")
    n = len(board)
    size = min(500 // n, 80)
    offset = 10
    for i in range(n):
        for j in range(n):
            x1 = offset + j*size
            y1 = offset + i*size
            x2 = offset + (j+1)*size
            y2 = offset + (i+1)*size
            color = "#f0d9b5" if (i + j) % 2 == 0 else "#b58863"
            canvas.create_rectangle(x1, y1, x2, y2, fill=color)
            if board[i] == j:
                canvas.create_oval(x1+size//4, y1+size//4, x2-size//4, y2-size//4, fill="red")


def solve():
    try:
        n = int(entry_n.get())
        algorithm = algo_choice.get()

        if algorithm == "Backtracking Search":
            solutions = solve_n_queens_backtracking(n)
            if solutions:
                draw_board(canvas, solutions[0])
            else:
                messagebox.showinfo("Info", "No solution found.")
        elif algorithm == "Best-First Search":
            solution = solve_n_queens_best_first(n)
            if solution:
                draw_board(canvas, solution)
            else:
                messagebox.showinfo("Info", "No solution found.")
        elif algorithm == "Hill-Climbing Search":
            solution = solve_n_queens_hill_climbing(n)
            if solution:
                draw_board(canvas, solution)
            else:
                messagebox.showinfo("Info", "No solution found.")
        elif algorithm == "Genetic Algorithm":
            solution = solve_n_queens_genetic(n)
            if solution:
                draw_board(canvas, solution)
            else:
                messagebox.showinfo("Info", "No solution found.")
        else:
            messagebox.showerror("Error", "Please select a valid algorithm.")
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid board size.")

# Main GUI Window
root = tk.Tk()
root.title("N-Queens Solver")
root.geometry("600x650")

frame = tk.Frame(root)
frame.pack(pady=10)

label_n = tk.Label(frame, text="Board Size (n):", font=("Arial", 12))
label_n.grid(row=0, column=0, padx=5, pady=5)
entry_n = tk.Entry(frame, font=("Arial", 12))
entry_n.grid(row=0, column=1, padx=5, pady=5)

label_algo = tk.Label(frame, text="Select Algorithm:", font=("Arial", 12))
label_algo.grid(row=1, column=0, padx=5, pady=5)
algo_choice = ttk.Combobox(frame, values=["Backtracking Search", "Best-First Search", "Hill-Climbing Search", "Genetic Algorithm"], font=("Arial", 12))
algo_choice.grid(row=1, column=1, padx=5, pady=5)

solve_button = tk.Button(root, text="Solve N-Queens", command=solve, font=("Arial", 14), bg="#4CAF50", fg="white")
solve_button.pack(pady=10)

canvas = tk.Canvas(root, width=550, height=550, bg="white")
canvas.pack(pady=10)

root.mainloop()
