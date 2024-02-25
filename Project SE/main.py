import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sqlite3
from sqlite3 import Error
import warnings

from datetime import date

# Suppress DeprecationWarnings globally
warnings.simplefilter("ignore", category=DeprecationWarning)

########################################################################
########################################################################
########################################################################

# Connect to SQLite database
conn = sqlite3.connect('projectse_db.db')
cur = conn.cursor()

########################################################################

################# Starting page with Login Screen  #####################


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("ui/loginscreen.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        
        
########################################################################       
        self.username_icon.setPixmap(QPixmap('icons/username.png'))
        self.password_icon.setPixmap(QPixmap('icons/password.png'))
        
########################################################################       

        self.loginbtn.clicked.connect(self.login)  
        self.userfield.returnPressed.connect(self.login)  ### "Enter" key event
        self.passwordfield.returnPressed.connect(self.login)  ### Para gumana yung Enter key as click to the loginbtn
        
########################################################################
    def login(self):
        user = self.userfield.text()
        password = self.passwordfield.text()
        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")
        else:
            try:
                query = 'SELECT password FROM employee WHERE username = ?'
                cur.execute(query, (user,))
                result_pass = cur.fetchone()
                if result_pass is not None and result_pass[0].strip() == password:
                    self.error.setText("Success!")
                    self.error.setStyleSheet("color: green")
                    self.loginbtn.setText("Proceed")
                    self.userfield.returnPressed.connect(lambda: self.redirect_based_on_role(user))
                    self.passwordfield.returnPressed.connect(lambda: self.redirect_based_on_role(user))
                    self.loginbtn.clicked.connect(lambda: self.redirect_based_on_role(user))
                else:
                    self.passwordfield.clear()
                    self.error.setText("Invalid username or password")

            except sqlite3.Error as err:
                print(f"Error: {err}")

    def redirect_based_on_role(self, user):  # redirect based on employee's role after login
        try:
            query = 'SELECT role FROM employee WHERE username = ?'
            cur.execute(query, (user,))
            result_role = cur.fetchone()
            if result_role is not None:
                role = result_role[0].strip()
                if role == 'Admin':  # if the user is an admin, go to user screen
                    self.gotohomescreen(user)
                elif role == 'Cashier':
                    self.gotocashierscreen(user)  # if the user is a cashier, go to cashier screen
                else:
                    self.error.setStyleSheet("color: red")
                    self.error.setText("Unknown role")
            else:
                self.error.setStyleSheet("color: red")
                self.error.setText("Role not found for user")

        except sqlite3.Error as err:
            print(f"Error: {err}")

    def gotohomescreen(self, user):
        widget.removeWidget(self)
        home = HomeScreen(user)
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def gotocashierscreen(self, user):
        widget.removeWidget(self)
        menu = CashierScreen(user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape: 
            event.ignore()
            
########################################################################
########################################################################

     
######################## ADMIN SCREENS ################################# 
class AdminCashierScreen(QDialog):
    def __init__(self, user):
        super(AdminCashierScreen, self).__init__()
        self.user = user
        loadUi("ui/admin_cashierscreen.ui",self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu2.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        #Redirect Functions
        self.logoutbtn.clicked.connect(self.gotologin)
        self.homebtn.clicked.connect(self.gotohome)
        self.settingsbtn.clicked.connect(self.gotosettings) 
        self.reportbtn.clicked.connect(self.gotosales) 
        self.p_managementbtn.clicked.connect(self.gotopmanagement)
    
        self.tableWidget.setColumnWidth(0, 300) # Table index 0, first column with 50 width pixel
        self.tableWidget.setColumnWidth(1, 100) # Table index 1, second column with 200 width pixel  
        
        self.tableWidget2.setColumnWidth(0, 50) # Table index 0, first column with 50 width pixel
        self.tableWidget2.setColumnWidth(1, 135) 
        self.tableWidget2.setColumnWidth(2, 100) 
        
    
        self.lugawbtn.clicked.connect(self.displayLugawProductList)
        self.mamibtn.clicked.connect(self.displayMamiProductList)
        self.maindishbtn.clicked.connect(self.displayMainDishProductList)
        self.dessertsbtn.clicked.connect(self.displayDessertsProductList)
        self.beveragesbtn.clicked.connect(self.displayBeveragesProductList)
        self.extrasbtn.clicked.connect(self.displayExtrasProductList)

        # Connect signals
        self.tableWidget.itemSelectionChanged.connect(self.addSelectedProductToInvoice)
        self.tableWidget2.itemChanged.connect(self.updateAmount)
        
    def addSelectedProductToInvoice(self):
        print("Adding selected product to invoice...")  # Add this line
        # Retrieve the selected row from TableWidget
        selected_indexes = self.tableWidget.selectedIndexes()
        if not selected_indexes:
            return
 

        # Extract product name from the selected row
        row = selected_indexes[0].row()
        product_name = str(self.tableWidget.item(row, 0).text())  # ProductName

        # Fetch product information based on product name
        query = "SELECT id, price FROM Product WHERE name = ?"
        cur.execute(query, (product_name,))
        product_info = cur.fetchone()

        if product_info:
            product_id = product_info[0]
            price = product_info[1]

            # Check if the product already exists in TableWidget2
            existing_row = self.findExistingProductRow(product_id)
            if existing_row is not None:
                # If the product exists, inform the user or take appropriate action
                QMessageBox.warning(self, "Duplicate Product", "This product is already in the invoice.")
            else:
                # If the product does not exist, add a new row
                row_position = self.tableWidget2.rowCount()
                self.tableWidget2.insertRow(row_position)
                self.tableWidget2.setItem(row_position, 0, QTableWidgetItem(str(1)))  # Default quantity to 1
                self.tableWidget2.setItem(row_position, 1, QTableWidgetItem(product_name))  # ProductName
                self.tableWidget2.setItem(row_position, 2, QTableWidgetItem(str(price)))  # Amount (ProductPrice)
                self.tableWidget2.setItem(row_position, 3, QTableWidgetItem(product_id))  # ProductID
            
                for row in range(self.tableWidget2.rowCount()):
                    for column in range(self.tableWidget2.columnCount()):
                        item = self.tableWidget2.item(row, column)
                        if item is not None:
                            item.setFont(QFont("Roboto", 10))  # Set font size
                            item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically
            
    def findExistingProductRow(self, product_id):
        # Search for the product ID in TableWidget2
        for row in range(self.tableWidget2.rowCount()):
            item = self.tableWidget2.item(row, 3)  # ProductID column
            if item is not None:
                print("Comparing:", item.text(), "with:", str(product_id))
                if item.text() == str(product_id):
                    print("Found duplicate at row:", row)
                    return row
        return None


    def updateAmount(self, item):
        # Calculate the amount based on the quantity entered
        if item.column() == 0:  # Quantity column
            row = item.row()
            quantity_item = self.tableWidget2.item(row, 0)
            amount_item = self.tableWidget2.item(row, 2)

            if quantity_item and amount_item:
                quantity = int(quantity_item.text())
                price = float(amount_item.text())
                amount = quantity * price
                amount_item.setText("{:.2f}".format(amount))  # Update the amount

    def displayLugawProductList(self):  #To load the data from database to the pyqt table
       
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/lugaw.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 1 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)
                
        
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
    
    def displayMamiProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/mami.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 2 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
    
    def displayMainDishProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/maindish.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 3 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)
      
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  

    def displayDessertsProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/desserts.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 4 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
                    
    def displayBeveragesProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/beverages.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 5 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)        

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
                    
    def displayExtrasProductList(self):  #To load the data from database to the pyqt table
       
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/extra.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 6 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)      
                  
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
                     
    def clearTableWidgetSelection(self):
        self.tableWidget.clearSelection()
    
    def gotologin(self):
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1) 


    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreen(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)
            
    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)     
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex()+1)   
    
    def gotosettings(self): #to settings screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def gotosales(self): #to user setting screen
        widget.removeWidget(self)

        sales= ReportScreen1(self.user)     
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()                  


class AddNewUserScreen(QDialog):
    def __init__(self, user):
        super(AddNewUserScreen, self).__init__()
        self.user = user
        loadUi("ui/add_new_userscreen.ui", self)
        self.insertbtn.clicked.connect(self.register)
        self.backbtn.clicked.connect(self.backfunction)

        # create a button group for the radio buttons
        self.roleButtonGroup = QButtonGroup()
        self.roleButtonGroup.addButton(self.adminbtn)
        self.roleButtonGroup.addButton(self.cashierbtn)

        # connect the button group's buttonClicked signal to a slot
        self.roleButtonGroup.buttonClicked.connect(self.handleRoleSelection)

    def handleRoleSelection(self, radioButton):
        # get the selected radio button's text
        selected_role = radioButton.text()
        # do something with the selected role, such as storing it in a variable
        print("Selected Role:", selected_role)

    def register(self):
        name = self.namefield.text()
        username = self.usernamefield.text()
        password = self.passwordfield.text()
        if len(name) == 0 or len(username) == 0 or len(password) == 0:
            self.error.setText("Please fill in all necessary fields, they cannot be null!")
        elif not self.adminbtn.isChecked() and not self.cashierbtn.isChecked():
            self.error.setText("Please select a role.")
        else:
            role = "Admin" if self.adminbtn.isChecked() else "Cashier" if self.cashierbtn.isChecked() else None
            user_info = [name, role, username, password]
            try:
                conn = sqlite3.connect('projectse_db.db')
                cur = conn.cursor()
                cur.execute("INSERT INTO Employee (name, role, username, password) "
                            "VALUES (?, ?, ?, ?)", user_info)
                conn.commit()
                self.error.setText("")
                QMessageBox.information(self, "Success", "Successfully Encoded!.")
                self.namefield.clear()
                self.usernamefield.clear()
                self.passwordfield.clear()
            except sqlite3.Error as e:
                self.error.setText("Check your input and try again, it may contain spaces.")
                print("Error:", e)
            finally:
                conn.close()
                

    def backfunction(self):
        widget.removeWidget(self)
        back = UserScreenEditMode(self.user)
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()


class AddNewProductScreen(QDialog):
    def __init__(self, user):
        super(AddNewProductScreen, self).__init__()
        self.user = user
        loadUi("ui/add_new_product.ui", self)
        self.newproductIMG.setPixmap(QPixmap('icons/newfood.png'))
        
        self.insertbtn.clicked.connect(self.addProduct)
        self.backbtn.clicked.connect(self.backfunction)

    def isInteger(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False
        
    def addProduct(self):
        try:
            productname = self.pnamefield.text()
            price = self.pricefield.text()

            if len(productname) == 0 or len(price) == 0:
                self.error.setText("Please fill in all necessary fields")
            elif not self.isInteger(price):
                self.error.setText("Price must be a decimal number.")
            elif self.categoryComboBox.currentIndex() == 0:
                self.error.setText("Please select a category for the product.")

            else:
                # Get the index of the selected category and add 1 to match the category IDs
                category = str(self.categoryComboBox.currentIndex() + 1)

                product_data = [productname, price, category]

                conn = sqlite3.connect('projectse_db.db')
                cur = conn.cursor()

                cur.execute("INSERT INTO Product (name, price, categoryID) "
                            "VALUES (?, ?, ?)", product_data)
                conn.commit()
                self.error.setText("")

                QMessageBox.information(self, "Success", "Successfully Encoded!.")

                self.pnamefield.clear()
                self.pricefield.clear()
                self.categoryComboBox.setCurrentIndex(0)
                self.backfunction()
                

        except sqlite3.Error as e:
            print("Error:", e)
        finally:
            if 'conn' in locals():
                conn.close()

    def backfunction(self):
        widget.removeWidget(self)
        back = PManagementScreen(self.user)
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            event.ignore()


class AdminProfScreen(QDialog):
    def __init__(self, user):
        super(AdminProfScreen, self).__init__()
        self.user = user
        loadUi("ui/adminprofilescreen.ui", self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    # Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings2.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        self.profileimg.setPixmap(QPixmap('icons/cresume.png'))  
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  # Pixmap for the second sidebar in settings screen.
        self.usersIcon.setPixmap(QPixmap('icons/users.png'))
        #######################################################
        # Redirect Functions
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.p_managementbtn.clicked.connect(self.gotopmanagement)
        self.settingsbtn.clicked.connect(self.gotosettings)
        self.usersbtn.clicked.connect(self.gotouserscreen)
        self.reportbtn.clicked.connect(self.gotosales)
        self.newpasswordbtn.clicked.connect(self.gotonewpassword)


        self.editimg.setPixmap(QPixmap('icons/editp.png')) 

        try:
            conn = sqlite3.connect('projectse_db.db')
            cur = conn.cursor()
            
            query = 'SELECT name, role, username, password FROM employee WHERE username = \'' + user + "\'"  #base sa nakalogin na user mafefetch lahat ng data information ni user.
            cur.execute(query)
            user_info = cur.fetchone()

            if user_info is not None:       #displaying all user info in the database.
                name, role, username, password = user_info
                self.boxlabel_name.setText(name)
                self.boxlabel_role.setText(role)
                self.boxlabel_username.setText(username)
                self.password.setText(password)
                self.password.setEchoMode(QtWidgets.QLineEdit.Password)
                self.viewpassword.setPixmap(QPixmap('icons/view.png')) 
            else:
                print("User not found")

        except sqlite3.Error as err:
            print(f"Error: {err}")

        finally:
            if conn:
                conn.close()
                
        self.editbtn.clicked.connect(self.toggle_echo_mode)
        
    def toggle_echo_mode(self):
        # Toggle the echo mode of the password field between Normal and Password
        if self.password.echoMode() == QLineEdit.Normal:
            self.password.setEchoMode(QLineEdit.Password)
            self.viewpassword.setPixmap(QPixmap('icons/view.png'))  
        else:
            self.password.setEchoMode(QLineEdit.Normal)
            self.viewpassword.setPixmap(QPixmap('icons/hide.png')) 
            

    def gotocashierscreen(self):  # To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotohome(self):  # To home profile screen
        widget.removeWidget(self)

        home = HomeScreen(self.user)
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotologin(self):
        widget.removeWidget(self)

        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def gotonewpassword(self): 
        widget.removeWidget(self)

        nwpass = AdminNewPasswordScreen(self.user)
        widget.addWidget(nwpass)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotouserscreen(self):  # To user screen
        widget.removeWidget(self)

        userlist = UserScreen(self.user)
        widget.addWidget(userlist)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotosettings(self):  # To user screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotosales(self):  # To user setting screen
        widget.removeWidget(self)

        sales = ReportScreen1(self.user)
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def keyPressEvent(self, event):  # To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()

class AdminNewPasswordScreen(QDialog):
    def __init__(self, user):
        super(AdminNewPasswordScreen, self).__init__()
        self.user = user
        loadUi("ui/newpasswordscreen.ui", self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    # Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings2.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        self.profileimg.setPixmap(QPixmap('icons/cresume.png'))  
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  # Pixmap for the second sidebar in settings screen.
        self.usersIcon.setPixmap(QPixmap('icons/users.png'))
        #######################################################
        # Redirect Functions
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.p_managementbtn.clicked.connect(self.gotopmanagement)
        self.settingsbtn.clicked.connect(self.gotosettings)
        self.usersbtn.clicked.connect(self.gotouserscreen)
        self.reportbtn.clicked.connect(self.gotosales)
        
        self.savebtn.clicked.connect(self.update_password)
        self.cancelbtn.clicked.connect(self.goback)

        
        self.new_passwordfield.setMaxLength(25)
        
 #------------------------------------------------------------------------------      
        
    def update_password(self):
            old_password = self.old_passwordfield.text()
            new_password = self.new_passwordfield.text()
            re_entered_password = self.re_passwordfield.text()

            # Add validation logic here
            if not old_password or not new_password or not re_entered_password:
                self.error.setText("Please fill in all fields.")
                return

            if new_password == old_password:
                self.error.setText("New password cannot be the same as the old password.")
                return
            
            if new_password != re_entered_password:
                self.error.setText("New password does not match.")
                return
            
            if len(new_password) > 25:
                self.error.setText("New password exceeds maximum length of 25 characters.")
                return

            
            if not self.check_password_strength(new_password):
                self.error.setText("New password must contain both uppercase and lowercase letters.")
                return 
            
            
            # Proceed with updating the password
            try:
                conn = sqlite3.connect('projectse_db.db')
                cur = conn.cursor()

                # Validate old password
                query = 'SELECT password FROM employee WHERE username = ?'
                cur.execute(query, (self.user,))
                stored_password = cur.fetchone()

                if not stored_password or stored_password[0] != old_password:
                    self.error.setText("Incorrect old password.")
                    return

                # Update the password
                update_query = 'UPDATE employee SET password = ? WHERE username = ?'
                cur.execute(update_query, (new_password, self.user))
                conn.commit()
                self.goback()
                
                
                QMessageBox.information(self, "Success", "Password updated successfully.")


            except sqlite3.Error as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {e}")

            finally:
                if conn:
                    conn.close()
        
    def check_password_strength(self, password):
        # Check if password contains both uppercase and lowercase letters
        has_upper = any(char.isupper() for char in password)
        has_lower = any(char.islower() for char in password)
        return has_upper and has_lower
        
#------------------------------------------------------------------------------------------------      
    
    def goback(self): 
        widget.removeWidget(self)

        back= AdminProfScreen(self.user)
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotocashierscreen(self):  # To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotohome(self):  # To home profile screen
        widget.removeWidget(self)

        home = HomeScreen(self.user)
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotologin(self):
        widget.removeWidget(self)

        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotouserscreen(self):  # To user screen
        widget.removeWidget(self)

        userlist = UserScreen(self.user)
        widget.addWidget(userlist)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotosettings(self):  # To user screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def gotosales(self):  # To user setting screen
        widget.removeWidget(self)

        sales = ReportScreen1(self.user)
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def keyPressEvent(self, event):  # To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()



class HomeScreen(QDialog):
    def __init__(self, user):
        super(HomeScreen, self).__init__()
        self.user = user
        loadUi("ui/homescreen.ui",self)
        
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home2.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        
        self.dashboardimg.setPixmap(QPixmap('icons/layout.png'))
        self.dashboardimg_2.setPixmap(QPixmap('icons/coca-leaves.png'))
        self.topimg.setPixmap(QPixmap('icons/badge.png'))
        self.pesoimg.setPixmap(QPixmap('icons/peso.png'))
        self.dailyimg.setPixmap(QPixmap('icons/24-hours.png'))
        
        
        #Redirect Functions
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.settingsbtn.clicked.connect(self.gotosettings) 
        self.reportbtn.clicked.connect(self.gotosales)
        self.p_managementbtn.clicked.connect(self.gotopmanagement) 

        # A Function to display the top 5 selling products based on sales
        self.displayTopSellingProduct()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start(1000)  # Update every 1 second

        # Initial update of the time label function
        self.update_time_label()
        
        current_date = date.today()
        
        try:
            query = f"SELECT printf('%.2f', SUM(Sales.totalPrice)) AS total_sales FROM Sales WHERE DATE(Sales.date) = '{current_date}'"
            cur.execute(query)
            totalsale = cur.fetchone()

            if totalsale is not None:
                totaldailysale = totalsale[0]  # Extract the total sale value from the tuple
                self.boxlabel_total.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                self.boxlabel_total.setText("00.00")  # Set label text to indicate no data available

        except Error as err:
            print(f"Error executing query: {err}")

        try:
            query = f"SELECT COUNT(*) AS totalSales FROM Sales  WHERE DATE(date) = '{current_date}'"
            cur.execute(query)
            totalsalecount = cur.fetchone()

            if totalsalecount is not None:
                totaldailysale = totalsalecount[0]  # Extract the total sale value from the tuple
                self.boxlabel_sale.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                self.boxlabel_sale.setText("0")  # Set label text to indicate no data available

        except Error as err:
            print(f"Error executing query: {err}")
    
    

    def displayTopSellingProduct(self):  #To load the data from database to the pyqt table
        query = "SELECT productName, totalQuantitySold \
                FROM ( SELECT P.name AS productName, SUM(T.quantity) AS totalQuantitySold \
                FROM \"Transaction\" T \
                JOIN Product P ON T.productID = P.id \
                GROUP BY T.productID \
                ORDER BY totalQuantitySold \
                DESC LIMIT 5 ) AS topSoldProducts"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)
        
        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 11))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically
        
    def update_time_label(self):
        current_datetime = QDateTime.currentDateTime()
        current_time_string = current_datetime.toString("MM-dd-yyyy HH:mm:ss")
        self.time.setText(current_time_string)
           
        

    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)     
    
    def gotologin(self):
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1) 
    
    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)     
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def gotosettings(self): #to settings screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def gotosales(self): #to user setting screen
        widget.removeWidget(self)

        sales= ReportScreen1(self.user)     
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()      



class PManagementScreen(QDialog):
    def __init__(self, user):
        super(PManagementScreen, self).__init__()
        self.user = user
        loadUi("ui/pmanagementscreen.ui",self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/pmanagement2.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        
        self.tableWidget.setColumnWidth(0, 50) # Table index 0, first column with 50 width pixel
        self.tableWidget.setColumnWidth(1, 250) # Table index 1, second column with 200 width pixel

        self.displayAllProductList()
        
        self.allbtn.clicked.connect(self.displayAllProductList)
        self.lugawbtn.clicked.connect(self.displayLugawProductList)
        self.mamibtn.clicked.connect(self.displayMamiProductList)
        self.maindishbtn.clicked.connect(self.displayMainDishProductList)
        self.dessertsbtn.clicked.connect(self.displayDessertsProductList)
        self.beveragesbtn.clicked.connect(self.displayBeveragesProductList)
        self.extrasbtn.clicked.connect(self.displayExtrasProductList)
        
         
        self.logoutbtn.clicked.connect(self.gotologin)     
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.reportbtn.clicked.connect(self.gotosales)
        self.settingsbtn.clicked.connect(self.gotosettings)
        
        self.addbtn.clicked.connect(self.gotoaddproduct) 
        self.deletebtn.clicked.connect(self.removeProduct)
        self.updatebtn.clicked.connect(self.updateProduct)

     # A fucntion to set the font size and alignment for items in the tableWidget
    def tableFontModify(self):
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 11))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically
                    

    def displayAllProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, printf('%.2f', price), status FROM Product ORDER BY categoryID ASC"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)  
        
        # Set font size and alignment for items in the tableWidget
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 11))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically


    def displayLugawProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, printf('%.2f', price), status FROM Product WHERE categoryID = 1"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)  

        self.tableFontModify()
                                 
    def displayMamiProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, printf('%.2f', price), status FROM Product WHERE categoryID = 2"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        self.tableFontModify()
                    
    def displayMainDishProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, printf('%.2f', price), status FROM Product WHERE categoryID = 3"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        self.tableFontModify()
                    
    def displayDessertsProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, printf('%.2f', price), status FROM Product WHERE categoryID = 4"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        self.tableFontModify()
                    
    def displayBeveragesProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, printf('%.2f', price), status FROM Product WHERE categoryID = 5"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)        

        self.tableFontModify()
                    
    def displayExtrasProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, printf('%.2f', price), status FROM Product WHERE categoryID = 6"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)        

        self.tableFontModify()
                    
    def removeProduct(self):
        
        # Get the selected row index
        row_index = self.tableWidget.currentRow()
        # Check if there is a selected row
        if row_index < 0:
            return
        selected_row_id = str(self.tableWidget.item(row_index, 0).text())
        
        try:
            delete_query = "DELETE FROM Product WHERE id = ?"
            cur.execute(delete_query, (selected_row_id,))
            conn.commit()
            
            self.tableWidget.removeRow(row_index)  
            
        except sqlite3.Error as err:
            print(f"Error: {err}")     
            
               
    def isInteger(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False


    def updateProduct(self):
            try:
                conn = sqlite3.connect('projectse_db.db')
                cur = conn.cursor()
                
                row_index = self.tableWidget.currentRow()
                if row_index < 0:
                    return
                
                selected_row_id = str(self.tableWidget.item(row_index, 0).text())

                new_productname = self.pnamefield.text() or None
                new_price = self.pricefield.text() or None
                new_status = self.comboBox.currentText() or None  # Get the selected status from the combo box
            
                formatted_price = None  # Initialize formatted_price
               
                if new_price and not self.isInteger(new_price):
                    self.error.setText("Price must be a decimal number.")
                    return
            
                if all(x is None for x in [new_productname, new_price, new_status]):
                    self.error.setText("At least one field must be filled before clicking the update.")
                else:
                    query = "UPDATE Product SET"
                    params = []

                    if new_productname:
                        query += " name = ?,"
                        params.append(new_productname)
                    if new_price:
                       query += " price = ?,"
                       formatted_price = "{:.2f}".format(float(new_price))
                       params.append(formatted_price)
                    if new_status:
                        query += " status = ?,"
                        params.append(new_status)
                    

                    query = query.rstrip(',') + " WHERE id = ?"
                    params.append(selected_row_id)
                    
                    self.error.setText("")
                    self.pnamefield.clear()
                    self.pricefield.clear()
                    self.comboBox.setCurrentIndex(0)
                    
                    cur.execute(query, tuple(params))
                    conn.commit()

                    for i, value in enumerate([new_productname,formatted_price, new_status]):
                        if value:
                            self.tableWidget.setItem(row_index, i + 1, QTableWidgetItem(value))
                            
                    self.tableFontModify()
                            
                    QMessageBox.information(self, "Success", "Product information updated successfully.")
            
            except sqlite3.Error as e:
                conn.rollback()  # Rollback the transaction in case of error
                QMessageBox.warning(self, "Error", f"An error occurred: {e}")
            finally:
                conn.close()
                                
                    
    def gotoaddproduct(self): 
        widget.removeWidget(self)
            
        aproduct = AddNewProductScreen(self.user)
        widget.addWidget(aproduct)
        widget.setCurrentIndex(widget.currentIndex()+1)        

    def gotologin(self):  #Direct to the login screen if logout button is clicked.
        widget.removeWidget(self)
            
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)    
    
    
    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreen(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
  
    def gotosettings(self): #to user screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotosales(self): #to user setting screen
        widget.removeWidget(self)

        sales= ReportScreen1(self.user)     
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex()+1)
        

    def keyPressEvent(self, event):    #To ignore close event by "ESC" key
        if event.key() == Qt.Key_Escape:
            event.ignore()       
        
        
class ReportScreen1(QDialog):
    def __init__(self, user):
        super(ReportScreen1, self).__init__()
        self.user = user
        loadUi("ui/reportscreen.ui",self)
        
        ######################################################
        
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report2.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        
        #######################################################

        #TableWidget
        self.tableWidget.setColumnWidth(0, 50) # Table index 0, first column with 50 width pixel
        self.tableWidget.setColumnWidth(1, 200) # Table index 1, second column with 200 width pixel
        self.tableWidget.setColumnWidth(2, 100) # Table index 2, three column with 100 width pixel
        self.tableWidget.setColumnWidth(3, 160) # Table index 3, fourth column with 160 width pixel

        self.displaySales()
        
        self.logoutbtn.clicked.connect(self.gotologin)     
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.p_managementbtn.clicked.connect(self.gotopmanagement)
        self.settingsbtn.clicked.connect(self.gotosettings)
        self.DSRbtn.clicked.connect(self.gotodailysale)
        


    def displaySales(self):  # To load the data from database to the pyqt table
        try:
            conn = sqlite3.connect('projectse_db.db')
            cur = conn.cursor()

            query = "SELECT id, name, printf('%.2f', Totalprice), orderType FROM Sales"
            cur.execute(query)
            rows = cur.fetchall()
            row_count = len(rows)

            # Check if there are any rows
            if row_count == 0:
                return

            column_count = len(rows[0])

            # Resize the table widget to fit the data
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setColumnCount(column_count)

            # Set the data into the table widget
            for row in range(row_count):
                for col in range(column_count):
                    item = QTableWidgetItem(str(rows[row][col]))
                    self.tableWidget.setItem(row, col, item)  

            # To make the horizontal headers text aligned to the left of the table. 
            for row in range(self.tableWidget.rowCount()):
                for column in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(row, column)
                    if item is not None:
                        item.setFont(QFont("Roboto", 11))  # Set font size
                        item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically
                        
        except sqlite3.Error as err:
            print(f"Error: {err}")

        finally:
            if 'conn' in locals():
                conn.close()
      
        
    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)     
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
        
    def gotodailysale(self): #To daily sale report screen.
        widget.removeWidget(self)


        menu = ReportScreen2(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)    
        
        
    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreen(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1) 
        
    def gotologin(self):  #Direct to the login screen if logout button is clicked.
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)    
    
        
    def gotosettings(self): #to user screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
        

    def keyPressEvent(self, event):    #To ignore close event by "ESC" key
        if event.key() == Qt.Key_Escape:
            event.ignore()

class ReportScreen2(QDialog):
    def __init__(self, user):
        super(ReportScreen2, self).__init__()
        self.user = user
        loadUi("ui/reportscreen2.ui",self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report2.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################

        #TableWidget
        self.tableWidget.setColumnWidth(0, 50) # Table index 0, first column with 50 width pixel
        self.tableWidget.setColumnWidth(1, 200) # Table index 1, second column with 200 width pixel
        self.tableWidget.setColumnWidth(2, 120) # Table index 2, three column with 100 width pixel
        self.tableWidget.setColumnWidth(3, 160) # Table index 3, fourth column with 160 width pixel
        self.tableWidget.setColumnWidth(4, 120) # Table index 3, fourth column with 160 width pixel

        self.displaydailySales()
        
        self.logoutbtn.clicked.connect(self.gotologin)     
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.settingsbtn.clicked.connect(self.gotosettings)
        self.salesbtn.clicked.connect(self.gotosales)
        self.p_managementbtn.clicked.connect(self.gotopmanagement)
        
        # Set up QDateEdit widget
        self.dateEdit.setDate(QDate.currentDate())
        self.dateEdit.dateChanged.connect(self.displaydailySales)
        self.displaydailySales()
   
    
    
    def displaydailySales(self):

        selected_date = self.dateEdit.date().toString(Qt.ISODate)

        try:
            conn = sqlite3.connect('projectse_db.db')
            cur = conn.cursor()

            query = f"SELECT Sales.id, Sales.date, Sales.name, Employee.name, printf('%.2f', Sales.Totalprice)" \
                    f"FROM Sales " \
                    f"JOIN Employee ON Sales.employeeID = Employee.id " \
                    f"WHERE DATE(Sales.date) = '{selected_date}'"

            cur.execute(query)
            rows = cur.fetchall()
            row_count = len(rows)

            # Check if there are any rows
            if row_count == 0:
                return

            column_count = len(rows[0])

            # Resize the table widget to fit the data
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setColumnCount(column_count)

            # Set the data into the table widget
            for row in range(row_count):
                for col in range(column_count):
                    item = QTableWidgetItem(str(rows[row][col]))
                    self.tableWidget.setItem(row, col, item)

            # To make the horizontal headers text aligned to the left of the table. 
            for row in range(self.tableWidget.rowCount()):
                for column in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(row, column)
                    if item is not None:
                        item.setFont(QFont("Roboto", 11))  # Set font size
                        item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically

            conn.commit()

        except sqlite3.Error as err:
            print(f"Error: {err}")

            if 'conn' in locals():
                conn.close()

        try:
            conn = sqlite3.connect('projectse_db.db')
            cur = conn.cursor()

            query = f"SELECT printf('%.2f', SUM(Sales.totalPrice)) AS total_sales FROM Sales WHERE DATE(Sales.date) = '{selected_date}'"
            cur.execute(query)
            totalsale = cur.fetchone()

            if totalsale is not None:
                totaldailysale = totalsale[0]  # Extract the total sale value from the tuple
                self.boxlabel_total.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                print("error")

            conn.commit()

        except sqlite3.Error as err:
            print(f"Error: {err}")

      
      
    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)
 
 
    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreen(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1) 
        
     
    def gotologin(self):  #Direct to the login screen if logout button is clicked.
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)    

    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)     
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex()+1)

        
    def gotosales(self): #to Report-Sale screen if menu button is clicked.
        widget.removeWidget(self)

        sales= ReportScreen1(self.user)     
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotosettings(self): #to user screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
        

    def keyPressEvent(self, event):    #To ignore close event by "ESC" key
        if event.key() == Qt.Key_Escape:
            event.ignore()

class SettingScreen(QDialog):
    def __init__(self, user):
        super(SettingScreen, self).__init__()
        self.user = user
        loadUi("ui/settingscreen.ui",self)
        
        
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings2.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  #Pixmap for the second sidebar in settings screen.
        self.usersIcon.setPixmap(QPixmap('icons/users.png'))
        #######################################################
        
        
        #redirect functions
        self.userprofbtn.clicked.connect(self.gotoadminprofscreen)
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.logoutbtn.clicked.connect(self.gotologin) 
        self.reportbtn.clicked.connect(self.gotosales)
        self.usersbtn.clicked.connect(self.gotouserscreen) 
        self.p_managementbtn.clicked.connect(self.gotopmanagement)
 

    def gotoadminprofscreen(self): #to admin profile screen
        widget.removeWidget(self)
        
        adminprof = AdminProfScreen(self.user)     
        widget.addWidget(adminprof)
        widget.setCurrentIndex(widget.currentIndex()+1)   

    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1) 
        
    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreen(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

 
    def gotologin(self):
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)  
        
        
    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)     
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotosales(self): #to Report sales setting screen
        widget.removeWidget(self)

        sales= ReportScreen1(self.user)     
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
        
    def gotouserscreen(self): #to user screen
        widget.removeWidget(self)
        
        userlist = UserScreen(self.user)     
        widget.addWidget(userlist)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
        
    
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()

class UserScreen(QDialog):
    def __init__(self, user):
        super(UserScreen, self).__init__()
        self.user = user
        loadUi("ui/userscreen.ui",self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings2.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  #Pixmap for the second sidebar in settings screen.
        self.usersIcon.setPixmap(QPixmap('icons/users.png'))
        self.editIcon.setPixmap(QPixmap('icons/edit.png'))
        
        #######################################################
        #TableWidget
        self.tableWidget.setColumnWidth(0, 50) # Table index 0, first column with 50 width pixel
        self.tableWidget.setColumnWidth(1, 200) # Table index 1, second column with 200 width pixel
        self.tableWidget.setColumnWidth(2, 100) # Table index 2, three column with 100 width pixel
        self.tableWidget.setColumnWidth(3, 160) # Table index 3, fourth column with 160 width pixel
        self.tableWidget.setColumnWidth(4, 150) # Table index 4, fifth column with 150 width pixel
        self.displayEmployee()
        
        self.logoutbtn.clicked.connect(self.gotologin)     
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.p_managementbtn.clicked.connect(self.gotopmanagement) 
        self.settingsbtn.clicked.connect(self.gotosettings)
        self.userprofbtn.clicked.connect(self.gotoadminprofscreen)
        self.editbtn.clicked.connect(self.gotouserscreenedit)
        self.reportbtn.clicked.connect(self.gotosales)   
        
    def displayEmployee(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM employee"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)  
        
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 11))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically
        
    def gotoadminprofscreen(self): #to admin profile screen
        widget.removeWidget(self)
        
        adminprof = AdminProfScreen(self.user)     
        widget.addWidget(adminprof)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
              
    def gotologin(self):  #Direct to the login screen if logout button is clicked.
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)    
    
    
    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = AdminCashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotohome(self):
        widget.removeWidget(self)

        home = HomeScreen(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotopmanagement(self):
        widget.removeWidget(self)

        product = PManagementScreen(self.user)     
        widget.addWidget(product)
        widget.setCurrentIndex(widget.currentIndex()+1)


    def gotosettings(self): #to user screen
        widget.removeWidget(self)

        settings = SettingScreen(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
        
    def gotouserscreenedit(self): #to user screen
        widget.removeWidget(self)

        usersedit = UserScreenEditMode(self.user)     
        widget.addWidget(usersedit)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    
    def gotosales(self): #to user setting screen
        widget.removeWidget(self)

        sales= ReportScreen1(self.user)     
        widget.addWidget(sales)
        widget.setCurrentIndex(widget.currentIndex()+1)
            
            
    def keyPressEvent(self, event):    #To ignore close event by "ESC" key
        if event.key() == Qt.Key_Escape:
            event.ignore()


class UserScreenEditMode(QDialog):
    def __init__(self, user):
        super(UserScreenEditMode, self).__init__()
        self.user = user
        loadUi("ui/userscreen_edit.ui",self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings2.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  #Pixmap for the second sidebar in settings screen.
        self.usersIcon.setPixmap(QPixmap('icons/users.png'))
        #######################################################
        #TableWidget
        self.tableWidget.setColumnWidth(0, 50) # Table index 0, first column with 50 width pixel
        self.tableWidget.setColumnWidth(1, 200) # Table index 1, second column with 200 width pixel
        self.tableWidget.setColumnWidth(2, 100) # Table index 2, three column with 100 width pixel
        self.tableWidget.setColumnWidth(3, 160) # Table index 3, fourth column with 160 width pixel
        self.tableWidget.setColumnWidth(4, 150) # Table index 4, fifth column with 150 width pixel
        self.displayEmployee()
         
        self.backbtn.clicked.connect(self.gotouserscreen) 
        self.dropbtn.clicked.connect(self.deleteEmployee)
        self.addbtn.clicked.connect(self.gotoadduser)
        
    def displayEmployee(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM employee"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)  
        
        #To set the row items font size and text alignment to center.
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 11))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically


    def deleteEmployee(self):
        # Get the selected row index
        row_index = self.tableWidget.currentRow()
        # Check if there is a selected row
        if row_index < 0:
            return
        selected_row_id = int(self.tableWidget.item(row_index, 0).text())
        selected_username = self.tableWidget.item(row_index, 3).text()  #  username is in column index 3

        # Check if the user is trying to delete their own data
        if selected_username == self.user:
            QMessageBox.warning(self, "Warning", "You cannot delete your own data.")
            return

        delete_query = "DELETE FROM Employee WHERE id =? "
        cur.execute(delete_query, (selected_row_id,))
        conn.commit()
        self.tableWidget.removeRow(row_index)


    def gotoadduser(self): #to add a new user.
        widget.removeWidget(self)
        
        newuser = AddNewUserScreen(self.user)     
        widget.addWidget(newuser)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
        
    def gotouserscreen(self): #to user screen
        widget.removeWidget(self)
        
        userlist = UserScreen(self.user)     
        widget.addWidget(userlist)
        widget.setCurrentIndex(widget.currentIndex()+1)
  

    def keyPressEvent(self, event):    #To ignore close event by "ESC" key
        if event.key() == Qt.Key_Escape:
            event.ignore()



######################## CASHIER SCREENS ############################### 

class HomeScreenForCashier(QDialog):
    def __init__(self, user):
        super(HomeScreenForCashier, self).__init__()
        self.user = user
        loadUi("ui/homescreenforcashier.ui",self)
        
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home2.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        
        self.dashboardimg.setPixmap(QPixmap('icons/layout.png'))
        self.dashboardimg_2.setPixmap(QPixmap('icons/coca-leaves.png'))
        self.topimg.setPixmap(QPixmap('icons/badge.png'))
        self.pesoimg.setPixmap(QPixmap('icons/peso.png'))
        self.dailyimg.setPixmap(QPixmap('icons/24-hours.png'))
        
        
        #Redirect Functions
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.settingsbtn.clicked.connect(self.gotosettings) 

        # A Function to display the top 5 selling products based on sales
        self.displayTopSellingProduct()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_label)
        self.timer.start(1000)  # Update every 1 second

        # Initial update of the time label function
        self.update_time_label()
        
        current_date = date.today()
        
        try:
            query = f"SELECT printf('%.2f', SUM(Sales.totalPrice)) AS total_sales FROM Sales WHERE DATE(Sales.date) = '{current_date}'"
            cur.execute(query)
            totalsale = cur.fetchone()

            if totalsale is not None:
                totaldailysale = totalsale[0]  # Extract the total sale value from the tuple
                self.boxlabel_total.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                self.boxlabel_total.setText("00.00")  # Set label text to indicate no data available

        except Error as err:
            print(f"Error executing query: {err}")

        try:
            query = f"SELECT COUNT(*) AS totalSales FROM Sales  WHERE DATE(date) = '{current_date}'"
            cur.execute(query)
            totalsalecount = cur.fetchone()

            if totalsalecount is not None:
                totaldailysale = totalsalecount[0]  # Extract the total sale value from the tuple
                self.boxlabel_sale.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                self.boxlabel_sale.setText("0")  # Set label text to indicate no data available

        except Error as err:
            print(f"Error executing query: {err}")
    
    

    def displayTopSellingProduct(self):  #To load the data from database to the pyqt table
        query = "SELECT productName, totalQuantitySold \
                FROM ( SELECT P.name AS productName, SUM(T.quantity) AS totalQuantitySold \
                FROM \"Transaction\" T \
                JOIN Product P ON T.productID = P.id \
                GROUP BY T.productID \
                ORDER BY totalQuantitySold \
                DESC LIMIT 5 ) AS topSoldProducts"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)
        
        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 11))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically
        
    def update_time_label(self):
        current_datetime = QDateTime.currentDateTime()
        current_time_string = current_datetime.toString("MM-dd-yyyy HH:mm:ss")
        self.time.setText(current_time_string)
           
        

    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = CashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)     
    
    def gotologin(self):
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1) 
    
    
    def gotosettings(self): #to settings screen
        widget.removeWidget(self)

        settings = SettingScreenForCashier(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
        
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()      

class CashierScreen(QDialog):
    def __init__(self, user):
        super(CashierScreen, self).__init__()
        self.user = user
        loadUi("ui/cashierscreen.ui",self)
        ######################################################
        #Pixmap for the pngs images within the sidebar.
        self.homeIcon.setPixmap(QPixmap('icons/home.png')) 
        self.menuIcon.setPixmap(QPixmap('icons/menu2.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        #Redirect Functions
        self.homebtn.clicked.connect(self.gotohome)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.settingsbtn.clicked.connect(self.gotosettings)
        

        self.tableWidget.setColumnWidth(0, 300) # Table index 0, first column with 50 width pixel
        self.tableWidget.setColumnWidth(1, 100) # Table index 1, second column with 200 width pixel  
        
        self.tableWidget2.setColumnWidth(0, 50) # Table index 0, first column with 50 width pixel
        self.tableWidget2.setColumnWidth(1, 135) 
        self.tableWidget2.setColumnWidth(2, 100) 
        
    
        self.lugawbtn.clicked.connect(self.displayLugawProductList)
        self.mamibtn.clicked.connect(self.displayMamiProductList)
        self.maindishbtn.clicked.connect(self.displayMainDishProductList)
        self.dessertsbtn.clicked.connect(self.displayDessertsProductList)
        self.beveragesbtn.clicked.connect(self.displayBeveragesProductList)
        self.extrasbtn.clicked.connect(self.displayExtrasProductList)

        # Connect signals
        self.tableWidget.itemSelectionChanged.connect(self.addSelectedProductToInvoice)
        self.tableWidget2.itemChanged.connect(self.updateAmount)
        
    def addSelectedProductToInvoice(self):
        print("Adding selected product to invoice...")  # Add this line
        # Retrieve the selected row from TableWidget
        selected_indexes = self.tableWidget.selectedIndexes()
        if not selected_indexes:
            return
 

        # Extract product name from the selected row
        row = selected_indexes[0].row()
        product_name = str(self.tableWidget.item(row, 0).text())  # ProductName

        # Fetch product information based on product name
        query = "SELECT id, price FROM Product WHERE name = ?"
        cur.execute(query, (product_name,))
        product_info = cur.fetchone()

        if product_info:
            product_id = product_info[0]
            price = product_info[1]

            # Check if the product already exists in TableWidget2
            existing_row = self.findExistingProductRow(product_id)
            if existing_row is not None:
                # If the product exists, inform the user or take appropriate action
                QMessageBox.warning(self, "Duplicate Product", "This product is already in the invoice.")
            else:
                # If the product does not exist, add a new row
                row_position = self.tableWidget2.rowCount()
                self.tableWidget2.insertRow(row_position)
                self.tableWidget2.setItem(row_position, 0, QTableWidgetItem(str(1)))  # Default quantity to 1
                self.tableWidget2.setItem(row_position, 1, QTableWidgetItem(product_name))  # ProductName
                self.tableWidget2.setItem(row_position, 2, QTableWidgetItem(str(price)))  # Amount (ProductPrice)
                self.tableWidget2.setItem(row_position, 3, QTableWidgetItem(product_id))  # ProductID
            
                for row in range(self.tableWidget2.rowCount()):
                    for column in range(self.tableWidget2.columnCount()):
                        item = self.tableWidget2.item(row, column)
                        if item is not None:
                            item.setFont(QFont("Roboto", 10))  # Set font size
                            item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically
            
    def findExistingProductRow(self, product_id):
        # Search for the product ID in TableWidget2
        for row in range(self.tableWidget2.rowCount()):
            item = self.tableWidget2.item(row, 3)  # ProductID column
            if item is not None:
                print("Comparing:", item.text(), "with:", str(product_id))
                if item.text() == str(product_id):
                    print("Found duplicate at row:", row)
                    return row
        return None


    def updateAmount(self, item):
        # Calculate the amount based on the quantity entered
        if item.column() == 0:  # Quantity column
            row = item.row()
            quantity_item = self.tableWidget2.item(row, 0)
            amount_item = self.tableWidget2.item(row, 2)

            if quantity_item and amount_item:
                quantity = int(quantity_item.text())
                price = float(amount_item.text())
                amount = quantity * price
                amount_item.setText("{:.2f}".format(amount))  # Update the amount

    def displayLugawProductList(self):  #To load the data from database to the pyqt table
       
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/lugaw.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 1 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)
                
        
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
    
    def displayMamiProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/mami.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 2 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
    
    def displayMainDishProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/maindish.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 3 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)
      
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  

    def displayDessertsProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/desserts.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 4 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
                    
    def displayBeveragesProductList(self):  #To load the data from database to the pyqt table
        
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/beverages.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 5 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)        

        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
                    
    def displayExtrasProductList(self):  #To load the data from database to the pyqt table
       
        self.clearTableWidgetSelection()
        self.imgplaceholder.setPixmap(QPixmap('icons/extra.png'))
        
        query = "SELECT name, printf('%.2f', price) FROM Product WHERE categoryID = 6 AND status = 'Available'"
        cur.execute(query)
        rows = cur.fetchall()
        row_count = len(rows)

        # Check if there are any rows
        if row_count == 0:
            return

        column_count = len(rows[0])

        # Resize the table widget to fit the data
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setColumnCount(column_count)

        # Set the data into the table widget
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem(str(rows[row][col]))
                self.tableWidget.setItem(row, col, item)      
                  
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item is not None:
                    item.setFont(QFont("Roboto", 13))  # Set font size
                    item.setTextAlignment(Qt.AlignCenter)  # Center-align text horizontally and vertically  
                     
    def clearTableWidgetSelection(self):
        self.tableWidget.clearSelection()  

    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreenForCashier(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotologin(self):  #To logout from the system
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1) 
    
    
    def gotosettings(self): #to user setting screen
        widget.removeWidget(self)

        settings = SettingScreenForCashier(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()    

class SettingScreenForCashier(QDialog):
    def __init__(self, user):
        super(SettingScreenForCashier, self).__init__()
        self.user = user
        loadUi("ui/settingscreenforcashier.ui",self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png')) 
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings2.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  #Pixmap for the second sidebar in settings screen.
        #######################################################
        
        #redirect button functions
        self.homebtn.clicked.connect(self.gotohome)
        self.logoutbtn.clicked.connect(self.gotologin) 
        self.userprofbtn.clicked.connect(self.gotouserprofscreen) 
        self.menubtn.clicked.connect(self.gotocashierscreen)

    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreenForCashier(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def gotologin(self): #To login screen if logout button is clicked.
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)  
        
        
    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = CashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1) 
        
        
    def gotouserprofscreen(self): #to user profile screen
        widget.removeWidget(self)
        
        userprof = UserProfScreen(self.user)     
        widget.addWidget(userprof)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen. (Close Event)
        if event.key() == Qt.Key_Escape:
            event.ignore()

class UserProfScreen(QDialog):
    def __init__(self, user):
        super(UserProfScreen, self).__init__()
        self.user = user
        loadUi("ui/userprofilescreen.ui",self)
        ######################################################
        #Pixmap for the pngs images within the sidebar.
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    # Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings2.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        self.profileimg.setPixmap(QPixmap('icons/cresume.png'))  
        #######################################################
        #Pixmap for the second sidebar in settings screen.
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  
        #######################################################
        #Redirect Functions
        self.homebtn.clicked.connect(self.gotohome)
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.settingsbtn.clicked.connect(self.gotosettings)
        
        try:
            conn = sqlite3.connect('projectse_db.db')
            cur = conn.cursor()
            
            query = 'SELECT name, role, username, password FROM employee WHERE username = \'' + user + "\'"  #base sa nakalogin na user mafefetch lahat ng data information ni user.
            cur.execute(query)
            user_info = cur.fetchone()

            if user_info is not None:       #displaying all user info in the database.
                name, role, username, password = user_info
                self.boxlabel_name.setText(name)
                self.boxlabel_role.setText(role)
                self.boxlabel_username.setText(username)
                self.password.setText(password)
                self.password.setEchoMode(QtWidgets.QLineEdit.Password)
                self.viewpassword.setPixmap(QPixmap('icons/view.png')) 
            else:
                print("User not found")

        except sqlite3.Error as err:
            print(f"Error: {err}")

        finally:
            if conn:
                conn.close()
        self.editbtn.clicked.connect(self.toggle_echo_mode)
        
    def toggle_echo_mode(self):
        # Toggle the echo mode of the password field between Normal and Password
        if self.password.echoMode() == QLineEdit.Normal:
            self.password.setEchoMode(QLineEdit.Password)
            self.viewpassword.setPixmap(QPixmap('icons/view.png'))  
        else:
            self.password.setEchoMode(QLineEdit.Normal)
            self.viewpassword.setPixmap(QPixmap('icons/hide.png'))  
            

    def gotocashierscreen(self): #To cashier screen if menu button is clicked.
        widget.removeWidget(self)

        menu = CashierScreen(self.user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotohome(self): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreenForCashier(self.user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)
   
    def gotologin(self):
        widget.removeWidget(self)
        
        login = LoginScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotosettings(self): #to user screen
        widget.removeWidget(self)

        settings = SettingScreenForCashier(self.user)     
        widget.addWidget(settings)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
        
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()
        




#main
app = QApplication(sys.argv)
login = LoginScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(login)
widget.setFixedHeight(800)
widget.setFixedWidth(1200)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")