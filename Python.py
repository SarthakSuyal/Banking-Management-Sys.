import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox

# Database connection
def connect_to_db():
    print("Connecting to database...")
    return sqlite3.connect("banking_management.db")

# Create the customer table (if it doesn't exist)
def create_customer_table():
    print("Creating customer table if it doesn't exist...")
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                address TEXT,
                account_type TEXT,
                loan_status TEXT DEFAULT 'Not Paid'
            )
        ''')
        conn.commit()
        print("Table created successfully or already exists.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        conn.close()

# Add new customer (with duplicate check)
def add_customer(name, address, account_type, loan_status):
    print(f"Adding customer: {name}, {address}, {account_type}, {loan_status}")
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        # Check if the customer already exists
        cursor.execute("SELECT * FROM customers WHERE name = ? AND address = ? AND account_type = ? AND loan_status = ?", 
                       (name, address, account_type, loan_status))
        result = cursor.fetchone()

        if result:
            print("Customer already exists.")
            return "Customer already exists."
        else:
            cursor.execute("INSERT INTO customers (name, address, account_type, loan_status) VALUES (?, ?, ?, ?)", 
                           (name, address, account_type, loan_status))
            conn.commit()
            print("Customer added successfully.")
            return "Customer added successfully."
    except Exception as e:
        print(f"Error adding customer: {e}")
        return f"Error: {e}"
    finally:
        conn.close()

# Update a customer's information
def update_customer(id, name, address, account_type, loan_status):
    print(f"Updating customer ID {id} with new data.")
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''UPDATE customers 
                          SET name = ?, address = ?, account_type = ?, loan_status = ?
                          WHERE id = ?''', (name, address, account_type, loan_status, id))
        conn.commit()
        print("Customer updated successfully.")
    except Exception as e:
        print(f"Error updating customer: {e}")
    finally:
        conn.close()

# Delete a customer
def delete_customer(id):
    print(f"Deleting customer with ID: {id}")
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''DELETE FROM customers WHERE id = ?''', (id,))
        conn.commit()
        print("Customer deleted successfully.")
    except Exception as e:
        print(f"Error deleting customer: {e}")
    finally:
        conn.close()

# View all customers
def view_customers():
    print("Viewing all customers...")
    conn = connect_to_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        print("Customers retrieved successfully.")
        return customers
    except Exception as e:
        print(f"Error viewing customers: {e}")
        return []
    finally:
        conn.close()

class BankingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Banking Management System')
        self.setGeometry(100, 100, 600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.add_button = QPushButton('Add Customer')
        self.add_button.clicked.connect(self.add_customer)
        layout.addWidget(self.add_button)

        self.view_button = QPushButton('View Customers')
        self.view_button.clicked.connect(self.view_customers)
        layout.addWidget(self.view_button)

        self.update_button = QPushButton('Update Customer')
        self.update_button.clicked.connect(self.update_customer)
        layout.addWidget(self.update_button)

        self.delete_button = QPushButton('Delete Customer')
        self.delete_button.clicked.connect(self.delete_customer)
        layout.addWidget(self.delete_button)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.show()

    def add_customer(self):
        print("Triggered add_customer UI function.")
        name, ok = QInputDialog.getText(self, 'Add Customer', 'Enter customer name:')
        if not ok:
            return
        address, ok = QInputDialog.getText(self, 'Add Customer', 'Enter customer address:')
        if not ok:
            return
        account_type, ok = QInputDialog.getText(self, 'Add Customer', 'Enter account type (Savings/Current):')
        if not ok:
            return
        loan_status, ok = QInputDialog.getText(self, 'Add Customer', 'Loan status:')
        if not ok:
            return

        message = add_customer(name, address, account_type, loan_status)
        self.show_message(message)
        self.view_customers()

    def update_customer(self):
        print("Triggered update_customer UI function.")
        row = self.table.currentRow()
        if row < 0:
            self.show_message("Please select a customer to update.")
            return
        
        customer_id = self.table.item(row, 0).text()
        name, ok = QInputDialog.getText(self, 'Update Customer', 'Enter new name:')
        if not ok:
            return
        address, ok = QInputDialog.getText(self, 'Update Customer', 'Enter new address:')
        if not ok:
            return
        account_type, ok = QInputDialog.getText(self, 'Update Customer', 'Enter new account type:')
        if not ok:
            return
        loan_status, ok = QInputDialog.getText(self, 'Update Customer', 'Enter new loan status:')
        if not ok:
            return

        update_customer(customer_id, name, address, account_type, loan_status)
        self.view_customers()

    def delete_customer(self):
        print("Triggered delete_customer UI function.")
        row = self.table.currentRow()
        if row < 0:
            self.show_message("Please select a customer to delete.")
            return

        customer_id = self.table.item(row, 0).text()
        delete_customer(customer_id)
        self.view_customers()

    def view_customers(self):
        print("Triggered view_customers UI function.")
        customers = view_customers()
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Address", "Account Type", "Loan Status"])

        for customer in customers:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            for column, item in enumerate(customer):
                self.table.setItem(row_position, column, QTableWidgetItem(str(item)))

    def show_message(self, message):
        print(f"Showing message: {message}")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Info")
        msg.exec_()

if __name__ == '__main__':
    print("Starting the application...")
    create_customer_table()
    app = QApplication(sys.argv)
    window = BankingApp()
    sys.exit(app.exec_())
