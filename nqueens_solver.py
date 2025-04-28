import time
import copy
import heapq
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# BACKTRACKING SEARCH
def solve_n_queens_backtracking(n):
    results = []
    board = [["."] * n for _ in range(n)]

    def is_safe(row, col):
        for prev_row in range(row):
            if board[prev_row][col] == "Q":
                return False
        # Check top-left diagonal
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if board[i][j] == "Q":
                return False
            i -= 1
            j -= 1
        # Check top-right diagonal
        i, j = row - 1, col + 1
        while i >= 0 and j < n:
            if board[i][j] == "Q":
                return False
            i -= 1
            j += 1
        return True

    def backtrack(row):
        if row == n:
            copy = [r.copy() for r in board]
            results.append(copy)
            return
        for col in range(n):
            if is_safe(row, col):
                board[row][col] = "Q"
                backtrack(row + 1)
                board[row][col] = "."

    backtrack(0)
    return results

# HILL-CLIMBING SEARCH
def solve_n_queens_hill_climbing(n):
    def calculate_conflicts(board):
        conflicts = 0
        for r1 in range(n):
            for r2 in range(r1 + 1, n):
                c1 = board[r1].index("Q")
                c2 = board[r2].index("Q")
                if c1 == c2 or abs(c1 - c2) == abs(r1 - r2):
                    conflicts += 1
        return conflicts

    # Generate random board
    board = [["."] * n for _ in range(n)]
    for row in range(n):
        col = random.randint(0, n - 1)
        board[row][col] = "Q"

    current_conflicts = calculate_conflicts(board)

    while True:
        best_move = None
        best_conflicts = current_conflicts

        for row in range(n):
            current_col = board[row].index("Q")
            for col in range(n):
                if col != current_col:
                    new_board = copy.deepcopy(board)
                    new_board[row][current_col] = "."
                    new_board[row][col] = "Q"
                    conflicts = calculate_conflicts(new_board)
                    if conflicts < best_conflicts:
                        best_conflicts = conflicts
                        best_move = (row, col)

        if best_move:
            row, new_col = best_move
            old_col = board[row].index("Q")
            board[row][old_col] = "."
            board[row][new_col] = "Q"
            current_conflicts = best_conflicts
        else:
            break

    if current_conflicts == 0:
        return board
    else:
        return None

# BEST-FIRST SEARCH
def solve_n_queens_best_first(n, gui=None):
    def conflicts(board):
        queens = [(r, row.index("Q")) for r, row in enumerate(board) if "Q" in row]
        return sum(
            1 for i in range(len(queens)) for j in range(i+1, len(queens))
            if queens[i][1] == queens[j][1] or abs(queens[i][1] - queens[j][1]) == abs(queens[i][0] - queens[j][0])
        )

    board = [["."] * n for _ in range(n)]
    heap = [(0, board)]

    while heap:
        priority, current = heapq.heappop(heap)
        if gui:
            gui.log_message(f"Priority {priority}")
        row = next((i for i in range(n) if "Q" not in current[i]), -1)
        if row == -1:
            return current
        for col in range(n):
            new_board = copy.deepcopy(current)
            new_board[row][col] = "Q"
            heapq.heappush(heap, (conflicts(new_board), new_board))

    return None

# GENETIC ALGORITHM
def solve_n_queens_genetic(n, population_size=100, generations=500):
    def conflicts(board):
        queens = [(r, row.index("Q")) for r, row in enumerate(board)]
        conflict_count = 0
        for i in range(len(queens)):
            for j in range(i + 1, len(queens)):
                if queens[i][1] == queens[j][1] or abs(queens[i][1] - queens[j][1]) == abs(queens[i][0] - queens[j][0]):
                    conflict_count += 1
        return conflict_count


    def random_board():
        board = [["."] * n for _ in range(n)]
        for r in range(n):
            board[r][random.randint(0, n-1)] = "Q"
        return board

    def fitness(board):
        max_pairs = (n * (n-1)) // 2
        return max_pairs - conflicts(board)

    def crossover(p1, p2):
        child = [["."] * n for _ in range(n)]
        for r in range(n):
            col = p1[r].index("Q") if random.random() < 0.5 else p2[r].index("Q")
            child[r][col] = "Q"
        return child

    def mutate(board):
        r = random.randint(0, n-1)
        board[r] = ["."] * n
        board[r][random.randint(0, n-1)] = "Q"

    population = [random_board() for i in range(population_size)]

    for _ in range(generations):
        fitness_population = [(fitness(board), board) for board in population]
        fitness_population.sort(reverse=True)
        population = [board for fit, board in fitness_population]

        if conflicts(population[0]) == 0:
            return population[0]

        next_gen = population[:10]
        while len(next_gen) < population_size:
            p1 = random.choice(population[:50])
            p2 = random.choice(population[:50])
            child = crossover(p1, p2)
            if random.random() < 0.3:
                mutate(child)
            next_gen.append(child)

        population = next_gen

    return population[0]

# GUI Functions
class NQueensGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("N-Queens Solver")
        self.root.geometry("650x750")  
        self.center_window(650, 750)
        self.solutions = []
        self.current_solution = -1
        self.solving_in_progress = False

        self.create_widgets()
        self.setup_scrollable_canvas()
        self.update_status("Ready")

    def create_widgets(self):
        wrapper = ttk.Frame(self.root)
        wrapper.pack(pady=10, fill=tk.X)

        control_frame = ttk.Frame(wrapper)
        control_frame.pack(anchor="center")

        ttk.Label(control_frame, text="Board Size:").grid(row=0, column=0, padx=5)
        self.n_entry = ttk.Entry(control_frame, width=5)
        self.n_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(control_frame, text="Algorithm:").grid(row=0, column=2, padx=5)
        self.algo_combo = ttk.Combobox(control_frame, values=[
            "Backtracking Search", "Best-First Search", 
            "Hill-Climbing Search", "Genetic Algorithm"
        ])
        self.algo_combo.grid(row=0, column=3, padx=5)
        
        self.solve_btn = ttk.Button(control_frame, text="Solve", command=self.start_solving)
        self.solve_btn.grid(row=0, column=4, padx=5)
        
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

        self.status = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W, padding=(5, 5), font=("Segoe UI", 10))
        self.status.pack(side=tk.BOTTOM, fill=tk.X, ipady=7)

    def setup_scrollable_canvas(self):
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(container, bg="white", width=600, height=600)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
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
            import time
            start_time = time.time()

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

            end_time = time.time()
            self.solve_time = end_time - start_time  

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
            self.update_status(f"Found {len(solutions)} valid solutions in {self.solve_time:.3f} seconds")
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
        theme = {"light": "#2d2d4d", "dark": "#0d0d1a", "queen": "#00ff9d"} 

        self.canvas.update_idletasks()

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        cell_size = min(canvas_width, canvas_height - 40) // n

        # Correct centering calculation
        board_width = cell_size * n
        board_height = cell_size * n
        x_offset = (canvas_width - board_width) // 2
        y_offset = (canvas_height - board_height) // 2

        for row in range(n):
            for col in range(n):
                x1 = x_offset + col * cell_size
                y1 = y_offset + row * cell_size
                color = theme["light"] if (row + col) % 2 == 0 else theme["dark"]
                self.canvas.create_rectangle(x1, y1, x1+cell_size, y1+cell_size, fill=color, outline="")
                if board[row][col] == "Q":
                    cx = x1 + cell_size // 2
                    cy = y1 + cell_size // 2
                    self.canvas.create_text(cx, cy, text="♛", font=("Arial", cell_size//2), fill=theme["queen"])

        self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

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
        queens = []
        for row in range(n):
            for col in range(n):
                if board[row][col] == "Q":
                    queens.append((row, col))
        for i in range(len(queens)):
            for j in range(i+1, len(queens)):
                r1, c1 = queens[i]
                r2, c2 = queens[j]
                if c1 == c2 or abs(c1 - c2) == abs(r1 - r2):
                    return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = NQueensGUI(root)
    root.mainloop()