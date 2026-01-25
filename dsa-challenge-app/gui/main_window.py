import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font
from datetime import timedelta

class MainWindow:
    """Main application window with enhanced UI"""
    
    def __init__(self, root, service):
        self.root = root
        self.service = service
        self.participant_id = None
        self.current_problem_id = 1
        self.timer_running = False
        self.current_problem_data = None
        
        # Configure root window
        self.root.title("DSA Coding Challenge")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'primary': '#007acc',
            'success': '#4caf50',
            'error': '#f44336',
            'warning': '#ff9800',
            'secondary': '#2d2d2d',
            'accent': '#3a3a3a',
            'border': '#404040'
        }
        
        # Configure styles
        self.setup_styles()
        
        # Create main container
        self.container = tk.Frame(root, bg=self.colors['bg'])
        self.container.pack(fill='both', expand=True)
        
        # Show registration screen first
        self.show_registration()
    
    def setup_styles(self):
        """Setup custom styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('TFrame', background=self.colors['bg'])
        style.configure('TLabel', background=self.colors['bg'], foreground=self.colors['fg'])
        style.configure('TButton', background=self.colors['primary'], foreground=self.colors['fg'])
        style.map('TButton', background=[('active', '#005a9e')])
    
    def show_registration(self):
        """Show enhanced registration screen"""
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Registration frame
        reg_frame = tk.Frame(self.container, bg=self.colors['secondary'], padx=40, pady=40)
        reg_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_label = tk.Label(
            reg_frame, 
            text="🏆 DSA Coding Challenge", 
            font=('Arial', 28, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['primary']
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Subtitle
        subtitle = tk.Label(
            reg_frame,
            text="Test your coding skills • 10 Problems • 2 Hours",
            font=('Arial', 11),
            bg=self.colors['secondary'],
            fg='#888888'
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Name field
        tk.Label(reg_frame, text="Name:", font=('Arial', 12, 'bold'), bg=self.colors['secondary'], fg=self.colors['fg']).grid(row=2, column=0, sticky='e', padx=10, pady=15)
        self.name_entry = tk.Entry(reg_frame, width=30, font=('Arial', 12), bg=self.colors['accent'], fg=self.colors['fg'], insertbackground='white', relief='flat', bd=5)
        self.name_entry.grid(row=2, column=1, padx=10, pady=15)
        
        # Email field
        tk.Label(reg_frame, text="Email:", font=('Arial', 12, 'bold'), bg=self.colors['secondary'], fg=self.colors['fg']).grid(row=3, column=0, sticky='e', padx=10, pady=15)
        self.email_entry = tk.Entry(reg_frame, width=30, font=('Arial', 12), bg=self.colors['accent'], fg=self.colors['fg'], insertbackground='white', relief='flat', bd=5)
        self.email_entry.grid(row=3, column=1, padx=10, pady=15)
        
        # Info note
        note = tk.Label(
            reg_frame,
            text="Note: You can select language for each problem during the contest",
            font=('Arial', 9, 'italic'),
            bg=self.colors['secondary'],
            fg='#888888'
        )
        note.grid(row=4, column=0, columnspan=2, pady=(10, 20))
        
        # Start button
        start_btn = tk.Button(
            reg_frame,
            text="Start Contest →",
            command=self.register_and_start,
            font=('Arial', 14, 'bold'),
            bg=self.colors['success'],
            fg='white',
            padx=30,
            pady=15,
            relief='flat',
            cursor='hand2'
        )
        start_btn.grid(row=5, column=0, columnspan=2, pady=10)
    
    def register_and_start(self):
        """Register participant and start contest"""
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not name:
            messagebox.showerror("Error", "Please enter your name")
            return
        
        try:
            # Register participant with default language (will be selected per problem)
            self.participant_id = self.service.register_participant(name, email, "python")
            
            # Start contest
            success, message = self.service.start_contest(self.participant_id)
            if not success:
                messagebox.showerror("Error", message)
                return
            
            # Show contest interface
            self.show_contest_interface()
            self.start_timer()
            
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")
    
    def show_contest_interface(self):
        """Show enhanced contest interface"""
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Main container with dark theme
        self.container.config(bg=self.colors['bg'])
        
        # Top bar
        top_frame = tk.Frame(self.container, bg=self.colors['secondary'], height=60)
        top_frame.pack(fill='x', padx=0, pady=0)
        top_frame.pack_propagate(False)
        
        participant = self.service.get_participant(self.participant_id)
        
        # Left side - participant info
        info_frame = tk.Frame(top_frame, bg=self.colors['secondary'])
        info_frame.pack(side='left', padx=20, pady=10)
        
        tk.Label(info_frame, text=f"👤 {participant['name']}", font=('Arial', 11, 'bold'), 
                bg=self.colors['secondary'], fg=self.colors['fg']).pack(side='left', padx=10)
        
        # Right side - timer and score
        right_frame = tk.Frame(top_frame, bg=self.colors['secondary'])
        right_frame.pack(side='right', padx=20, pady=10)
        
        self.score_label = tk.Label(right_frame, text="Score: 0/100", font=('Arial', 13, 'bold'),
                                    bg=self.colors['secondary'], fg=self.colors['success'])
        self.score_label.pack(side='right', padx=15)
        
        self.timer_label = tk.Label(right_frame, text="⏱ 02:00:00", font=('Arial', 14, 'bold'),
                                    bg=self.colors['secondary'], fg=self.colors['warning'])
        self.timer_label.pack(side='right', padx=15)
        
        # Main content area
        content_frame = tk.Frame(self.container, bg=self.colors['bg'])
        content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel - Problem list
        left_panel = tk.Frame(content_frame, bg=self.colors['secondary'], width=250)
        left_panel.pack(side='left', fill='y', padx=(0, 10))
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="📝 Problems", font=('Arial', 13, 'bold'), 
                bg=self.colors['secondary'], fg=self.colors['fg']).pack(pady=15)
        
        # Scrollable problem list
        list_frame = tk.Frame(left_panel, bg=self.colors['secondary'])
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.problem_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 10),
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            selectbackground=self.colors['primary'],
            selectforeground='white',
            relief='flat',
            bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.problem_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.problem_listbox.yview)
        self.problem_listbox.bind('<<ListboxSelect>>', self.on_problem_select)
        
        # Load problems
        self.problems = self.service.get_all_problems()
        for prob in self.problems:
            self.problem_listbox.insert(tk.END, f"{prob['problem_id']}. {prob['title']}")
        
        # Right panel - Problem view and editor
        right_panel = tk.Frame(content_frame, bg=self.colors['bg'])
        right_panel.pack(side='left', fill='both', expand=True)
        
        # Problem description
        desc_frame = tk.LabelFrame(
            right_panel,
            text=" Problem Description ",
            font=('Arial', 11, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            relief='flat',
            bd=2
        )
        desc_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.problem_desc = scrolledtext.ScrolledText(
            desc_frame,
            wrap=tk.WORD,
            height=12,
            font=('Arial', 10),
            bg=self.colors['accent'],
            fg=self.colors['fg'],
            insertbackground='white',
            relief='flat',
            padx=10,
            pady=10
        )
        self.problem_desc.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Code editor with language selector
        editor_header = tk.Frame(right_panel, bg=self.colors['bg'])
        editor_header.pack(fill='x', pady=(0, 5))
        
        tk.Label(editor_header, text="💻 Code Editor", font=('Arial', 11, 'bold'),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(side='left')
        
        # Language selector
        lang_frame = tk.Frame(editor_header, bg=self.colors['bg'])
        lang_frame.pack(side='right')
        
        tk.Label(lang_frame, text="Language:", font=('Arial', 10),
                bg=self.colors['bg'], fg=self.colors['fg']).pack(side='left', padx=5)
        
        self.language_var = tk.StringVar(value="python")
        self.language_dropdown = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=["python", "java"],
            state="readonly",
            width=10,
            font=('Arial', 10)
        )
        self.language_dropdown.pack(side='left', padx=5)
        self.language_dropdown.bind('<<ComboboxSelected>>', self.on_language_change)
        
        editor_frame = tk.LabelFrame(
            right_panel,
            text="",
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            relief='flat',
            bd=2
        )
        editor_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.code_editor = scrolledtext.ScrolledText(
            editor_frame,
            wrap=tk.NONE,
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='#d4d4d4',
            insertbackground='white',
            relief='flat',
            padx=10,
            pady=10,
            selectbackground='#264f78'
        )
        self.code_editor.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Bottom panel - Buttons and results
        bottom_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        bottom_frame.pack(fill='x')
        
        # Button frame
        btn_frame = tk.Frame(bottom_frame, bg=self.colors['bg'])
        btn_frame.pack(side='left', pady=5)
        
        # Run button
        run_btn = tk.Button(
            btn_frame,
            text="▶ Run Code",
            command=self.run_code,
            font=('Arial', 11, 'bold'),
            bg=self.colors['primary'],
            fg='white',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        run_btn.pack(side='left', padx=5)
        
        # Submit button
        submit_btn = tk.Button(
            btn_frame,
            text="✓ Submit",
            command=self.submit_code,
            font=('Arial', 11, 'bold'),
            bg=self.colors['success'],
            fg='white',
            padx=20,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        submit_btn.pack(side='left', padx=5)
        
        # End contest button
        end_btn = tk.Button(
            btn_frame,
            text="End Contest",
            command=self.end_contest_confirm,
            font=('Arial', 10),
            bg=self.colors['error'],
            fg='white',
            padx=15,
            pady=10,
            relief='flat',
            cursor='hand2'
        )
        end_btn.pack(side='left', padx=5)
        
        # Result label
        self.result_label = tk.Label(
            bottom_frame,
            text="",
            font=('Arial', 11, 'bold'),
            bg=self.colors['bg']
        )
        self.result_label.pack(side='left', padx=20)
        
        # Load first problem
        self.load_problem(1)
    
    def on_problem_select(self, event):
        """Handle problem selection"""
        selection = self.problem_listbox.curselection()
        if selection:
            problem_id = selection[0] + 1
            self.load_problem(problem_id)
    
    def on_language_change(self, event=None):
        """Handle language change - reload current problem with new language"""
        if hasattr(self, 'current_problem_id'):
            self.load_problem(self.current_problem_id)
    
    def load_problem(self, problem_id):
        """Load problem details with selected language"""
        self.current_problem_id = problem_id
        current_lang = self.language_var.get()
        self.current_problem_data = self.service.get_problem(problem_id, current_lang)
        
        if self.current_problem_data:
            # Update description
            self.problem_desc.config(state='normal')
            self.problem_desc.delete('1.0', tk.END)
            
            desc_text = f"Problem {self.current_problem_data['problem_id']}: {self.current_problem_data['title']}\n"
            desc_text += f"{'='*80}\n"
            desc_text += f"Difficulty: {self.current_problem_data['difficulty']} | Marks: {self.current_problem_data['marks']}\n\n"
            desc_text += self.current_problem_data['description']
            
            self.problem_desc.insert('1.0', desc_text)
            self.problem_desc.config(state='disabled')
            
            # Update code editor with starter code
            self.code_editor.delete('1.0', tk.END)
            self.code_editor.insert('1.0', self.current_problem_data['starter_code'])
            
            # Clear result
            self.result_label.config(text="")
    
    def run_code(self):
        """Run code against sample test case"""
        code = self.code_editor.get('1.0', tk.END).strip()
        
        if not code:
            messagebox.showwarning("Warning", "Please write some code before running")
            return
        
        # Show processing
        self.result_label.config(text="Running...", fg=self.colors['primary'])
        self.root.update()
        
        # Get first test case as sample
        from backend.problem_loader import get_test_cases
        test_cases = get_test_cases(self.current_problem_id)
        
        if not test_cases:
            self.result_label.config(text="No test cases available", fg=self.colors['error'])
            return
        
        # Run against first test case using selected language
        from backend.executor import get_executor
        current_lang = self.language_var.get()
        
        try:
            executor = get_executor(current_lang)
            test_input = test_cases[0]['input']
            expected = test_cases[0]['expected_output']
            
            success, output, error, exec_time = executor.execute(code, test_input)
            
            if success:
                import json
                try:
                    actual = json.loads(output) if output else None
                except:
                    actual = output.strip()
                
                # Compare with expected
                from backend.judge import Judge
                judge = Judge()
                if judge._compare_output(actual, expected):
                    self.result_label.config(
                        text=f"✓ Sample Test Passed! ({exec_time:.3f}s) | Input: {test_input} | Output: {actual}",
                        fg=self.colors['success']
                    )
                else:
                    self.result_label.config(
                        text=f"✗ Sample Test Failed | Expected: {expected} | Got: {actual}",
                        fg=self.colors['error']
                    )
            else:
                self.result_label.config(text=f"✗ Error: {error[:150]}", fg=self.colors['error'])
        except Exception as e:
            self.result_label.config(text=f"✗ Error: {str(e)[:150]}", fg=self.colors['error'])
    
    def submit_code(self):
        """Submit code for judging"""
        code = self.code_editor.get('1.0', tk.END).strip()
        
        if not code:
            messagebox.showwarning("Warning", "Please write some code before submitting")
            return
        
        # Show processing
        self.result_label.config(text="Judging...", fg=self.colors['primary'])
        self.root.update()
        
        # Submit to service using selected language
        current_lang = self.language_var.get()
        result = self.service.submit_code(
            self.participant_id,
            self.current_problem_id,
            code,
            current_lang
        )
        
        # Show result
        if result['success']:
            verdict = result['verdict']
            score = result['score']
            
            if verdict == "Accepted":
                self.result_label.config(
                    text=f"✓ {verdict} (+{score} marks)",
                    fg=self.colors['success']
                )
            else:
                self.result_label.config(
                    text=f"✗ {verdict}",
                    fg=self.colors['error']
                )
            
            # Update score
            self.update_score()
        else:
            self.result_label.config(text=f"Error: {result['message']}", fg=self.colors['error'])
    
    def update_score(self):
        """Update score display"""
        results = self.service.get_results(self.participant_id)
        if results:
            self.score_label.config(text=f"Score: {results['total_score']}/100")
    
    def start_timer(self):
        """Start contest timer"""
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Update timer display"""
        if not self.timer_running:
            return
        
        status = self.service.get_contest_status(self.participant_id)
        if status and status['is_active']:
            remaining = status['remaining_time']
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            seconds = remaining % 60
            
            self.timer_label.config(text=f"⏱ {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            if remaining > 0:
                self.root.after(1000, self.update_timer)
            else:
                self.timer_running = False
                self.end_contest()
        else:
            self.timer_running = False
            self.end_contest()
    
    def end_contest_confirm(self):
        """Confirm and end contest"""
        if messagebox.askyesno("End Contest", "Are you sure you want to end the contest?"):
            self.end_contest()
    
    def end_contest(self):
        """End contest and show results"""
        self.timer_running = False
        self.service.end_contest(self.participant_id)
        self.show_results()
    
    def show_results(self):
        """Show enhanced results screen"""
        # Clear container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        results_frame = tk.Frame(self.container, bg=self.colors['secondary'], padx=50, pady=40)
        results_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(results_frame, text="🏁 Contest Ended", font=('Arial', 28, 'bold'),
                bg=self.colors['secondary'], fg=self.colors['fg']).pack(pady=20)
        
        results = self.service.get_results(self.participant_id)
        if results:
            # Score
            score_label = tk.Label(results_frame, text=f"{results['total_score']}/100",
                                  font=('Arial', 48, 'bold'), bg=self.colors['secondary'],
                                  fg=self.colors['success'])
            score_label.pack(pady=10)
            
            tk.Label(results_frame, text=f"Problems Solved: {results['problems_solved']}/10",
                    font=('Arial', 16), bg=self.colors['secondary'], fg=self.colors['fg']).pack(pady=5)
            
            # Performance level
            level = results['performance_level']
            level_colors = {'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
            level_color = level_colors.get(level, self.colors['fg'])
            
            level_frame = tk.Frame(results_frame, bg=level_color, padx=20, pady=10)
            level_frame.pack(pady=20)
            
            tk.Label(level_frame, text=f"🏆 {level} Level", font=('Arial', 20, 'bold'),
                    bg=level_color, fg='black').pack()
            
            # Close button
            tk.Button(results_frame, text="Close", command=self.root.quit,
                     font=('Arial', 12, 'bold'), bg=self.colors['primary'], fg='white',
                     padx=30, pady=10, relief='flat', cursor='hand2').pack(pady=20)
