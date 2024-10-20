import mysql.connector as m, time as t, datetime as dt

con = m.connect(host='localhost', user='root', password='root', charset='utf8', database='bank')
cur=con.cursor()

def getName(id):
    cur.execute(f"SELECT name FROM customer WHERE user_id = '{id}'")
    return cur.fetchone()[0]

def auth(userId, password):
    cur.execute(f"SELECT count(user_id) FROM customer WHERE user_id = '{userId}' and passcode = '{password}'")
    res = cur.fetchone()
    if res[0] == 0:
        return "error"
    else:
        return userId

def checkBalance(userId):
    cur.execute(f"SELECT bal FROM customer WHERE user_id = {userId}")
    return cur.fetchone()[0]

def deposit(userId, amt):
    cur.execute(f"UPDATE customer SET bal = bal + {amt} WHERE user_id = '{userId}'")
    cur.execute(f"SELECT max(t_id) FROM transact")
    cmd = cur.fetchone()
    newTransacId = cmd[0] + 1 if cmd[0] is not None else 1

    curr_date = t.strftime('%Y-%m-%d')
    curr_time = t.strftime('%H:%M:%S')

    cur.execute(f"INSERT INTO transact VALUES({newTransacId}, {userId}, '{curr_date}', '{curr_time}',{amt}, null, {userId})")
    
    con.commit()
    t.sleep(1.0)
    print(f"Amount of ₹{amt} has been deposited into your account.\n")


def withdraw(userId, amt):
    bal = checkBalance(userId)
    if amt > bal: 
        t.sleep(0.5)
        print("Insufficient funds.\n")
        return None
    cur.execute(f"UPDATE customer SET bal = bal - {amt} WHERE user_id = '{userId}'")
    cur.execute(f"SELECT max(t_id) FROM transact")
    cmd = cur.fetchone()
    newTransacId = cmd[0] + 1 if cmd[0] is not None else 1

    curr_date = t.strftime('%Y-%m-%d')
    curr_time = t.strftime('%H:%M:%S')

    cur.execute(f"INSERT INTO transact VALUES({newTransacId}, {userId}, '{curr_date}', '{curr_time}', null, {amt}, {userId})")

    con.commit() 
    t.sleep(0.5)
    print(f"Amount of ₹{amt} has been withdrawn from your account.\n")

def makePayment(userId, amt, recipientId):
    cur.execute(f"SELECT count(user_id) FROM customer WHERE user_id = '{recipientId}'")
    res = cur.fetchone()
    if res[0] == 0:
        t.sleep(0.5)
        print("Transaction failed, User ",userId,"not found...\n")
        return None
    else:
        bal = checkBalance(userId)
        if amt > bal: 
            t.sleep(0.5)
            print("Insufficient funds.\n")
            return None
        cur.execute(f"UPDATE customer SET bal = bal - {amt} WHERE user_id = '{userId}'")
        cur.execute(f"UPDATE customer SET bal = bal + {amt} WHERE user_id = '{recipientId}'")
        cur.execute(f"SELECT max(t_id) FROM transact")
        cmd = cur.fetchone()
        newTransacId = cmd[0] + 1 if cmd[0] is not None else 1

        curr_date = t.strftime('%Y-%m-%d')
        curr_time = t.strftime('%H:%M:%S')

        cur.execute(f"INSERT INTO transact VALUES({newTransacId}, {userId}, '{curr_date}', '{curr_time}', null, {amt}, '{recipientId}')")
        newTransacId += 1
        cur.execute(f"INSERT INTO transact VALUES({newTransacId}, {recipientId}, '{curr_date}', '{curr_time}', {amt},null, '{userId}')")
        
        con.commit() 
        t.sleep(0.5)
        print(f"Amount of ₹{amt} has been successfully transferred to {getName(recipientId)}\n")

def viewStatement(userId, startDate='0001-01-01', endDate=t.strftime('%Y-%m-%d')):
    try:
        dt.datetime.strptime(startDate, "%Y-%m-%d")
        dt.datetime.strptime(endDate, "%Y-%m-%d")
    except ValueError:
        t.sleep(0.5)
        print("Improper date formatting, try again.\n")
        return None
    
    cur.execute(f"SELECT * FROM transact WHERE user_id={userId} and tdate BETWEEN '{startDate}' and '{endDate}'")
    statements = cur.fetchall()
    if not statements: 
        t.sleep(0.5)
        print("No transaction has taken place under this account.\n")
        return None
    
    print("="*75)
    print("| Transac ID |    Date    |   Time   | Credit | Debit | Payee/Recipient |")
    print("-"*75)
    for (t_id,_,date,time,credit,debit,payee_recipient) in statements:
        credit = credit if credit else "    "
        debit = debit if debit else "    "

        print(f"|     {t_id}     | {date} | {time}  |  {credit}  |  {debit} |    {getName(payee_recipient)}     |")
    
    cur.execute(f"SELECT SUM(COALESCE(credit, 0)) FROM transact WHERE user_id = {userId} and tdate BETWEEN '{startDate}' and '{endDate}'")
    totalCredit = cur.fetchone()

    cur.execute(f"SELECT SUM(COALESCE(debit, 0)) FROM transact WHERE user_id = {userId} and tdate BETWEEN '{startDate}' and '{endDate}'")
    totalDebit = cur.fetchone()

    netTransAmt = totalCredit[0] - totalDebit[0]
    print(f"|\t\t\t\t\t\tNet Transaction amount: {netTransAmt} |")
    print("="*75)



print("="*30)
t.sleep(0.5)
print("Wecome user to the Chettinad Bank!")
print("="*30)
t.sleep(0.5)
print("Please login to use our services.")
while True:
    t.sleep(0.5)
    userId = input("Enter user id:")
    password = input("Enter password:")
    t.sleep(0.5)
    print("Authorizing...Please Wait...")
    t.sleep(3.0)
    if auth(userId, password) == "error":
        print("Error! The user_id or passcode provided is incorrect")
        q = input("Do you want to try again? (Y/N)")
        t.sleep(0.5)
        if q not in 'Yy':
            t.sleep(0.5)
            print('Thank you !!') 
            break
    else:
        print("\nYou've successfully logged in!")
        print(f"Welcome {getName(userId)}!\n")
        print("~"*50)
        t.sleep(1.0)
        print("List of services: \n")
        for i in ['1. Withdraw cash','2. Deposit Cash','3. Check Balance','4. View Statement','5. Fund Transfer','6. Log out','7. Exit']:
            t.sleep(0.5)
            print(i)
        print("~"*50)
        while True:
            try: choice = int(input("Enter the number to select service (enter 8 to view menu):"))
            except ValueError: 
                print("Invalid input, try again.\n")
                continue
            match choice:
                case 1:
                    try: amt = int(input("Enter Withdrawal Amount: ₹"))
                    except ValueError: 
                        print("Invalid input, try again.\n")
                        continue
                    t.sleep(0.5)
                    withdraw(userId, amt)
                case 2:
                    try: amt = int(input("Enter Deposition Amount: ₹"))
                    except ValueError: 
                        print("Invalid input, try again...\n")
                        continue
                    t.sleep(0.5)
                    deposit(userId, amt)
                case 3:
                    t.sleep(0.5)
                    print(f"Your current balance is ₹{checkBalance(userId)} /-\n")
                case 4:
                    t.sleep(0.5)
                    startdate = input("Enter the start date (yyyy-mm-dd) [press enter to skip]: ")
                    enddate = input("Enter end date (yyyy-mm-dd) [press enter to skip]: ")
                    t.sleep(0.5)
                    if startdate == "" and enddate == "":
                        viewStatement(userId)
                    elif startdate == "":
                        viewStatement(userId, endDate=enddate)
                    elif enddate == "":
                        viewStatement(userId, startDate=startdate)
                    else:
                        viewStatement(userId, startdate, enddate)

                case 5:
                    t.sleep(0.5)
                    try:
                        amt = int(input("Enter the amount to be transferred: "))
                        recipient = int(input("Enter the recipient's id: "))
                    except ValueError:
                        print("Invalid input, try again.\n")
                        continue
                    t.sleep(0.5)
                    makePayment(userId, amt, recipient)
                case 6:
                    t.sleep(0.5)
                    print("You've successfully logged out!")
                    break
                case 7:
                    print("Exiting.....")
                    t.sleep(3.0)
                    break
                case 8:
                    print("~"*50)
                    for i in ['1. Withdraw cash','2. Deposit Cash','3. Check Balance','4. View Statement','5. Fund Transfer','6. Log out','7. Exit']:
                        t.sleep(0.5)
                        print(i)            
                    print("~"*50)
                case _:
                    t.sleep(0.5)
                    print("Invalid choice selected...Try again\n")

        if choice == 7:
            print("Exiting.....")
            t.sleep(3.0)
            break