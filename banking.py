import mysql.connector as m, time as t, credentials as c, datetime as dt

con = m.connect(host='localhost', user='user', password='root', charset='utf8', database='bank')
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
    print(f"Amount of ₹{amt} has been deposited into your account.")


def withdraw(userId, amt):
    bal = checkBalance(userId)
    if amt > bal: 
        print("Insufficient funds.")
        return None
    cur.execute(f"UPDATE customer SET bal = bal - {amt} WHERE user_id = '{userId}'")
    cur.execute(f"SELECT max(t_id) FROM transact")
    cmd = cur.fetchone()
    newTransacId = cmd[0] + 1 if cmd[0] is not None else 1

    curr_date = t.strftime('%Y-%m-%d')
    curr_time = t.strftime('%H:%M:%S')

    cur.execute(f"INSERT INTO transact VALUES({newTransacId}, {userId}, '{curr_date}', '{curr_time}', null, {amt}, {userId})")

    con.commit() 
    print(f"Amount of ₹{amt} has been withdrawn from your account.")

def makePayment(userId, amt, recipientId):
    cur.execute(f"SELECT count(user_id) FROM customer WHERE user_id = '{recipientId}'")
    res = cur.fetchone()
    if res[0] == 0:
        print("Transaction failed, no user exists by that id.")
        return None
    else:
        bal = checkBalance(userId)
        if amt > bal: 
            print("Insufficient funds.")
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
        print(f"Amount of ₹{amt} has been successfully transferred to {getName(recipientId)}")

def viewStatement(userId, startDate='0000-01-01', endDate=t.strftime('%Y-%m-%d')):
    try:
        dt.datetime.strptime(startDate, "%Y-%m-%d")
        dt.datetime.strptime(endDate, "%Y-%m-%d")
    except ValueError:
        print("Improper date formatting, try again.")
        return None
    
    cur.execute(f"SELECT * FROM transact WHERE user_id={userId} and tdate BETWEEN '{startDate}' and '{endDate}'")
    statements = cur.fetchall()
    if not statements: 
        print("No transaction has taken place under this account.")
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
print("Wecome user to the Chettinad Bank!")
print("="*30)
print("Please login to use our services.")
while True:
    userId = input("Enter user id:")
    password = input("Enter password:")
    if auth(userId, password) == "error":
        print("Error! The user_id or passcode provided is incorrect")
        q = input("Do you want to try again? [press n to exit] (y/n)")
        if q != 'y': break
    else:
        print("You've successfully logged in!")
        print(f"Welcome {getName(userId)}!")
        print("~"*10)
        print("List of services: \n1. Withdraw cash \n2. Deposit Cash \n3. Check Balance \n4. View Statement \n5. Fund Transfer (recipient must belong to the same bank)\n6. Log out\n7. Exit")
        print("~"*10)
        while True:
            try: choice = int(input("Choose the number to select service (press 8 to view menu):"))
            except ValueError: 
                print("Invalid input, try again.")
                continue
            match choice:
                case 1:
                    try: amt = int(input("Enter the amount to be withdrawn: "))
                    except ValueError: 
                        print("Invalid input, try again.")
                        continue
                    withdraw(userId, amt)
                case 2:
                    try: amt = int(input("Enter the amount to be deposited: "))
                    except ValueError: 
                        print("Invalid input, try again.")
                        continue
                    deposit(userId, amt)
                case 3:
                    print(f"Your current balance is ₹{checkBalance(userId)} only")
                case 4:
                    startdate = input("Enter the start date (yyyy-mm-dd) [optional, enter to skip]: ")
                    enddate = input("Enter end date (yyyy-mm-dd) [optional, enter to skip]: ")
                    if startdate == "" and enddate == "":
                        viewStatement(userId)
                    elif startdate == "":
                        viewStatement(userId, endDate=enddate)
                    elif enddate == "":
                        viewStatement(userId, startDate=startdate)
                    else:
                        viewStatement(userId, startdate, enddate)

                case 5:
                    try:
                        amt = int(input("Enter the amount to be transferred: "))
                        recipient = int(input("Enter the recipient's id: "))
                    except ValueError:
                        print("Invalid input, try again.")
                        continue
                    makePayment(userId, amt, recipient)
                case 6:
                    print("You've successfully logged out!")
                    break
                case 7:
                    break
                case 8:
                    print("~"*10)
                    print("List of services: \n1. Withdraw cash \n2. Deposit Cash \n3. Check Balance \n4. View Statement \n5. Fund Transfer (recipient must belong to the same bank)\n6. Log out\n7. Exit")
                    print("~"*10)
                case _:
                    print("Invalid choice selected...Try again")

        if choice == 7: break