import random
import string
import sys
import select
import des_encryption

def main():
    print("Welcome to VaultLock. Please enter your password.")
    password = input("Password: ")
    if password == "vault123":
        print("Access granted.")
    else:
        print("Access denied.")
        exit()

    def timed_input(prompt, timeout=10):
        print(prompt, end='', flush=True)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().strip()
        else:
            print("\nIdle timeout. Exiting.")
            exit()

    while True:
        print("What would you like to do? \nTo generate a new password, type 1. \nTo view an existing login, type 2.\nTo create a new login, type 3.")
        choice = timed_input("Choice: ")

        if choice == "1":
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
            if include_numbers and include_special:
                print("Generating a password with numbers and special characters...")
                characters = string.ascii_letters + string.digits + string.punctuation
            elif include_numbers:
                print("Generating a password with numbers...")
                characters = string.ascii_letters + string.digits
            elif include_special:
                print("Generating a password with special characters...")
                characters = string.ascii_letters + string.punctuation
            else:
                print("Generating a password without numbers or special characters...")
                characters = string.ascii_letters
            password = ''.join(random.choice(characters) for _ in range(length))
            print("Generated password:", password, "\n")

        elif choice == "2":
            print("Viewing existing logins...")
            login_name = timed_input("Enter login name: ").lower()
            try:
                with open("dataFile.txt", "r") as f:
                    # Search for login_name in dataFile.txt
                    for line in f:
                        # Parse line to extract stored login name and encrypted password
                        # Format assumed: login_name,encrypted_password
                        stored_login_name, encrypted_password = line.strip().split(',', 1)
                        if stored_login_name == login_name:
                            # Import and use des_encryption.py to decrypt password with initial password as key
                            # from des_encryption import decrypt
                            # decrypted_password = decrypt(encrypted_password, password)
                            # Display decrypted password to user
                            print("Decrypted password for login", login_name, "is:", encrypted_password)
            except FileNotFoundError:
                print("Data file not found.")

        elif choice == "3":
            print("Creating a new login...")
            new_login = timed_input("Enter new login name: ")
            new_password = timed_input("Enter password: ")
            try:
                # Check if encrypt_password exists in des_encryption
                if hasattr(des_encryption, "encrypt_password"):
                    encrypted_password = des_encryption.encrypt_password(new_password, password)
                    with open("dataFile.txt", "a") as f:
                        f.write(f"{new_login.lower()},{encrypted_password}\n")
                else:
                    print("Error: encrypt_password function not found in des_encryption module.")
            except Exception as e:
                print(f"Error saving login: {e}")

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
import random
import string
import sys
import select
import des_encryption

def main():
    print("Welcome to VaultLock. Please enter your password.")
    password = input("Password: ")
    if password == "ABCDEF0123456789":
        print("Access granted.")
    else:
        print("Access denied.")
        exit()

    def timed_input(prompt, timeout=10000):
        print(prompt, end='', flush=True)
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.readline().strip()
        else:
            print("\nIdle timeout. Exiting.")
            exit()

    while True:
        print("\nWhat would you like to do? \nTo generate a new password, type 1. \nTo view an existing login, type 2.\nTo create a new login, type 3.")
        choice = timed_input("Choice: ")

        if choice == "1":
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
            if include_numbers and include_special:
                print("Generating a password with numbers and special characters...")
                characters = string.ascii_letters + string.digits + string.punctuation
            elif include_numbers:
                print("Generating a password with numbers...")
                characters = string.ascii_letters + string.digits
            elif include_special:
                print("Generating a password with special characters...")
                characters = string.ascii_letters + string.punctuation
            else:
                print("Generating a password without numbers or special characters...")
                characters = string.ascii_letters
            password = ''.join(random.choice(characters) for _ in range(length))
            print("Generated password:", password)

        elif choice == "2":
            print("Viewing existing logins...")
            login_name = timed_input("Enter login name: ").lower()
            try:
                found = False
                with open("dataFile.txt", "r") as f:
                    for line in f:
                        stored_login_name, encrypted_password = line.strip().split(',', 1)
                        if stored_login_name == login_name:
                            decrypted_password = des_encryption.decrypt_password(encrypted_password, password)
                            print("Decrypted password for login", login_name, "is:", decrypted_password)
                            found = True
                            break
                if not found:
                    print("Login not found.")
            except FileNotFoundError:
                print("Data file not found.")

        elif choice == "3":
            print("Creating a new login...")
            new_login = timed_input("Enter new login name: ")
            new_password = timed_input("Enter password: ")
            try:
                if hasattr(des_encryption, "encrypt_password"):
                    encrypted_password = des_encryption.encrypt_password(new_password, password)
                    print("Encrypted password:", encrypted_password)
                    with open("dataFile.txt", "a") as f:
                        f.write(f"{new_login.lower()},{encrypted_password}\n")
                    print("Login saved successfully.")
                else:
                    print("Error: encrypt_password function not found in des_encryption module.")
            except Exception as e:
                print(f"Error saving login: {e}")

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()