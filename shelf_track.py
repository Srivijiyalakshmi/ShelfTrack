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

DB_NAME = "ebookstore.db"

#=================================================================================
#                              DATABASE UTILITIES
#=================================================================================

def get_connection():
    """
    Create and return a database connection.
    Enables foreign key constraint enforcement.
    Returns:
        sqlite3.Connection: Active database connection.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    """Create author and book tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS author (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)

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
    """
    Insert default data into tables if they are empty.
    """
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
            cursor.executemany(
                "INSERT INTO author VALUES (?, ?, ?)",
                authors
            )

        cursor.execute("SELECT COUNT(*) FROM book")
        if cursor.fetchone()[0] == 0:
            books = [
                (3001, "A Tale of Two Cities", 1290, 30),
                (3002, "Harry Potter and the Philosopher's Stone", 8937, 40),
                (3003, "The Lion, the Witch and the Wardrobe", 2356, 25),
                (3004, "The Lord of the Rings", 6380, 37),
                (3005, "Alice's Adventures in Wonderland", 5620, 12)
            ]
            cursor.executemany(
                "INSERT INTO book VALUES (?, ?, ?, ?)",
                books
            )

        conn.commit()

#=================================================================================
#                             VALIDATION FUNCTIONS
#=================================================================================

def validate_id(value):
    """
    Validate that the provided ID is a 4-digit numeric string.
    
    Parameters:
        value (str): User input representing an ID.
        
    Returns:
        int: Converted intger ID.
        
    Raises:
        ValueError: If input is not a 4-digit number.
    """
    if not value.isdigit() or len(value) != 4:
        raise ValueError("ID must be a 4-digit number.")
    return int(value)

def validate_quantity(value):
    """
    Validate that the quantity is a positive integer.
    
    Parameters:
        value (str): User input representing quantity.
        
    Returns:
        int: Converted integer quantity.
        
    Raises:
        ValueError: If input is not numeric.
    """
    if not value.isdigit():
        raise ValueError("Quantity must be a number.")
    return int(value)

#=================================================================================
#                             CRUD OPERATIONS
#=================================================================================

def add_book():
    """
    Add a new book to the database.
    
    Validates:
    ~ Book ID format
    ~ Author ID format
    ~ Quantity format
    ~ Author existence in database
    """
    try:
        book_id = validate_id(input("Enter Book ID (4 digits): "))
        title = input("Enter Book Title: ")
        author_id = validate_id(input("Enter Author ID (4 digits): "))
        qty = validate_quantity(input("Enter Quantity: "))

        with get_connection() as conn:
            cursor = conn.cursor()

            # Check if author exists
            cursor.execute("SELECT id FROM author WHERE id = ?", (author_id,))
            if not cursor.fetchone():
                print("Author ID does not exist. Please add the author first.")
                return

            cursor.execute("""
                INSERT INTO book (id, title, authorID, qty)
                VALUES (?, ?, ?, ?)
            """, (book_id, title, author_id, qty))

            conn.commit()

        print("Book added successfully.")

    except Exception as e:
        print(f"Error: {e}")

def update_book():
    """
    Update book quantity or author details.
    """
    try:
        book_id = validate_id(input("Enter Book ID to update: "))   

        with get_connection() as conn:
            cursor = conn.cursor()

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
    """
    Delete a book from the database using its ID.
    """
    try:
        book_id = validate_id(input("Enter Book ID to delete: "))

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
            conn.commit()

        print("Book deleted successfully.")

    except Exception as e:
        print(f"Error: {e}")

def search_book():
    """
    Search for books by title keyword.
    """
    try:
        keyword = input("Enter title keyword: ")

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT book.id, book.title, author.name
                FROM book
                INNER JOIN author ON book.authorID = author.id
                WHERE book.title LIKE ?
            """, (f"%{keyword}%",))

            results = cursor.fetchall()

            if results:
                for book in results:
                    print(f"ID: {book[0]} | Title: {book[1]} | Author: {book[2]}")
            else:
                print("No books found.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")

def view_all_books():
    """
    Display all books with their author details.
    """
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
    """
    Display main menu and handle user interaction.
    """
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