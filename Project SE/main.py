import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import mysql.connector
from mysql.connector.errors import *
import warnings


# Suppress DeprecationWarnings globally
warnings.simplefilter("ignore", category=DeprecationWarning)

########################################################################
########################################################################
########################################################################

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="WFZximct1!",                   #MYSQL connection
    database="seproject_db",
    autocommit=True ) 
    
cur = conn.cursor()

########################################################################
########################################################################
################# Starting page with Login Screen  #####################


class LoginScreen(QDialog):
    def __init__(self):
        super(LoginScreen, self).__init__()
        loadUi("ui/loginscreen.ui", self)
        self.passwordfield.setEchoMode(QtWidgets.QLineEdit.Password)
        self.loginbtn.clicked.connect(self.login)
        self.userfield.returnPressed.connect(self.login)  ###Key event
        self.passwordfield.returnPressed.connect(self.login)  ### Para gumana yung Enter key as click to the loginbtn

    def login(self):
        user = self.userfield.text()
        password = self.passwordfield.text()
        if len(user) == 0 or len(password) == 0:
            self.error.setText("Please input all fields.")
        else:
            try:
                conn = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    passwd="WFZximct1!",
                    database="seproject_db")
                cur = conn.cursor()

                query = 'SELECT password FROM employee WHERE username = \'' + user + "\'"    #a query to check the the password of the user if matches to the username data.
                cur.execute(query,)

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

            except mysql.connector.Error as err:
                print(f"Error: {err}")

            finally:
                if 'conn' in locals() and conn.is_connected():
                    conn.close()

    def redirect_based_on_role(self, user):  # redirect based on employee's role after login
        try:
            query = 'SELECT role FROM employee WHERE username = \'' + user + "\'"
            cur.execute(query)

            result_role = cur.fetchone()    
            if result_role is not None:                 
                role = result_role[0].strip()
                if role == 'admin' or role == 'Admin':  
                    self.gotohomescreen(user)   # if the user is an admin, go to user screen
                elif role == 'cashier' or role == 'Cashier': 
                    self.gotocashierscreen(user)  # if the user is a cashier, go to cashier screen
                else:
                    self.error.setText("Unknown role")
                    self.error.setStyleSheet("color: red")   # Turns the Qlabel text color to red so we can know that the displayed text is an error message.
            else:
                self.error.setText("Role not found for user")
                self.error.setStyleSheet("color: red")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
            
    def gotohomescreen(self, user): #to home profile screen
        widget.removeWidget(self)
        
        home = HomeScreen(user)     
        widget.addWidget(home)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def gotocashierscreen(self, user): #To cashier screen
        widget.removeWidget(self)

        menu = CashierScreen(user)
        widget.addWidget(menu)
        widget.setCurrentIndex(widget.currentIndex()+1)
        
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape: 
            event.ignore()
     
########################################################################
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
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
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

        #To Insert or Register a new data to Employee Table
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
                #establish the connection inside the try function
                conn = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    passwd="WFZximct1!",
                    database="seproject_db",
                    autocommit=True)
                cur = conn.cursor()
                cur.execute("INSERT INTO Employee (name, role, username, password) "
                            "VALUES (%s, %s, %s, %s)", user_info)
                self.error.setText("")
                QMessageBox.information(self, "Success", "Successfully Encoded!.")
                self.namefield.clear()
                self.usernamefield.clear()
                self.passwordfield.clear()
        
            except mysql.connector.Error as err:
                print(f"Error: {err}")

            finally:
                if 'conn' in locals() and conn.is_connected():
                    conn.close()

    def backfunction(self):
        widget.removeWidget(self)
        
        back = UserScreenEditMode(self.user)
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def keyPressEvent(self, event):    #To ignore close event by "ESC" key
        if event.key() == Qt.Key_Escape:
            event.ignore()


class AddNewProductScreen(QDialog):
    def __init__(self, user):
        super(AddNewProductScreen, self).__init__()
        
        self.user = user
        
        loadUi("ui/add_new_product.ui", self)
        self.insertbtn.clicked.connect(self.addproduct)
        self.backbtn.clicked.connect(self.backfunction)

        # create a button group for the radio buttons
        self.roleButtonGroup = QButtonGroup()
        self.roleButtonGroup.addButton(self.lugawbtn)
        self.roleButtonGroup.addButton(self.mamibtn)
        self.roleButtonGroup.addButton(self.maindishbtn)
        self.roleButtonGroup.addButton(self.dessertsbtn)
        self.roleButtonGroup.addButton(self.beveragesbtn)
        self.roleButtonGroup.addButton(self.extrasbtn)

        # connect the button group's buttonClicked signal to a slot
        self.roleButtonGroup.buttonClicked.connect(self.handleCategorySelection)

    def handleCategorySelection(self, radioButton):
        # get the selected radio button's text
        selected_category = radioButton.text()
        # do something with the selected role, such as storing it in a variable
        print("Selected Category:", selected_category)

        #To Insert or Register a new data to Employee Table
    def addproduct(self):
        try:
            productname = self.pnamefield.text()
            price = self.pricefield.text()

            if len(productname) == 0 or len(price) == 0:
                self.error.setText("Please fill in all necessary fields")
            elif not self.lugawbtn.isChecked() and not \
                    self.mamibtn.isChecked() and not \
                    self.maindishbtn.isChecked() and not \
                    self.dessertsbtn.isChecked() and not \
                    self.beveragesbtn.isChecked() and not \
                    self.extrasbtn.isChecked():
                    self.error.setText("Please select a category for the product.")

            else:
                category = "1" if self.lugawbtn.isChecked() else \
                        "2" if self.mamibtn.isChecked() else \
                        "3" if self.maindishbtn.isChecked() else \
                        "4" if self.dessertsbtn.isChecked() else \
                        "5" if self.beveragesbtn.isChecked() else \
                        "6" if self.extrasbtn.isChecked() else None

                product_data = [productname, price, category]

                # Establish the database connection
                conn = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    passwd="WFZximct1!",
                    database="seproject_db",
                    autocommit=True)
                cur = conn.cursor()

                # Execute the SQL query
                cur.execute("INSERT INTO Product (name, price, categoryID) "
                            "VALUES (%s, %s, %s)", product_data)

                # Clear any previous error messages
                self.error.setText("")

                # Show success message
                QMessageBox.information(self, "Success", "Successfully Encoded!.")

                # Clear input fields
                self.pnamefield.clear()
                self.pricefield.clear()

        except mysql.connector.Error as err:
            # Print the error to the console
            print(f"Error: {err}")

            # Display error message to the user
            self.error.setText("An error occurred while inserting the product.")

        finally:
            # Close the database connection
            if 'conn' in locals() and conn.is_connected():
                conn.close()

    def backfunction(self):
        widget.removeWidget(self)
        
        back = PManagementScreen(self.user)
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def keyPressEvent(self, event):    #To ignore close event by "ESC" key
        if event.key() == Qt.Key_Escape:
            event.ignore()

            
class AdminProfScreen(QDialog):
    def __init__(self, user):
        super(AdminProfScreen, self).__init__()
        self.user = user
        loadUi("ui/adminprofilescreen.ui",self)
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        self.image.setPixmap(QPixmap('icons/placeholder.jpg'))  
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  #Pixmap for the second sidebar in settings screen.
        self.usersIcon.setPixmap(QPixmap('icons/users.png'))
        #######################################################
        #Redirect Functions
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.homebtn.clicked.connect(self.gotohome)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.p_managementbtn.clicked.connect(self.gotopmanagement)
        self.settingsbtn.clicked.connect(self.gotosettings)
        self.usersbtn.clicked.connect(self.gotouserscreen)
        self.reportbtn.clicked.connect(self.gotosales)
        
        
   
        try:
            query = f'SELECT name, role, username, password FROM employee WHERE username = \'' + user + "\'"  #base sa nakalogin na user mafefetch lahat ng data information ni user.
            cur.execute(query)
            user_info = cur.fetchone()

            if user_info is not None:       #displaying all user info in the database.
                name, role, username, password = user_info
                self.boxlabel_name.setText(name)
                self.boxlabel_role.setText(role)
                self.boxlabel_username.setText(username)
                self.password.setText(password)
                self.password.setEchoMode(QtWidgets.QLineEdit.Password)
            else:
                print("User not found")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    
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


    def gotouserscreen(self): #to user screen
        widget.removeWidget(self)
        
        userlist = UserScreen(self.user)     
        widget.addWidget(userlist)
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
    
        
    def keyPressEvent(self, event): #To ignore 'ESC' Key, kasi nireremove niya yung current stacked page sa screen.
        if event.key() == Qt.Key_Escape:
            event.ignore()            

class HomeScreen(QDialog):
    def __init__(self, user):
        super(HomeScreen, self).__init__()
        self.user = user
        loadUi("ui/homescreen.ui",self)
        
        ######################################################
        self.homeIcon.setPixmap(QPixmap('icons/home.png'))    #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        
        
        #Redirect Functions
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.settingsbtn.clicked.connect(self.gotosettings) 
        self.reportbtn.clicked.connect(self.gotosales)
        self.p_managementbtn.clicked.connect(self.gotopmanagement) 

        
        self.displayTopSellingProduct()
        
        try:
            query = f"SELECT SUM(Sales.totalPrice) AS total_sales FROM Sales WHERE DATE(Sales.date) = CURDATE()"
            cur.execute(query)
            totalsale = cur.fetchone()

            if totalsale is not None:
                totaldailysale = totalsale[0]  # Extract the total sale value from the tuple
                self.boxlabel_total.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                print("error")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            
        try:
            query = f"SELECT\
                    COUNT(*) AS totalSales \
                    FROM Sales \
                    WHERE DATE(date) = CURDATE()\
                    "
    
            cur.execute(query)
            totalsale = cur.fetchone()

            if totalsale is not None:
                totaldailysale = totalsale[0]  # Extract the total sale value from the tuple
                self.boxlabel_sale.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                print("error")

        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
    
    def displayTopSellingProduct(self):  #To load the data from database to the pyqt table
        query = "SELECT productName, totalQuantitySold \
                FROM ( SELECT P.name AS productName, SUM(T.quantity) AS totalQuantitySold \
                FROM Transaction T \
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
        self.p_mIcon.setPixmap(QPixmap('icons/productm.png'))
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
        self.deletebtn.clicked.connect(self.deleteProduct)
        self.updatebtn.clicked.connect(self.updateProduct)


    def displayAllProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM Product ORDER BY categoryiD ASC"
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
        
        #To make the horizontal headers text aligned to the left of the table. 
        for col in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(col)
            if header_item is not None:
                header_text = header_item.text()
                header_item = QTableWidgetItem(header_text)
                header_item.setTextAlignment(Qt.AlignLeft)
                self.tableWidget.setHorizontalHeaderItem(col, header_item)
        
        #Table Design 
        self.setStyleSheet("""
            QTableWidget {
                background-color: white; /* Set default background color */
            }
            


            QTableWidget::item:hover {
                background-color: #FB9722; /* Set background color for header on hover */   
            }

            QHeaderView::section {
                font-family:'Inter';
                font-size: 13px;
                font-weight: bold;
                background-color: #FB9722; /* Set background color for header */
                color: black; /* Set text color for header */
                padding-left: 5px; /* Add padding to the left for better appearance */
            }       
        """)
        
    def displayLugawProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM Product WHERE categoryID = 1"
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
                
    def displayMamiProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM Product WHERE categoryID = 2"
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

    def displayMainDishProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM Product WHERE categoryID = 3"
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

    def displayDessertsProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM Product WHERE categoryID = 4"
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


    def displayBeveragesProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM Product WHERE categoryID = 5"
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

    def displayExtrasProductList(self):  #To load the data from database to the pyqt table
        query = "SELECT * FROM Product WHERE categoryID = 6"
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

    def deleteProduct(self):
        
        # Get the selected row index
        row_index = self.tableWidget.currentRow()
        # Check if there is a selected row
        if row_index < 0:
            return
        selected_row_id = str(self.tableWidget.item(row_index, 0).text())
        
        try:
            delete_query = "DELETE FROM Product WHERE id = %s"
            cur.execute(delete_query, (selected_row_id,))
            conn.commit()
            
            self.tableWidget.removeRow(row_index)  
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")         


    def updateProduct(self):
            try:
                row_index = self.tableWidget.currentRow()
                if row_index < 0:
                    return

                selected_row_id = str(self.tableWidget.item(row_index, 0).text())

                new_productname = self.pnamefield.text() or None
                new_price = self.pricefield.text() or None
               

               
                if all(x is None for x in [new_productname, new_price]):
                    self.error.setText("At least one field must be filled before clicking the update.")
                else:
                    query = "UPDATE Product SET"
                    params = []

                    if new_productname:
                        query += " name = %s,"
                        params.append(new_productname)
                    if new_price:
                        query += " price = %s,"
                        params.append(new_price)
                    

                    query = query.rstrip(',') + " WHERE id = %s"
                    params.append(selected_row_id)
                    
                    self.error.setText("")
                    self.pnamefield.clear()
                    self.pricefield.clear()
                    
                    cur.execute(query, tuple(params))
                    conn.commit()

                    for i, value in enumerate([new_productname, new_price]):
                        if value:
                            self.tableWidget.setItem(row_index, i + 1, QTableWidgetItem(value))
                            

            except Exception as e:
                if e.errno == 1062:
                    self.error.setText ("The product name is already exist" )
                elif e.errno == 1366:
                    self.error.setText ("Incorrect decimal value for pricing")
                else:
                    print("An error occurred:", e)

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
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
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
        
        
        self.voidbtn.clicked.connect(self.deleteSales)


    def deleteSales(self):
        # Get the selected row index
        row_index = self.tableWidget.currentRow()
        # Check if there is a selected row
        if row_index < 0:
            return
        selected_row_id = int(self.tableWidget.item(row_index, 0).text())

        try:
            delete_query1 = "DELETE FROM Transaction WHERE salesID = %s"
            cur.execute(delete_query1, (selected_row_id,))
            conn.commit()

            delete_query2 = "DELETE FROM Sales WHERE id = %s"
            cur.execute(delete_query2, (selected_row_id,))
            conn.commit()
            
            self.tableWidget.removeRow(row_index)     
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")         


    def displaySales(self):  #To load the data from database to the pyqt table
        query = "SELECT id, name, totalPrice, orderType FROM Sales"
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
        
        #To make the horizontal headers text aligned to the left of the table. 
        for col in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(col)
            if header_item is not None:
                header_text = header_item.text()
                header_item = QTableWidgetItem(header_text)
                header_item.setTextAlignment(Qt.AlignLeft)
                self.tableWidget.setHorizontalHeaderItem(col, header_item)
        
        #Table Design 
        self.setStyleSheet("""
            QTableWidget {
                background-color: white; /* Set default background color */
            }
            


            QTableWidget::item:hover {
                background-color: #FB9722; /* Set background color for header on hover */   
            }

            QHeaderView::section {
                font-family:'Inter';
                font-size: 13px;
                font-weight: bold;
                background-color: #FB9722; /* Set background color for header */
                color: black; /* Set text color for header */
                padding-left: 5px; /* Add padding to the left for better appearance */
            }       
        """)
      
        
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
        self.reportIcon.setPixmap(QPixmap('icons/report.png'))
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
            query = f"SELECT Sales.id, Sales.date, Sales.name, Employee.name, Sales.totalPrice " \
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

            #To make the horizontal headers text aligned to the left of the table. 
            for col in range(self.tableWidget.columnCount()):
                header_item = self.tableWidget.horizontalHeaderItem(col)
                if header_item is not None:
                    header_text = header_item.text()
                    header_item = QTableWidgetItem(header_text)
                    header_item.setTextAlignment(Qt.AlignLeft)
                    self.tableWidget.setHorizontalHeaderItem(col, header_item)

            #Table Design 
            self.setStyleSheet("""
            QTableWidget {
                background-color: white; /* Set default background color */
            }
            


            QTableWidget::item:hover {
                background-color: #FB9722; /* Set background color for header on hover */   
            }

            QHeaderView::section {
                font-family:'Inter';
                font-size: 13px;
                font-weight: bold;
                background-color: #FB9722; /* Set background color for header */
                color: black; /* Set text color for header */
                padding-left: 5px; /* Add padding to the left for better appearance */
            }       
        """)
            
            conn.commit()
            
            self.tableWidget.update()
            
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    
        try:
            query = f"SELECT SUM(Sales.totalPrice) AS total_sales FROM Sales WHERE DATE(Sales.date) = '{selected_date}'"
            cur.execute(query)
            totalsale = cur.fetchone()

            if totalsale is not None:
                totaldailysale = totalsale[0]  # Extract the total sale value from the tuple
                self.boxlabel_total.setText(str(totaldailysale))  # Convert to string before setting as label text
            else:
                print("error")

        except mysql.connector.Error as err:
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
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
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
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
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
        
        #To make the horizontal headers text aligned to the left of the table. 
        for col in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(col)
            if header_item is not None:
                header_text = header_item.text()
                header_item = QTableWidgetItem(header_text)
                header_item.setTextAlignment(Qt.AlignLeft)
                self.tableWidget.setHorizontalHeaderItem(col, header_item)
        
        #Table Design 
        self.setStyleSheet("""
            QTableWidget {
                background-color: white; /* Set default background color */
            }
            

            QTableWidget::item:hover {
                background-color: #FB9722; /* Set background color for header on hover */   
            }

            QHeaderView::section {
                font-family:'Inter';
                font-size: 13px;
                font-weight: bold;
                background-color: #FB9722; /* Set background color for header */
                color: black; /* Set text color for header */
                padding-left: 5px; /* Add padding to the left for better appearance */
            }       
        """)
        
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
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
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
        
        #To make the horizontal headers text aligned to the left of the table. 
        for col in range(self.tableWidget.columnCount()):
            header_item = self.tableWidget.horizontalHeaderItem(col)
            if header_item is not None:
                header_text = header_item.text()
                header_item = QTableWidgetItem(header_text)
                header_item.setTextAlignment(Qt.AlignLeft)
                self.tableWidget.setHorizontalHeaderItem(col, header_item)
        
        #Table Design 
        self.setStyleSheet("""
            QTableWidget {
                background-color: white; /* Set default background color */
            }
            


            QTableWidget::item:hover {
                background-color: #FB9722; /* Set background color for header on hover */   
            }

            QHeaderView::section {
                font-family:'Inter';
                font-size: 13px;
                font-weight: bold;
                background-color: #FB9722; /* Set background color for header */
                color: black; /* Set text color for header */
                padding-left: 5px; /* Add padding to the left for better appearance */
            }       
        """)



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

        delete_query = "DELETE FROM Employee WHERE id = %s"
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
class CashierScreen(QDialog):
    def __init__(self, user):
        super(CashierScreen, self).__init__()
        self.user = user
        loadUi("ui/cashierscreen.ui",self)
        ######################################################
        #Pixmap for the pngs images within the sidebar.
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        #Redirect Functions
        self.logoutbtn.clicked.connect(self.gotologin)
        self.settingsbtn.clicked.connect(self.gotosettings)  
    
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
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        #######################################################
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  #Pixmap for the second sidebar in settings screen.
        #######################################################
        
        #redirect button functions
        self.logoutbtn.clicked.connect(self.gotologin) 
        self.userprofbtn.clicked.connect(self.gotouserprofscreen) 
        self.menubtn.clicked.connect(self.gotocashierscreen)
    
    
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
        self.menuIcon.setPixmap(QPixmap('icons/menu.png'))
        self.settingIcon.setPixmap(QPixmap('icons/settings.png'))
        self.logoutIcon.setPixmap(QPixmap('icons/shutdown.png'))
        self.image.setPixmap(QPixmap('icons/placeholder.jpg'))  
        #######################################################
        #Pixmap for the second sidebar in settings screen.
        self.userprofIcon.setPixmap(QPixmap('icons/user.png'))
        self.appearanceIcon.setPixmap(QPixmap('icons/appearance.png'))  
        #######################################################
        #Redirect Functions
        self.menubtn.clicked.connect(self.gotocashierscreen)
        self.logoutbtn.clicked.connect(self.gotologin)
        self.settingsbtn.clicked.connect(self.gotosettings)
        
        try:
            query = f'SELECT name, role, username, password FROM employee WHERE username = \'' + user + "\'"  #base sa nakalogin na user mafefetch lahat ng data information ni user.
            cur.execute(query)
            user_info = cur.fetchone()

            if user_info is not None:       #displaying all user info in the database.
                name, role, username, password = user_info
                self.boxlabel_name.setText(name)
                self.boxlabel_role.setText(role)
                self.boxlabel_username.setText(username)
                self.password.setText(password)
                self.password.setEchoMode(QtWidgets.QLineEdit.Password)
            else:
                print("User not found")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    
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