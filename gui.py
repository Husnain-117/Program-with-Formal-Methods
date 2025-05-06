import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from parser import parse_and_transform, SSAConverter, format_ssa_output, parser, EXAMPLE_PROGRAM, EXAMPLE_PROGRAM_2, check_program_equivalence
from smt_generator import SMTGenerator

class MiniLangGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniLang Analyzer")
        self.root.geometry("1100x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        # --- Program Analysis Tab ---
        self.tab_analysis = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analysis, text="Program Analysis")

        self.setup_analysis_tab()

        # --- Equivalence Tab ---
        self.tab_equiv = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_equiv, text="Equivalence Check")

        self.setup_equiv_tab()

    def setup_analysis_tab(self):
        frame = self.tab_analysis

        # Input program
        input_label = ttk.Label(frame, text="Input Program:")
        input_label.pack(anchor='w', padx=5, pady=(5,0))
        self.input_text = scrolledtext.ScrolledText(frame, height=10, font=("Consolas", 12))
        self.input_text.pack(fill='x', padx=5, pady=5)
        self.input_text.insert('1.0', EXAMPLE_PROGRAM.strip())

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Parse & Analyze", command=self.analyze_program).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Clear", command=lambda: self.input_text.delete('1.0', tk.END)).pack(side='left', padx=2)

        # Output tabs
        self.analysis_tabs = ttk.Notebook(frame)
        self.analysis_tabs.pack(fill='both', expand=True, padx=5, pady=5)

        self.tab_parse_tree = self._add_output_tab(self.analysis_tabs, "Parse Tree")
        self.tab_ast = self._add_output_tab(self.analysis_tabs, "AST")
        self.tab_ssa = self._add_output_tab(self.analysis_tabs, "SSA")
        self.tab_smt = self._add_output_tab(self.analysis_tabs, "SMT Verification")

    def setup_equiv_tab(self):
        frame = self.tab_equiv

        # Program 1
        label1 = ttk.Label(frame, text="Program 1:")
        label1.grid(row=0, column=0, sticky='w', padx=5, pady=(5,0))
        self.input_prog1 = scrolledtext.ScrolledText(frame, height=8, font=("Consolas", 12))
        self.input_prog1.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)
        self.input_prog1.insert('1.0', EXAMPLE_PROGRAM.strip())

        # Program 2
        label2 = ttk.Label(frame, text="Program 2:")
        label2.grid(row=0, column=1, sticky='w', padx=5, pady=(5,0))
        self.input_prog2 = scrolledtext.ScrolledText(frame, height=8, font=("Consolas", 12))
        self.input_prog2.grid(row=1, column=1, sticky='nsew', padx=5, pady=5)
        self.input_prog2.insert('1.0', EXAMPLE_PROGRAM_2.strip())

        # Button
        btn = ttk.Button(frame, text="Check Equivalence", command=self.check_equivalence)
        btn.grid(row=2, column=0, columnspan=2, pady=5)

        # Output
        self.equiv_output = scrolledtext.ScrolledText(frame, height=18, font=("Consolas", 12), state='disabled')
        self.equiv_output.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)

        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def _add_output_tab(self, notebook, title):
        frame = ttk.Frame(notebook)
        text = scrolledtext.ScrolledText(frame, font=("Consolas", 12), state='disabled')
        text.pack(fill='both', expand=True)
        notebook.add(frame, text=title)
        return text

    def analyze_program(self):
        code = self.input_text.get('1.0', tk.END).strip()
        if not code:
            messagebox.showwarning("Input Required", "Please enter a program.")
            return

        # Parse Tree
        try:
            tree = parser.parse(code)
            parse_tree_str = tree.pretty()
        except Exception as e:
            parse_tree_str = f"Parse Error:\n{e}"

        # AST
        try:
            ast = parse_and_transform(code)
            ast_str = str(ast)
        except Exception as e:
            ast_str = f"AST Error:\n{e}"

        # SSA
        try:
            ssa = SSAConverter().convert(ast)
            ssa_str = format_ssa_output(ssa)
        except Exception as e:
            ssa_str = f"SSA Error:\n{e}"

        # SMT
        try:
            smt = SMTGenerator(ssa)
            smt.to_smt()
            smt_str = smt.check_assertions()
        except Exception as e:
            smt_str = f"SMT Error:\n{e}"

        self._set_output(self.tab_parse_tree, parse_tree_str)
        self._set_output(self.tab_ast, ast_str)
        self._set_output(self.tab_ssa, ssa_str)
        self._set_output(self.tab_smt, smt_str)

    def check_equivalence(self):
        prog1 = self.input_prog1.get('1.0', tk.END).strip()
        prog2 = self.input_prog2.get('1.0', tk.END).strip()
        if not prog1 or not prog2:
            messagebox.showwarning("Input Required", "Please enter both programs.")
            return
        try:
            ast1 = parse_and_transform(prog1)
            ssa1 = SSAConverter().convert(ast1)
            ast2 = parse_and_transform(prog2)
            ssa2 = SSAConverter().convert(ast2)
            result = check_program_equivalence(ssa1, ssa2)
        except Exception as e:
            result = f"Equivalence Error:\n{e}"
        self._set_output(self.equiv_output, result)

    def _set_output(self, widget, text):
        widget.config(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert('1.0', text)
        widget.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniLangGUI(root)
    root.mainloop() 