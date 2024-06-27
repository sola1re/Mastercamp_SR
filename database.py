import sqlite3

"""
This file should be run once on its own to create the db.
Any following run will reset the database.
"""

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('server_database.db')
cursor = conn.cursor()

# Drop the tables if they exist
cursor.execute('DROP TABLE IF EXISTS messages')
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('DROP TABLE IF EXISTS channels')

# Create the users table
cursor.execute('''
CREATE TABLE users(
    ID_user INTEGER PRIMARY KEY,
    Pseudo TEXT NOT NULL UNIQUE,
    Password TEXT NOT NULL
)
''')

# Create the channels table
cursor.execute('''
CREATE TABLE channels(
    ID_channel INTEGER PRIMARY KEY,
    Name TEXT NOT NULL UNIQUE,
    Password TEXT NOT NULL
)
''')

# Create the messages table
cursor.execute('''
CREATE TABLE messages(
    ID_message INTEGER PRIMARY KEY,
    Content TEXT NOT NULL,
    Type BOOLEAN NOT NULL,
    ID_user INTEGER NOT NULL,
    ID_channel INTEGER NOT NULL,
    FOREIGN KEY(ID_user) REFERENCES users(ID_user),
    FOREIGN KEY(ID_channel) REFERENCES channels(ID_channel)
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
