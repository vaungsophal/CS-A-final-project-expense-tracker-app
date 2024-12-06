import tkinter as tk
from tkcalendar import DateEntry
from tkinter import ttk, messagebox
from datetime import datetime
import customtkinter as ctk
from customtkinter import CTk, CTkLabel, CTkFrame, CTkEntry, CTkComboBox, CTkButton, CTkToplevel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import db

months = [
    "All", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]
years = ["All"] + [str(year) for year in range(2020, datetime.now().year + 1)]

class ExpenseTrackerClass(CTk):
    def __init__(self, current_user_id):
        super().__init__()
        self.title("Expense Tracker")
        self.geometry("600x450")
        self.current_user_id = current_user_id
        self.expenses = []
        self.categories = [
            "Food",
            "Transportation",
            "Education",
            "Entertainment",
            "Shopping",
            "Other",
        ]
        self.create_widgets()

    def create_widgets(self):
        # Left side menu buttons
        self.menu_frame = tk.Frame(self, bg= "black")
        self.menu_frame.pack(side='left', fill='y')

        buttons_data = [
            ("Add Expense", self.add_expense),
            ("Expense Records", self.data_records),
            ("Budget Control", self.manage_expense_setting),
            ("Expense Analysis", self.data_analysis),
            ("Expense Flow", self.daily_expenses)
        ]

        for text, command in buttons_data:
            button = CTkButton(self.menu_frame, text=text, height=35, command=command)
            button.pack(pady=10, padx=5)

        # Right side frame for changing content
        self.window_frame = tk.Frame(self, bg ="white")
        self.window_frame.pack(side="right", fill="both", expand=True)

    def add_expense(self):
        # Destroy existing window frame and recreate it
        self.clear_window_frame()
        
        # Add Expense Label
        self.add_expense_label = CTkLabel(self.window_frame, text="Add Expense", font=("Helvetica", 16, "bold"))
        self.add_expense_label.pack(pady=10, padx =10)  
        
        # Input fields
        self.expense_label = CTkLabel(self.window_frame, text="Amount ($):", font=("Helvetica", 14))
        self.expense_label.pack() # Align to the right
        self.expense_entry = CTkEntry(self.window_frame, font=("Helvetica", 14), width=200)
        self.expense_entry.pack()

        self.item_label = CTkLabel(self.window_frame, text="Description:", font=("Helvetica", 14))
        self.item_label.pack()  # Align to the right
        self.item_entry = CTkEntry(self.window_frame, font=("Helvetica", 14), width=200)
        self.item_entry.pack()

        self.category_label = CTkLabel(self.window_frame, text="Category:", font=("Helvetica", 14))
        self.category_label.pack()  # Align to the right
        self.category_dropdown = CTkComboBox(self.window_frame, values=self.categories, font=("Helvetica", 14), width=200)
        self.category_dropdown.pack()

        self.date_label = CTkLabel(self.window_frame, text="Date:", font=("Helvetica", 14))
        self.date_label.pack() 
        self.date_entry = DateEntry(self.window_frame, font=("Helvetica", 14), width=24, date_pattern='yyyy-mm-dd')
        self.date_entry.pack()

        self.button_add = CTkButton(self.window_frame, text="Add", command=self.add_to_list, width=80)
        self.button_add.pack(pady =10)  

    def add_to_list(self):
        # Gather input data
        amount = self.expense_entry.get()
        description = self.item_entry.get()
        category = self.category_dropdown.get()
        date = self.date_entry.get_date().strftime('%Y-%m-%d')  # Extract and format date
        
        # Validate input
        if not all([amount, description, category, date]):
            messagebox.showwarning("Warning", "Please fill in all fields.")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number for the amount.")
            return

        # Save the expense to the database
        conn, cursor = db.connect_to_database()
        cursor.execute("INSERT INTO expenses (user_id, amount, description, category, date) VALUES (?, ?, ?, ?, ?)",
                    (self.current_user_id, amount, description, category, date))
        conn.commit()

        # Check if the expense exceeds the target limit
        cursor.execute("SELECT target_amount FROM spending_targets WHERE user_id=?", (self.current_user_id,))
        target = cursor.fetchone()

        if target:
            target_amount = target[0]
            exceed_amount = amount - target_amount
            if exceed_amount > 0:
                messagebox.showinfo("Exceed Expense Target",
                                    f"Your expense is exceed ${exceed_amount:.2f} from target amount ${target_amount:2f}")

        # Append the expense to the list of expenses
        self.expenses.append((amount, description, category, date))

        # Clear the input fields
        self.expense_entry.delete(0, tk.END)
        self.item_entry.delete(0, tk.END)
        self.category_dropdown.set("")  # Clear the selection
        self.date_entry.set_date(datetime.now())  # Set date to current date

    def clear_window_frame(self):
        for widget in self.window_frame.winfo_children():
            widget.destroy()

    def data_records(self):
        self.clear_window_frame()

        # Data Records Label
        self.record_label = CTkLabel(self.window_frame, text = "Expense Record", font=("Helvetica", 16, "bold"))
        self.record_label.pack(side='top')

        select_monthyear_frame = CTkFrame(self.window_frame)
        select_monthyear_frame.pack()

        # Create a label for the month dropdown menu
        filter_option_label = CTkLabel(select_monthyear_frame, text="Filter Transactions by Date")
        filter_option_label.grid(row=0, column=0, columnspan=5, padx=5, pady=5)

        month_label = CTkLabel(select_monthyear_frame, text="Month:")
        month_label.grid(row=1, column=1, padx=5)

        # Create the month dropdown menu
        self.month_var = tk.StringVar(select_monthyear_frame)
        self.month_var.set("All")  # Default option
        months = ["All", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_dropdown = tk.OptionMenu(select_monthyear_frame, self.month_var, *months, command=self.filter_expenses)
        month_dropdown.grid(row=1, column=2, padx=5)

        # Create a label for the year dropdown menu
        year_label = CTkLabel(select_monthyear_frame, text="Year:")
        year_label.grid(row=1, column=3, padx=5)

        # Create the year dropdown menu
        self.year_var = tk.StringVar(select_monthyear_frame)
        self.year_var.set("All")  # Default option
        years = ["All"] + [str(year) for year in range(2020, datetime.now().year + 1)]
        year_dropdown = tk.OptionMenu(select_monthyear_frame, self.year_var, *years, command=self.filter_expenses)
        year_dropdown.grid(row=1, column=4, padx=5)

        self.tree = ttk.Treeview(self.window_frame, height=25)
        self.tree["columns"]=("Amount","Description","Category","Date")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Amount", width=100, anchor=tk.CENTER)
        self.tree.column("Description", width=400, anchor=tk.CENTER)
        self.tree.column("Category", width=200, anchor=tk.CENTER)
        self.tree.column("Date", width=200, anchor=tk.CENTER)
        
        self.tree.heading("#0", text="", anchor=tk.CENTER)
        self.tree.heading("Amount", text="Amount($)", anchor=tk.CENTER)
        self.tree.heading("Description", text="Description", anchor=tk.CENTER)
        self.tree.heading("Category", text="Category", anchor=tk.CENTER)
        self.tree.heading("Date", text="Date", anchor=tk.CENTER)

        conn, cursor = db.connect_to_database()
        cursor.execute("SELECT id, amount, description, category, date FROM expenses WHERE user_id=?", (self.current_user_id,))
        expenses = cursor.fetchall()
        # Color tags
        self.tree.tag_configure('evenrow', background='#f0f0ff')
        self.tree.tag_configure('oddrow', background='#ffffff')

        for i, expense in enumerate(expenses, start=1):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", text="", values=(expense[1], expense[2], expense[3], expense[4]), tags=(tag,))

        self.tree.pack(padx=20, pady=20)

        main_button = CTkFrame(self.window_frame)
        main_button.pack(padx=5, pady=5)
        # Function to update the expense in the database and treeview
        def edit_expense_command():
            # Get the selected item
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select an expense to edit.")
                return

            # Get the index of the selected item
            selected_index = int(self.tree.index(selected_item[0]))
            # Get the expense details from the selected item
            expense_id = expenses[selected_index][0]

            # Create a separate edit window
            edit_window = CTkToplevel()
            edit_window.title("Edit Expense")

            # Create labels and entry fields for editing
            amount_label =CTkLabel(edit_window, text="Amount:")
            amount_entry =CTkEntry(edit_window)
            amount_entry.insert(0, expenses[selected_index][1])
            amount_label.grid(row=0, column=0, padx=5, pady=5)
            amount_entry.grid(row=0, column=1, padx=5, pady=5)

            description_label =CTkLabel(edit_window, text="Description:")
            description_entry =CTkEntry(edit_window)
            description_entry.insert(0, expenses[selected_index][2])
            description_label.grid(row=1, column=0, padx=5, pady=5)
            description_entry.grid(row=1, column=1, padx=5, pady=5)

            category_label =CTkLabel(edit_window, text="Category:")
            category_entry =CTkEntry(edit_window)
            category_entry.insert(0, expenses[selected_index][3])
            category_label.grid(row=2, column=0, padx=5, pady=5)
            category_entry.grid(row=2, column=1, padx=5, pady=5)

            date_label =CTkLabel(edit_window, text="Date (yyyy-mm-dd):")
            date_entry =CTkEntry(edit_window)
            date_entry.insert(0, expenses[selected_index][4])
            date_label.grid(row=3, column=0, padx=5, pady=5)
            date_entry.grid(row=3, column=1, padx=5, pady=5)

            # Function to update the expense in the database and treeview
            def update_expense():
                new_amount = amount_entry.get()
                new_description = description_entry.get()
                new_category = category_entry.get()
                new_date = date_entry.get()

                if new_amount and new_description and new_category and new_date:
                    try:
                        datetime.strptime(new_date, '%Y-%m-%d')
                    except ValueError:
                        messagebox.showwarning("Warning", "Invalid date format. Please use yyyy-mm-dd.")
                        return

                    conn, cursor = db.connect_to_database()
                    cursor.execute("UPDATE expenses SET amount=?, description=?, category=?, date=? WHERE id=?",
                                (new_amount, new_description, new_category, new_date, expense_id))
                    conn.commit()  # Commit changes to the database

                    # Refresh the treeview with updated data
                    self.data_records()  # Refresh the expenses from the database

                    edit_window.destroy()
                else:
                    messagebox.showwarning("Warning", "Please fill in all fields.")

            update_button = CTkButton(edit_window, text="Update", command=update_expense)
            update_button.grid(row=4, columnspan=2, pady=10)

        edit_button = CTkButton(main_button, text="Edit", command=edit_expense_command)
        edit_button.grid(row=0, column=0, padx=5, pady=5)  

        # Function to delete the expense from the database and treeview
        def delete_expense_command():
            # Get the selected item
            selected_item = self.tree.selection()
            if not selected_item:
                messagebox.showwarning("Warning", "Please select an expense to delete.")
                return
            
            # Get the index of the selected item
            selected_index = int(self.tree.index(selected_item[0]))
            # Get the expense details from the selected item
            expense_id = expenses[selected_index][0]

            if messagebox.askyesno("Confirmation", "Are you sure you want to delete this expense?"):
                conn, cursor = db.connect_to_database()
                cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))  
                conn.commit()

                # Refresh the treeview with updated data
                self.data_records()  # Refresh the expenses from the database

        delete_button = CTkButton(main_button, text="Delete", command=delete_expense_command)
        delete_button.grid(row=0, column=1, padx=5, pady=5)  

        self.total_label = CTkLabel(main_button, text="Total Expenses:", font=("Helvetica", 14))
        self.total_label.grid(row=1, columnspan=2) 
        self.update_total_label()
        self.load_expenses()

    def filter_expenses(self, *args):
        # Get selected month and year
        selected_month = self.month_var.get()
        selected_year = self.year_var.get()
        # Clear existing Treeview items
        self.tree.delete(*self.tree.get_children())
        # Filter expenses based on selected month and year
        conn, cursor = db.connect_to_database()
        if selected_month == "All" and selected_year == "All":
            cursor.execute("SELECT id, amount, description, category, date FROM expenses WHERE user_id=?", (self.current_user_id,))
        elif selected_month == "All":
            cursor.execute("SELECT id, amount, description, category, date FROM expenses WHERE user_id=? AND strftime('%Y', date)=?", (self.current_user_id, selected_year))
        elif selected_year == "All":
            cursor.execute("SELECT id, amount, description, category, date FROM expenses WHERE user_id=? AND strftime('%m', date)=?", (self.current_user_id, str(months.index(selected_month)).zfill(2)))
        else:
            # Modify the SQL query to filter by both year and month
            cursor.execute("SELECT id, amount, description, category, date FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?", (self.current_user_id, f"{selected_year}-{str(months.index(selected_month)).zfill(2)}"))
        
        expenses = cursor.fetchall()

        # Insert filtered expenses into Treeview
        for i, expense in enumerate(expenses, start=1):
            self.tree.insert("", i, values=(expense[1], expense[2], expense[3], expense[4]))

    def manage_expense_setting(self):
        def confirm_or_update_target():
            target_amount = float(self.budgets_entry.get())
            if target_amount >= 0:
                conn, cursor = db.connect_to_database()
                cursor.execute("SELECT target_amount FROM spending_targets WHERE user_id=?", (self.current_user_id,))
                existing_target = cursor.fetchone()
                if existing_target:
                    cursor.execute("UPDATE spending_targets SET target_amount=? WHERE user_id=?",
                                (target_amount, self.current_user_id))
                    messagebox.showinfo("Success", "Expense budgets updated successfully.")
                else:
                    cursor.execute("INSERT INTO spending_targets (user_id, target_amount) VALUES (?, ?)",
                                (self.current_user_id, target_amount))
                    messagebox.showinfo("Success", "Expense budgets set successfully.")
                conn.commit()
                self.update_set_target()  # Call the method to update the target label
                self.manage_expense_setting() #load manange expense window
            else:
                messagebox.showwarning("Invalid Input", "Please enter a valid positive number for the budget.")

        def check_target_amount():
            conn, cursor = db.connect_to_database()
            cursor.execute("SELECT target_amount FROM spending_targets WHERE user_id=?", (self.current_user_id,))
            target = cursor.fetchone()

            if target:
                target_amount = target[0]
                messagebox.showinfo("Target Amount", f"Your daily expense target is ${target_amount:.2f}")
            else:
                messagebox.showinfo("No Target Set", "You have not set a daily expense target yet.")

        self.clear_window_frame()

        self.expense_target_label = CTkLabel(self.window_frame, text="Expense Limit Management",
                                            font=("Helvetica", 16, "bold"))
        self.expense_target_label.pack()

        limit_expense_frame = CTkFrame(self.window_frame)
        limit_expense_frame.pack()

        self.budgets_label = CTkLabel(limit_expense_frame, text="Define Expense Limit Amount ($) ",
                                    font=("Helvetica", 14))
        self.budgets_label.grid(row=0, column=1, columnspan=3, pady=5, padx=10)

        self.budgets_entry = CTkEntry(limit_expense_frame, font=("Helvetica", 14), width=120)
        self.budgets_entry.grid(row=1, column=1, columnspan=3, pady=5, padx=10)

        confirm_button = CTkButton(limit_expense_frame, text="Confirm/Update", width=100,
                                command=confirm_or_update_target)
        confirm_button.grid(row=2, column=1, columnspan=2, padx =10, pady=10)

        check_button = CTkButton(limit_expense_frame, text="Check Limit Amount", command=check_target_amount)
        check_button.grid(row=2, column=3, pady=10, padx=10)

        self.target_label = CTkLabel(limit_expense_frame, text="", font=("Helvetica", 14))
        self.target_label.grid(row=3, column=1, columnspan=3, pady=10)

        conn, cursor = db.connect_to_database()
        cursor.execute("SELECT target_amount FROM spending_targets WHERE user_id=?", (self.current_user_id,))
        target = cursor.fetchone()

        if not target:
            messagebox.showinfo("No Spending Target", "You have not set a spending target yet.")
        else:
            target_amount = target[0]

            # Fetch expenses exceeding the spending target
            cursor.execute(
                "SELECT date, SUM(amount) FROM expenses WHERE user_id=? GROUP BY date HAVING SUM(amount) > ?",
                (self.current_user_id, target_amount))
            exceeded_expenses = cursor.fetchall()

            exceed_list_frame = CTkFrame(self.window_frame)
            exceed_list_frame.pack(padx=5, pady=5)

            list_label = CTkLabel(exceed_list_frame, text="Exceed Expenses Record", font=("Helvetica", 14, "bold"))
            list_label.pack(side="top", fill="both", expand=True)

            tree = ttk.Treeview(exceed_list_frame)
            tree["columns"] = ("Amount", "Date", "Exceed Amount")  # Add "Exceed Amount" column
            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("Amount", width=200, anchor=tk.CENTER)
            tree.column("Date", width=300, anchor=tk.CENTER)
            tree.column("Exceed Amount", width=200, anchor=tk.CENTER)  # Define width for new column

            tree.heading("#0", text="", anchor=tk.CENTER)
            tree.heading("Amount", text="Total Amount($)", anchor=tk.CENTER)
            tree.heading("Date", text="Date", anchor=tk.CENTER)
            tree.heading("Exceed Amount", text="Exceed Amount($)", anchor=tk.CENTER)  # Set heading for new column

            for expense in exceeded_expenses:
                # Calculate exceed amount
                exceed_amount = expense[1] - target_amount
                tree.insert("", "end", text="", values=(expense[1], expense[0], exceed_amount))

            tree.pack()
        

    def update_total_label(self):
        total_expenses = sum(float(expense[0]) for expense in self.expenses)
        self.total_label.configure(text=f"Total Expenses: USD {total_expenses:.2f}")

    def load_expenses(self):
        conn, cursor = db.connect_to_database()
        cursor.execute("SELECT amount, description, category, date FROM expenses WHERE user_id=?", (self.current_user_id,))
        self.expenses = cursor.fetchall()

    def data_analysis(self):
        self.clear_window_frame()

        data_analysis_label = CTkLabel(self.window_frame, text = "Expense Analysis of Category", font=("Helvetica", 16, "bold"))
        data_analysis_label.pack()

        category_totals = {}

        # Calculate category totals
        for expense in self.expenses:
            category = expense[2]
            amount = float(expense[0])
            category_totals[category] = category_totals.get(category, 0) + amount

        # Plot the pie chart for category distribution
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%', startangle=140)
        ax.set_title('Expense Categories Distribution')

        # Add the pie chart to the combined window
        canvas = FigureCanvasTkAgg(fig, master=self.window_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.window_frame.mainloop()

    def daily_expenses(self):
        self.clear_window_frame()

        data_analysis_label = CTkLabel(self.window_frame, text="Daily Expense Flow", font=("Helvetica", 16, "bold"))
        data_analysis_label.pack()

        daily_totals = {}
        conn, cursor = db.connect_to_database()
        cursor.execute("SELECT date, SUM(amount) FROM expenses WHERE user_id=? GROUP BY date", (self.current_user_id,))
        expenses_data = cursor.fetchall()

        for date, total_amount in expenses_data:
            # Convert date to datetime object to ensure correct formatting
            formatted_date = datetime.strptime(date, '%Y-%m-%d')
            daily_totals[formatted_date] = total_amount

        sorted_dates = sorted(daily_totals.keys())

        # Plot the line chart for daily expenses
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(sorted_dates, [daily_totals[date] for date in sorted_dates], marker='o', linestyle='-')
        ax.set_title('Daily Expenses Trend')
        ax.set_xlabel('Date')
        ax.set_ylabel('Total Expenses ($)')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format the x-axis as dates
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

        # Add cursor hover functionality using mplcursors
        mplcursors.cursor(ax, hover=True)

        # Add the line chart to the combined window
        canvas = FigureCanvasTkAgg(fig, master=self.window_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.window_frame.mainloop()