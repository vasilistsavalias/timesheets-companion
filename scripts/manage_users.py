import sys
import os
import argparse

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.manager import DatabaseManager
from src.services.auth_service import AuthService
from src.database.models import User

# Initialize DB Manager
manager = DatabaseManager()
manager.create_tables()

def get_db():
    return next(manager.get_db())

def list_users():
    db = get_db()
    users = db.query(User).all()
    print(f"\n{'ID':<5} {'Username':<20} {'Name':<20} {'Role':<10}")
    print("-" * 60)
    for u in users:
        role = "admin" if u.is_admin else "user"
        print(f"{u.id:<5} {u.username:<20} {u.name or '':<20} {role:<10}")
    print("-" * 60)

def add_user(username, password, name=None, is_admin=False):
    db = get_db()
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"Skipping: User '{username}' already exists.")
        return
    
    try:
        AuthService.create_user(db, username, password, name, is_admin)
        print(f"Success: Created '{username}' ({'Admin' if is_admin else 'User'})")
    except Exception as e:
        print(f"Error creating {username}: {e}")

def delete_user(username):
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        print(f"Deleted: {username}")
    else:
        print(f"Not Found: {username}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # List
    subparsers.add_parser("list")

    # Add
    add = subparsers.add_parser("add")
    add.add_argument("username")
    add.add_argument("password")
    add.add_argument("--name")
    add.add_argument("--admin", action="store_true")

    # Delete
    dele = subparsers.add_parser("delete")
    dele.add_argument("username")

    args = parser.parse_args()

    if args.command == "list":
        list_users()
    elif args.command == "add":
        add_user(args.username, args.password, args.name, args.admin)
    elif args.command == "delete":
        delete_user(args.username)
