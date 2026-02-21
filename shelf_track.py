"""
shelf_track.py
~ A Bookstore Inventory Management System using SQLite.
Features:
~ Add books
~ Update books (including author details)
~ Delete books
~ Search books
~ View all books with author details
"""

import sqlite3

DATABASE_NAME = "ebookstore.db"

#=================================================================================
#                              DATABASE UTILITIES
#=================================================================================

DB_NAME = "ebookstore.db"

def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DB_NAME)

def create_tables():
    """Create book and author tables if they do not exit."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Author table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS author (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            country TEXT NOT NULL
        )
        """)

        # Book table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            authorID INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            FOREIGN KEY (authorID) REFERENCES author(id)
        )
        """)

        conn.commit()

def populate_tables():
    """Insert default data if tables are empty."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM author")
        if cursor.fetchone()[0] == 0:
            authors = [
                (1290, "Charles Dickens", "England"),
                (8937, "J.K. Rowling", "England"),
                (2356, "C.S. Lewis", "Ireland"),
                (6380, "J.R.R. Tolkien", "South Africa"),
                (5620, "Lewis Carroll", "England")
            ]
            cursor.executemany("INSERT INTO author VALUES (?, ?, ?)", authors)

        cursor.execute("SELECT COUNT(*) FROM book")
        if cursor.fetchone()[0] == 0:
            books = [
                (3001, "A Tale of Two Cities", 1290, 30),
                (3002, "Harry Potter and the Pjilosopher's Stone", 8937, 40),
                (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
                (3004, "The Lord of the Rings", 6380, 37),
                (3005, "Alice's Adventures in Wonderland", 5620, 12)
            ]
            cursor.executemany("INSERT INTO book VALUES (?, ?, ?, ?)", books)

        conn.commit()

#=================================================================================
#                             VALIDATION FUNCTIONS
#=================================================================================

def validate_id(value):
    """Validate that ID is a 4-digit integer."""
    if not value.isdigit() or len(value) != 4:
        raise ValueError("ID must be a 4-digit number.")
    return int(value)

def validate_quantity(value):
    """Validate quantity is positive integer."""
    if not value.isdigit():
        raise ValueError("Quantity must be a number.")
    return int(value)

#=================================================================================
#                             CRUD OPERATIONS
#=================================================================================

def add_book():
    try:
        book_id = validate_id(input("Enter Book ID (4 digits): "))
        title = input("Enter Book Title: ")
        author_id = validate_id(input("Enter Author ID (4 digits): "))
        qty = validate_quantity(input("Enter Quantity: "))

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO book VALUES (?, ?, ?, ?)",
                (book_id, title, author_id, qty)
            )
            conn.commit()

        print("Book added successfully.")

    except Exception as e:
        print(f"Error: {e}")

def update_book():
    try:
        book_id = validate_id(input("Enter Book ID to update: "))   

        with get_connection() as conn:
            cursor = conn.cursor()

            # Show current details with INNER JOIN
            cursor.execute("""
            SELECT book.title, author.name, author.country, book.qty
            FROM book
            INNER JOIN author ON book.authorID = author.id
            WHERE book.id = ?
            """, (book_id,)) 

            result = cursor.fetchone()

            if not result:
                print("Book not found.")
                return

            title, author_name, country, qty = result

            print("\nCurrent Details:") 
            print(f"Title: {title}") 
            print(f"Author: {author_name}") 
            print(f"Country: {country}") 
            print(f"Quantity: {qty}") 

            print("\n1. Update Quantity") 
            print("2. Update Author Details") 

            choice = input("Select option: ")

            if choice == "1":
                new_qty = validate_quantity(input("Enter new quantity: "))
                cursor.execute(
                    "UPDATE book SET qty = ? WHERE id = ?",
                    (new_qty, book_id)
                )

            elif choice == "2":
                new_name = input("Enter new author name: ")
                new_country = input("Enter new country: ")

                cursor.execute("""
                UPDATE author
                SET name = ?, country = ?
                WHERE id = (
                    SELECT authorID FROM book WHERE id = ?
                )
                """, (new_name, new_country, book_id))

            conn.commit()
            print("Update successful.")

    except Exception as e:
        print(f"Error: {e}")

def delete_book():
    try:
        book_id = validate_id(input("Enter Book ID to delete: "))

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bokk WHERE id = ?", (book_id))
            conn.commit()

        print("Book deleted successfully.")

    except Exception as e:
        print(f"Error: {e}")

def search_book():
    try:
        title = input("Enter title keyword: ")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT book_id, book.title, author.name
            FROM book
            INNE JOIN author ON book.authorID = author.id
            WHERE book.title LIKE ?
            """, (f"%(title)%",))

            results = cursor.fetchall()

            if results:
                for book in results:
                    print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]}")
            else:
                print("No books found.")

    except Exception as e:
        print(f"Error: {e}")

def view_all_books():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT book.title, author.name, author.country
            FROM book
            INNER JOIN author ON book.authorID = author.id
            """)

            result = cursor.fetchall()

            print("\nBook Details:\n")
            for title, name, country in result:
                print(f"Title: {title}")
                print(f"Author's Name: {name}")
                print(f"Author's Country: {country}")
                print()

    except Exception as e:
        print(f"Error: {e}")

#=================================================================================
#                                  MAIN MENU
#=================================================================================

def menu():
    while True:
        print("\n--- Ebookstore Menu ---")
        print("1. Enter book")
        print("2. Update book")
        print("3. Delete book")
        print("4. Search books")
        print("5. View details of all books")
        print("0. Exit")

        choice = input("Select option: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            update_book()
        elif choice == "3":
            delete_book()
        elif choice == "4":
            search_book()
        elif choice == "5":
            view_all_books()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("invalid option. Please try again.")

#=================================================================================
#                              PROGRAM ENTRY POINT
#=================================================================================

if __name__ == "__main__":
    create_tables()
    populate_tables()
    menu()