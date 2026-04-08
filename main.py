import random
import string
import sys
import select
import des_encryption
import csv
import secrets
import pwinput
import hashlib
import os
import stat
import time
import termios
import tty

def timed_input(prompt, timeout=20):  # Enter timeout in seconds
    print(prompt, end='', flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip()
    else:
        print("\nIdle timeout. Exiting.")
        exit()

def timed_pwinput(prompt, timeout=20, mask='*'):
    print(prompt, end='', flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    password = ''
    start_time = time.time()
    try:
        tty.setraw(fd)  # Disable line buffering and echo
        while True:
            # Check for input with a short timeout
            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if ready:
                char = sys.stdin.read(1)
                if char in ('\n', '\r'):  # Enter key
                    break
                elif char == '\x7f':  # Backspace
                    if password:
                        password = password[:-1]
                        sys.stdout.write('\b \b')  # Erase last mask char
                        sys.stdout.flush()
                else:
                    password += char
                    sys.stdout.write(mask)  # Mask with specified char
                    sys.stdout.flush()
            # Check timeout
            if time.time() - start_time > timeout:
                print("\nIdle timeout. Exiting.")
                sys.exit()  # Or return None if you prefer not to exit
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore terminal
    print()  # New line after input
    return password

def checkMasterPassword(password):
    with open("masterPassword.txt", "rb") as f:
        data = f.read()
        salt = data[:16]
        stored_hash = data[16:]
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        if hashed == stored_hash:
            return True
        else:
            return False
            exit()

def setMasterPassword(oldPassword=None):
    if oldPassword is None:
        if os.path.exists("masterPassword.txt"):
            oldPassword = timed_pwinput("Enter current master password: ")
            if not checkMasterPassword(oldPassword):
                print("Current password incorrect.")
                return
    
    while True:
        password = timed_pwinput("Enter new master password: ")
        if len(password) == 16:
            try:
                int(password, 16)
                break
            except ValueError:
                print("Password must be exactly 16 hex characters. Please try again.")
        else:
            print("Password must be exactly 16 hex characters. Please try again.")
    
    # Decrypt existing passwords with old password and re-encrypt with new password
    logins = []
    if os.path.exists("dataFile.txt") and oldPassword:
        with open("dataFile.txt", "r") as f:
            reader = csv.reader(f)
            for row in reader:
                login_name, encrypted_password = row
                decrypted = des_encryption.decrypt_password(encrypted_password, oldPassword)
                logins.append((login_name, decrypted))
        with open("dataFile.txt", "w", newline='') as f:
            writer = csv.writer(f)
            for login_name, decrypted_password in logins:
                new_encrypted = des_encryption.encrypt_password(decrypted_password, password)
                writer.writerow([login_name, new_encrypted])
    
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    with open("masterPassword.txt", "wb") as f:
        f.write(salt + hashed)
    setValidPermissions("masterPassword.txt")
    print("Master password set successfully.")
    return password

def new_password():
    while True:
        print("Does your password need to include numbers? (y/n)")
        include_numbers = timed_input("Include numbers: ")
        include_numbers = include_numbers.lower() == "y"

        print("Does your password need to include special characters? (y/n)")
        include_special = timed_input("Include special characters: ")
        include_special = include_special.lower() == "y"

        print("How long does your password need to be? (Enter a number)")
        length_input = timed_input("Length: ")
        try:
            length = int(length_input)
        except ValueError:
            print("Invalid length. Please try again.")
            continue

        password = generate_password(length, include_numbers, include_special)
        print("Generated password:", password)
        break

def generate_password(length, include_numbers=False, include_special=False):
    characters = string.ascii_letters
    if include_numbers:
        characters += string.digits
    if include_special:
        characters += string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def existing_login(password):
    print("Viewing existing logins...")
    login_name = timed_input("Enter login name: ").lower()
    found = False
    with open("dataFile.txt", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            encrypted_login_name, encrypted_password = row
            try:
                decrypted_login_name = des_encryption.decrypt_password(encrypted_login_name, password)
                if decrypted_login_name.lower() == login_name:
                    decrypted_password = des_encryption.decrypt_password(encrypted_password, password)
                    print("Decrypted password for login", login_name, "is:", decrypted_password)
                    found = True
                    break
            except Exception as decrypt_error:
                print(f"Error decrypting: {decrypt_error}")
                continue
    if not found:
        print("Login not found.")

def new_login(password):
    print("Creating a new login...")
    new_login = timed_input("Enter new login name: ")
    new_password_input = timed_pwinput("Enter password: ", mask="*")
    try:
        encrypted_login_name = des_encryption.encrypt_password(new_login, password)
        encrypted_password = des_encryption.encrypt_password(new_password_input, password)
        print("Encrypted password:", encrypted_password)
        with open("dataFile.txt", "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([encrypted_login_name, encrypted_password])
        setValidPermissions("dataFile.txt")
        print("Login saved successfully.")
    except Exception as e:
        print(f"Error saving login: {e}")

def change_master_password():
    with open("masterPassword.txt", "rb") as f:
        data = f.read()
        salt = data[:16]
        stored_hash = data[16:]
        current = timed_pwinput("Enter current master password: ")
        hashed = hashlib.pbkdf2_hmac('sha256', current.encode(), salt, 100000)
        if hashed == stored_hash:
            return setMasterPassword(current)
        else:
            print("Current password incorrect.")
            return None

def setValidPermissions(path):
    if os.name != "posix":
        print("WARNING: file permissions checking on Windows not implemented")
        return

    if not os.path.exists(path):
        return
    if not os.path.isfile(path):
        print(f"ERROR: the path {path!r} exists but is not a file")
        return

    statinfo = os.stat(path)
    # check file ownership
    if statinfo.st_uid != os.getuid():
        print(f"ERROR: the file {path!r} is not owned by the current user; exiting")
        exit(1)
    # ensure file permissions are correct
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def main():
    # if the files already exist, make sure they are owned by the current user and have correct permissions
    setValidPermissions("masterPassword.txt")
    setValidPermissions("dataFile.txt")

    if not os.path.exists("masterPassword.txt"):
        print("Welcome to VaultLock. Set up your master password.")
        setMasterPassword()
    else:
        print("Welcome to VaultLock. Please enter your password.")
        password = timed_pwinput("Password: ")
        if not checkMasterPassword(password):
            print("Incorrect password. Exiting.")
            exit()
        else:
            print("Login successful.")

    while True:
        print("\nWhat would you like to do? \nTo generate a new password, type 1." \
        " \nTo view an existing login, type 2.\nTo create a new login, type 3.\nTo change master password, type 4.")
        choice = timed_input("Choice: ")
        if choice == "1":
            new_password()
        elif choice == "2":
            existing_login(password)
        elif choice == "3":
            new_login(password)
        elif choice == "4":
            newPasswordInput = change_master_password()
            if newPasswordInput:
                password = newPasswordInput
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
