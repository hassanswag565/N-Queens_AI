import random
import heapq
import threading
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
# -------------------- ENHANCED GUI --------------------
class NQueensGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens Solver Pro")
        self.root.geometry("700x750")  
        self.center_window(700, 750)
        self.solutions = []
        self.current_solution = -1
        self.solving_in_progress = False
        
        self.themes = {
            "Classic": {"light": "#f0d9b5", "dark": "#b58863", "queen": "#aa0000"},
            "Cyber": {"light": "#2d2d4d", "dark": "#0d0d1a", "queen": "#00ff9d"},
            "Nature": {"light": "#e0f2e1", "dark": "#a3b899", "queen": "#228B22"},
            "Sunset": {"light": "#ffb3ba", "dark": "#ff6961", "queen": "#551a8b"}
        }
        
        self.create_widgets()
        self.setup_scrollable_canvas()
        self.center_board()
        self.update_status("Ready")

    def create_widgets(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X)

        ttk.Label(control_frame, text="Board Size:").grid(row=0, column=0, padx=5)
        self.n_entry = ttk.Entry(control_frame, width=5)
        self.n_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Algorithm:").grid(row=0, column=2, padx=5)
        self.algo_combo = ttk.Combobox(control_frame, values=[
            "Backtracking Search", "Best-First Search", 
            "Hill-Climbing Search", "Genetic Algorithm"
        ])
        self.algo_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(control_frame, text="Theme:").grid(row=0, column=4, padx=5)
        self.theme_combo = ttk.Combobox(control_frame, values=list(self.themes.keys()))
        self.theme_combo.current(0)
        self.theme_combo.grid(row=0, column=5, padx=5)
        
        self.solve_btn = ttk.Button(control_frame, text="Solve", command=self.start_solving)
        self.solve_btn.grid(row=0, column=6, padx=5)
        
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=5)
        
        self.prev_btn = ttk.Button(nav_frame, text="◀ Previous", 
                                 command=self.prev_solution, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="Next ▶", 
                                 command=self.next_solution, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.solution_counter = ttk.Label(nav_frame, text="Solution 0/0")
        self.solution_counter.pack(side=tk.LEFT, padx=10)

        self.status = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_scrollable_canvas(self):
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(container, bg="white")
        self.canvas.config(width=600, height=600)
        hscroll = ttk.Scrollbar(container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        vscroll = ttk.Scrollbar(container, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=hscroll.set, yscrollcommand=vscroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll.grid(row=1, column=0, sticky="ew")
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

    def update_status(self, message):
        self.status.config(text=message)
        self.root.update_idletasks()

    def start_solving(self):
        if not self.validate_inputs():
            return
            
        self.solving_in_progress = True
        self.root.after(5000, self.check_solving_progress)
        
        try:
            n = int(self.n_entry.get())
            self.solve_btn.config(state=tk.DISABLED)
            self.update_status("Solving...")
            threading.Thread(target=self.solve_thread, args=(n, self.algo_combo.get()), daemon=True).start()
        except ValueError:
            messagebox.showerror("Error", "Invalid board size")

    def validate_inputs(self):
        if not self.n_entry.get().strip():
            messagebox.showerror("Error", "Please enter board size!")
            return False
        if not self.algo_combo.get():
            messagebox.showerror("Error", "Please select an algorithm!")
            return False
        return True

    def check_solving_progress(self):
        if self.solving_in_progress:
            messagebox.showinfo("Please Wait", "Processing solutions... This might take a while for large boards.")

    def solve_thread(self, n, algorithm):
        try:
            solutions = []
            if algorithm == "Backtracking Search":
                solutions = solve_n_queens_backtracking(n)
            elif algorithm == "Best-First Search":
                result = solve_n_queens_best_first(n)
                solutions = [result] if result else []
            elif algorithm == "Hill-Climbing Search":
                result = solve_n_queens_hill_climbing(n)
                solutions = [result] if result and self.check_solution(result) else []
            elif algorithm == "Genetic Algorithm":
                result = solve_n_queens_genetic(n)
                solutions = [result] if result and self.check_solution(result) else []
            
            valid_solutions = [s for s in solutions if s is not None and self.check_solution(s)]
            self.root.after(0, self.show_solutions, valid_solutions)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: setattr(self, 'solving_in_progress', False))

    def show_solutions(self, solutions):
        self.solutions = solutions
        self.current_solution = 0 if solutions else -1
        
        if solutions:
            if len(solutions) > 15000:
                messagebox.showinfo("Notice", f"Found {len(solutions)} solutions. Displaying first solution.")
            self.draw_board(solutions[0])
            nav_state = tk.NORMAL if len(solutions) > 1 else tk.DISABLED
            self.prev_btn.config(state=nav_state)
            self.next_btn.config(state=nav_state)
            self.solution_counter.config(text=f"Solution 1/{len(solutions)}")
            self.update_status(f"Found {len(solutions)} valid solutions")
        else:
            self.canvas.delete("all")
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            self.solution_counter.config(text="Solution 0/0")
            messagebox.showinfo("No Solutions", "No valid solutions found.")
            self.update_status("No solutions found")
        
        self.solve_btn.config(state=tk.NORMAL)
    
    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = ((screen_height // 2)-40) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def draw_board(self, board):
        self.canvas.delete("all")
        n = len(board)
        theme = self.themes[self.theme_combo.get()]
        
        self.canvas.update_idletasks() 
 
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        cell_size = (min(canvas_width, canvas_height-40)) // n

        # Calculate center offsets
        x_offset = (canvas_width - (cell_size * n)) // 2
        y_offset = (canvas_height - (cell_size * n)) // 2


        
        # Ensure minimum padding
        x_offset = max(20, x_offset)
        y_offset = max(20, y_offset)

        for row in range(n):
            for col in range(n):
                x1 = x_offset + col * cell_size
                y1 = y_offset + row * cell_size
                color = theme["light"] if (row + col) % 2 == 0 else theme["dark"]
                self.canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size, 
                                           fill=color, outline="")
                if board[row] == col:
                    cx = x1 + cell_size // 2
                    cy = y1 + cell_size // 2
                    self.canvas.create_text(cx, cy, text="♛", 
                                          font=("Arial", cell_size//2), 
                                          fill=theme["queen"])
        
        # Update scroll region and center view
        self.canvas.configure(scrollregion=(
            x_offset - 20, y_offset - 20,
            x_offset + cell_size * n + 20,
            y_offset + cell_size * n + 20
        ))
        self.center_board()

    def center_board(self):
        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)
        self.canvas.update_idletasks()

    def prev_solution(self):
        if self.current_solution > 0:
            self.current_solution -= 1
            self.draw_board(self.solutions[self.current_solution])
            self.solution_counter.config(text=f"Solution {self.current_solution+1}/{len(self.solutions)}")

    def next_solution(self):
        if self.current_solution < len(self.solutions) - 1:
            self.current_solution += 1
            self.draw_board(self.solutions[self.current_solution])
            self.solution_counter.config(text=f"Solution {self.current_solution+1}/{len(self.solutions)}")

    @staticmethod
    def check_solution(board):
        n = len(board)
        for i in range(n):
            for j in range(i + 1, n):
                if board[i] == board[j] or abs(board[i] - board[j]) == abs(i - j):
                    return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = NQueensGUI(root)
    root.mainloop()