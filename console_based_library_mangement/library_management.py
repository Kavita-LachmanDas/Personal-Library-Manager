import sqlite3
import os
import datetime
from tabulate import tabulate
import time
import json


class LibraryManager:
    def __init__(self, db_name="data.db"):
        """Initialize the library manager with a SQLite database"""
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect_db()
        self.setup_db()

    def connect_db(self):
        """Connect to the SQLite database"""
        try:
            
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_name}")
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            exit(1)

    def setup_db(self):
        """Create books table if it doesn't exist"""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publication_year INTEGER,
            genre TEXT,
            read_status BOOLEAN,
            added_date TEXT
        )
        '''
        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Database setup error: {e}")

    def add_book(self, title, author, publication_year, genre, read_status):
        """Add a new book to the library"""
        try:
            added_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            query = '''
            INSERT INTO books (title, author, publication_year, genre, read_status, added_date)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            self.cursor.execute(query, (title, author, publication_year, genre, read_status, added_date))
            self.conn.commit()
            
            print("\n✅ Book added successfully!")
            time.sleep(1)
            return True
        except sqlite3.Error as e:
            print(f"Error adding book: {e}")
            return False

    def view_all_books(self):
        """Display all books in the library"""
        try:
            self.cursor.execute("SELECT * FROM books ORDER BY title")
            books = self.cursor.fetchall()
            
            if not books:
                print("\n📚 Your library is empty. Add some books to get started!")
                return
            
            # Prepare data for tabulate
            headers = ["ID", "Title", "Author", "Year", "Genre", "Status", "Date Added"]
            table_data = []
            
            for book in books:
                # Format the read status
                read_status = "Read ✓" if book[5] else "Unread ✗"
                
                # Add formatted row to table data
                table_data.append([
                    book[0],                  # ID
                    book[1],                  # Title
                    book[2],                  # Author
                    book[3],                  # Publication Year
                    book[4],                  # Genre
                    read_status,              # Read Status
                    book[6]                   # Added Date
                ])
            
            # Display table
            print("\n📚 Your Library:")
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            
        except sqlite3.Error as e:
            print(f"Error viewing books: {e}")

    def remove_book(self, book_id):
        """Remove a book from the library by ID"""
        try:
            # Check if book exists
            self.cursor.execute("SELECT title FROM books WHERE id = ?", (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print(f"\n❌ No book found with ID {book_id}")
                return False
            
            # Delete the book
            self.cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            self.conn.commit()
            
            print(f"\n✅ Book '{book[0]}' removed successfully!")
            time.sleep(1)
            return True
            
        except sqlite3.Error as e:
            print(f"Error removing book: {e}")
            return False

    def update_read_status(self, book_id):
        """Toggle the read status of a book"""
        try:
            # Check if book exists and get current status
            self.cursor.execute("SELECT title, read_status FROM books WHERE id = ?", (book_id,))
            book = self.cursor.fetchone()
            
            if not book:
                print(f"\n❌ No book found with ID {book_id}")
                return False
            
            # Toggle status
            new_status = not book[1]
            status_text = "Read ✓" if new_status else "Unread ✗"
            
            # Update the book
            self.cursor.execute("UPDATE books SET read_status = ? WHERE id = ?", (new_status, book_id))
            self.conn.commit()
            
            print(f"\n✅ Status of '{book[0]}' updated to {status_text}")
            time.sleep(1)
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating book status: {e}")
            return False

    def search_books(self, search_term, search_by):
        """Search for books by title, author, or genre"""
        try:
            query = f"SELECT * FROM books WHERE {search_by} LIKE ? ORDER BY title"
            self.cursor.execute(query, (f"%{search_term}%",))
            books = self.cursor.fetchall()
            
            if not books:
                print(f"\n🔍 No books found matching '{search_term}' in {search_by}")
                return
            
            # Prepare data for tabulate
            headers = ["ID", "Title", "Author", "Year", "Genre", "Status", "Date Added"]
            table_data = []
            
            for book in books:
                # Format the read status
                read_status = "Read ✓" if book[5] else "Unread ✗"
                
                # Add formatted row to table data
                table_data.append([
                    book[0],                  # ID
                    book[1],                  # Title
                    book[2],                  # Author
                    book[3],                  # Publication Year
                    book[4],                  # Genre
                    read_status,              # Read Status
                    book[6]                   # Added Date
                ])
            
            # Display table
            print(f"\n🔍 Search Results for '{search_term}' in {search_by}:")
            print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
            
        except sqlite3.Error as e:
            print(f"Error searching books: {e}")

    def get_statistics(self):
        """Calculate and display library statistics"""
        try:
            # Total books
            self.cursor.execute("SELECT COUNT(*) FROM books")
            total_books = self.cursor.fetchone()[0]
            
            if total_books == 0:
                print("\n📊 Your library is empty. Add some books to see statistics!")
                return
            
            # Read books
            self.cursor.execute("SELECT COUNT(*) FROM books WHERE read_status = 1")
            read_books = self.cursor.fetchone()[0]
            
            # Calculate percentage
            percent_read = (read_books / total_books * 100) if total_books > 0 else 0
            
            # Get genre counts
            self.cursor.execute("SELECT genre, COUNT(*) as count FROM books GROUP BY genre ORDER BY count DESC")
            genres = self.cursor.fetchall()
            
            # Get author counts
            self.cursor.execute("SELECT author, COUNT(*) as count FROM books GROUP BY author ORDER BY count DESC")
            authors = self.cursor.fetchall()
            
            # Get decade counts
            self.cursor.execute("SELECT (publication_year / 10) * 10 as decade, COUNT(*) FROM books GROUP BY decade ORDER BY decade")
            decades = self.cursor.fetchall()
            
            # Display summary statistics
            print("\n📊 Library Statistics:")
            print(f"Total Books: {total_books}")
            print(f"Books Read: {read_books}")
            print(f"Percentage Read: {percent_read:.1f}%")
            
            # Display top genres
            if genres:
                print("\nTop Genres:")
                for genre, count in genres[:5]:
                    print(f"  {genre}: {count} book{'s' if count > 1 else ''}")
            
            # Display top authors
            if authors:
                print("\nTop Authors:")
                for author, count in authors[:5]:
                    print(f"  {author}: {count} book{'s' if count > 1 else ''}")
            
            # Display books by decade
            if decades:
                print("\nBooks by Decade:")
                for decade, count in decades:
                    if decade is not None:  # Skip None values
                        print(f"  {decade}s: {count} book{'s' if count > 1 else ''}")
                
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")

    def export_library(self, filename="library_export.json"):
        """Export the library to a JSON file"""
        try:
            self.cursor.execute("SELECT * FROM books")
            books = self.cursor.fetchall()
            
            if not books:
                print("\n❌ Your library is empty. Nothing to export!")
                return False
            
            book_list = []
            for book in books:
                book_dict = {
                    "id": book[0],
                    "title": book[1],
                    "author": book[2],
                    "publication_year": book[3],
                    "genre": book[4],
                    "read_status": bool(book[5]),
                    "added_date": book[6]
                }
                book_list.append(book_dict)
            
            with open(filename, 'w') as file:
                json.dump(book_list, file, indent=4)
            
            print(f"\n✅ Library exported successfully to {filename}")
            return True
            
        except Exception as e:
            print(f"Error exporting library: {e}")
            return False

    def import_library(self, filename="library_export.json"):
        """Import library from a JSON file"""
        try:
            if not os.path.exists(filename):
                print(f"\n❌ File {filename} not found!")
                return False
            
            with open(filename, 'r') as file:
                books = json.load(file)
            
            if not books:
                print("\n❌ No books found in the import file!")
                return False
            
            # Confirm import
            count = len(books)
            confirm = input(f"\nImporting {count} books will replace your current library. Continue? (y/n): ")
            
            if confirm.lower() != 'y':
                print("Import cancelled.")
                return False
            
            # Clear current library
            self.cursor.execute("DELETE FROM books")
            
            # Import books
            for book in books:
                query = '''
                INSERT INTO books (title, author, publication_year, genre, read_status, added_date)
                VALUES (?, ?, ?, ?, ?, ?)
                '''
                self.cursor.execute(query, (
                    book['title'],
                    book['author'],
                    book['publication_year'],
                    book['genre'],
                    book['read_status'],
                    book['added_date']
                ))
            
            self.conn.commit()
            print(f"\n✅ Successfully imported {count} books!")
            return True
            
        except Exception as e:
            print(f"Error importing library: {e}")
            return False

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
           


def display_menu():
    """Display the main menu options"""
    print("\n" + "=" * 50)
    print("📚 PERSONAL LIBRARY MANAGER 📚".center(50))
    print("=" * 50)
    print("1. View Library")
    print("2. Add New Book")
    print("3. Remove Book")
    print("4. Update Read Status")
    print("5. Search Books")
    print("6. View Statistics")
    print("9. Exit")
    print("=" * 50)
    return input("Select an option (1-9): ")


def get_genre_selection():
    """Display a menu for genre selection"""
    genres = [
        "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", 
        "Mystery", "AI", "Codding", "Biography", 
        "History", "Self-Help", "Poetry", "Science", 
        "Philosophy", "Religion", "Art", "Other"
    ]
    
    print("\nSelect a genre:")
    for i, genre in enumerate(genres, 1):
        print(f"{i}. {genre}")
    
    while True:
        try:
            choice = int(input("\nEnter genre number (1-16): "))
            if 1 <= choice <= len(genres):
                return genres[choice-1]
            else:
                print("Invalid choice. Please enter a number between 1 and 16.")
        except ValueError:
            print("Please enter a valid number.")


def main():
    """Main function to run the library manager"""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Initialize library manager
    library = LibraryManager()
    
    while True:
        # Display menu and get choice
        choice = display_menu()
        
        if choice == '1':
            # View Library
            os.system('cls' if os.name == 'nt' else 'clear')
            library.view_all_books()
            input("\nPress Enter to continue...")
            
        elif choice == '2':
            # Add New Book
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n📝 ADD NEW BOOK")
            print("-" * 50)
            
            title = input("Enter book title: ")
            if not title:
                print("Title cannot be empty. Operation cancelled.")
                continue
                
            author = input("Enter author name: ")
            if not author:
                print("Author cannot be empty. Operation cancelled.")
                continue
            
            # Get publication year
            while True:
                try:
                    year_input = input("Enter publication year (or press Enter for current year): ")
                    if not year_input:
                        publication_year = datetime.datetime.now().year
                    else:
                        publication_year = int(year_input)
                        if publication_year < 1000 or publication_year > datetime.datetime.now().year:
                            print(f"Please enter a year between 1000 and {datetime.datetime.now().year}.")
                            continue
                    break
                except ValueError:
                    print("Please enter a valid year.")
            
            # Get genre
            genre = get_genre_selection()
            
            # Get read status
            while True:
                read_input = input("Have you read this book? (y/n): ")
                if read_input.lower() in ['y', 'n']:
                    read_status = read_input.lower() == 'y'
                    break
                else:
                    print("Please enter 'y' or 'n'.")
            
            # Add the book
            library.add_book(title, author, publication_year, genre, read_status)
            
        elif choice == '3':
            # Remove Book
            os.system('cls' if os.name == 'nt' else 'clear')
            library.view_all_books()
            
            try:
                book_id = int(input("\nEnter the ID of the book to remove (or 0 to cancel): "))
                if book_id == 0:
                    print("Operation cancelled.")
                    continue
                library.remove_book(book_id)
            except ValueError:
                print("Please enter a valid book ID.")
            
        elif choice == '4':
            # Update Read Status
            os.system('cls' if os.name == 'nt' else 'clear')
            library.view_all_books()
            
            try:
                book_id = int(input("\nEnter the ID of the book to update status (or 0 to cancel): "))
                if book_id == 0:
                    print("Operation cancelled.")
                    continue
                library.update_read_status(book_id)
            except ValueError:
                print("Please enter a valid book ID.")
            
        elif choice == '5':
            # Search Books
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n🔍 SEARCH BOOKS")
            print("-" * 50)
            
            print("Search by:")
            print("1. Title")
            print("2. Author")
            print("3. Genre")
            
            search_option = input("Select an option (1-3): ")
            
            if search_option == '1':
                search_by = "title"
            elif search_option == '2':
                search_by = "author"
            elif search_option == '3':
                search_by = "genre"
            else:
                print("Invalid option. Returning to main menu.")
                continue
            
            search_term = input(f"\nEnter {search_by} to search: ")
            if not search_term:
                print("Search term cannot be empty. Operation cancelled.")
                continue
                
            library.search_books(search_term, search_by)
            input("\nPress Enter to continue...")
            
        elif choice == '6':
            # View Statistics
            os.system('cls' if os.name == 'nt' else 'clear')
            library.get_statistics()
            input("\nPress Enter to continue...")
            
      
        elif choice == '9':
            # Exit
            print("\nThank you for using Personal Library Manager!")
            library.close()
            break
            
        else:
            print("Invalid option. Please try again.")
        
        # Clear screen for next iteration
        os.system('cls' if os.name == 'nt' else 'clear')


if __name__ == "__main__":
    main()