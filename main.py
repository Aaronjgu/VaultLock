import random
import string
import sys
import select
import des_encryption
import csv

def timed_input(prompt, timeout=20):  # Enter timeout in seconds
    print(prompt, end='', flush=True)
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if ready:
        return sys.stdin.readline().strip()
    else:
        print("\nIdle timeout. Exiting.")
        exit()

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
    return ''.join(random.choice(characters) for _ in range(length))

def existing_login(password):
    print("Viewing existing logins...")
    login_name = timed_input("Enter login name: ").lower()
    found = False
    with open("dataFile.txt", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            stored_login_name, encrypted_password = row
            if stored_login_name.lower() == login_name:
                try:
                    decrypted_password = des_encryption.decrypt_password(encrypted_password, password)
                    print("Decrypted password for login", login_name, "is:", decrypted_password)
                    found = True
                    break
                except Exception as decrypt_error:
                    print(f"Error decrypting password: {decrypt_error}")
                    continue
    if not found:
        print("Login not found.")

def new_login(password):
    print("Creating a new login...")
    new_login = timed_input("Enter new login name: ")
    new_password_input = timed_input("Enter password: ")
    try:
        try:
            encrypted_password = des_encryption.encrypt_password(new_password_input, password)
            print("Encrypted password:", encrypted_password)
            with open("dataFile.txt", "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([new_login, encrypted_password])
            print("Login saved successfully.")
        except Exception as encrypt_error:
            print(f"Error encrypting password: {encrypt_error}")
    except Exception as e:
        print(f"Error saving login: {e}")

def main():
    print("Welcome to VaultLock. Please enter your password.")
    password = input("Password: ")
    if password == "ABCDEF0123456789":
        print("Access granted.")
    else:
        print("Access denied.")
        exit()

    while True:
        print("\nWhat would you like to do? \nTo generate a new password, type 1." \
        " \nTo view an existing login, type 2.\nTo create a new login, type 3.")
        choice = timed_input("Choice: ")
        if choice == "1":
            new_password()
        elif choice == "2":
            existing_login(password)
        elif choice == "3":
            new_login(password)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()