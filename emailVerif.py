import smtplib
from json import loads
from random import randint
from time import time

class LateException(Exception):
    pass
class NoPendingVerificationException(Exception):
    pass
class InvalidCodeLength(Exception):
    pass
    

class EmailVerif:
    def __init__(self,ACCOUNT_ID:str, ACCOUNT_PASSWORD:str):
        self.__ACCOUNT_ID = ACCOUNT_ID
        self.__ACCOUNT_PASSWORD = ACCOUNT_PASSWORD
        self.__code_length = 6  #please dont be silly with this number

        self.__SMTP = smtplib.SMTP('smtp.gmail.com', 587)
        self.__SMTP.starttls()
        self.__verif_codes = {}  # where the key is the email and the value another dict with the code + timesent
        try:
            self.__SMTP.login(self.__ACCOUNT_ID, self.__ACCOUNT_PASSWORD)
        except smtplib.SMTPAuthenticationError:
            print("could not login with that information maybe due to 2FA or incorrect password")
            print("if this account has 2FA go on 'https://myaccount.google.com/apppasswords' to generate a password")
            print("this password will just have weak permissions and wont replace your actual password.")
            exit(0)
    
    def get_code_length(self):
        return self.__code_length
    
    def set_code_length(self,new_length:int):
        if new_length <= 0:
            raise InvalidCodeLength("invalid code length, must be at least 1")
        self.__code_length = new_length
    
    def send_verification(self,emails:list[str],timeLimit=120):
        if self.__code_length <= 0:
            raise InvalidCodeLength("invalid code length, must be at least 1")

        for dest_email in emails:
            Verification_Code = randint(10**(self.__code_length-1),(10**self.__code_length)-1)
            self.__verif_codes[dest_email] = {"Verification_Code":Verification_Code,"Time_Sent":time(),"Time_Limit":timeLimit}
            message = f'''
your verification code is: {Verification_Code}
'''
            self.__SMTP.sendmail(self.__ACCOUNT_ID, dest_email, message)
    
    def close(self):
        """call this function when ever your done with sending emails,\n
        you will need to log in again though"""
        self.__SMTP.quit()
    
    def enter_verif(self,email:str, Verification_code:int):
        try:
            verif_data = self.__verif_codes[email]
        except KeyError:
            raise NoPendingVerificationException(f"No verification code waiting for that email,{email}")
        
        if (float(verif_data["Time_Sent"])+float(verif_data["Time_Limit"])) < time():
            del self.__verif_codes[email]
            raise LateException(f"You are too late to enter a Verification Code as at least {verif_data['Time_Limit']} seconds has passed")

        return int(verif_data["Verification_Code"]) == int(Verification_code)


if __name__ == "__main__":
    with open("email_login_info.json","r") as f:
        data = loads(f.read())
        ACCOUNT_ID:str = data["ACCOUNT_ID"]
        ACCOUNT_PASSWORD:str = data["ACCOUNT_PASSWORD"]

    print("=== for sender ===")
    print("email address: ", ACCOUNT_ID)
    print("email password: yeah not showing that")
    print("\n"*2)

    li = [f"{ACCOUNT_ID}@gmail.com"]

    Email = EmailVerif(ACCOUNT_ID,ACCOUNT_PASSWORD)
    Email.send_verification(li,5)

    print("=== what the client should only see ===")
    print(f"whats the {Email.get_code_length()}-digit verification code")
    users_verif_code = input(">> ")
    try:
        correct_code = False
        correct_code = Email.enter_verif(ACCOUNT_ID+"@gmail.com",users_verif_code)
    except Exception as e:
        print("something went wrong with entering the verification code")
        print(e)

    if correct_code:
        print("YIPPIE YOUR ACCOUNT IS VERIFIED!")
    else:
        print("Invalid verification Code given")
    
    Email.close()