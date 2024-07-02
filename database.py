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
cursor.execute('DROP TABLE IF EXISTS logs')
cursor.execute('DROP TABLE IF EXISTS authorized_users')

# Create the users table
cursor.execute('''
CREATE TABLE users(
ID_user INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT NOT NULL UNIQUE,
password TEXT NOT NULL
)
''')

# Create the channels table
cursor.execute('''
CREATE TABLE channels(
ID_channel INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL UNIQUE,
password TEXT NOT NULL
)
''')

# Create the messages table
cursor.execute('''
CREATE TABLE messages(
ID_message INTEGER PRIMARY KEY AUTOINCREMENT,
content TEXT NOT NULL,
type INTEGER NOT NULL,
ID_user INTEGER NOT NULL,
ID_channel INTEGER NOT NULL,
timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY(ID_user) REFERENCES users(ID_user),
FOREIGN KEY(ID_channel) REFERENCES channels(ID_channel)
)
''')

# Create authorized_users table
cursor.execute('''
CREATE TABLE authorized_users(
   ID_user INTEGER NOT NULL,
   ID_channel INTEGER NOT NULL,
   role INT NOT NULL,
   PRIMARY KEY(ID_user, ID_channel),
   FOREIGN KEY(ID_user) REFERENCES users(ID_user),
   FOREIGN KEY(ID_channel) REFERENCES channels(ID_channel)
)
''')

# Create the logs table
cursor.execute('''
CREATE TABLE logs(
    ID_log INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    data TEXT NOT NULL
)
''')

# Create triggers for the users table
cursor.execute('''
CREATE TRIGGER user_insert AFTER INSERT ON users
BEGIN
    INSERT INTO logs (action, data) VALUES ('User inserted', 'ID_user=' || NEW.ID_user || ', Username=' || NEW.username || ', Password=' || NEW.password);
END;
''')

cursor.execute('''
CREATE TRIGGER user_update AFTER UPDATE ON users
BEGIN
    INSERT INTO logs (action, data) VALUES ('User updated', 
        'Old: ID_user=' || OLD.ID_user || ', username=' || OLD.username || ', Password=' || OLD.Password ||
        '; New: ID_user=' || NEW.ID_user || ', username=' || NEW.username || ', Password=' || NEW.Password);
END;
''')

cursor.execute('''
CREATE TRIGGER user_delete AFTER DELETE ON users
BEGIN
    INSERT INTO logs (action, data) VALUES ('User deleted', 'ID_user=' || OLD.ID_user || ', username=' || OLD.username || ', Password=' || OLD.Password);
END;
''')

# Create triggers for the channels table
cursor.execute('''
CREATE TRIGGER channel_insert AFTER INSERT ON channels
BEGIN
    INSERT INTO logs (action, data) VALUES ('Channel inserted', 'ID_channel=' || NEW.ID_channel || ', Name=' || NEW.Name || ', Password=' || NEW.Password);
END;
''')

cursor.execute('''
CREATE TRIGGER channel_update AFTER UPDATE ON channels
BEGIN
    INSERT INTO logs (action, data) VALUES ('Channel updated', 
        'Old: ID_channel=' || OLD.ID_channel || ', Name=' || OLD.name || ', Password=' || OLD.password ||
        '; New: ID_channel=' || NEW.ID_channel || ', Name=' || NEW.name || ', Password=' || NEW.password);
END;
''')

cursor.execute('''
CREATE TRIGGER channel_delete AFTER DELETE ON channels
BEGIN
    INSERT INTO logs (action, data) VALUES ('Channel deleted', 'ID_channel=' || OLD.ID_channel || ', Name=' || OLD.Name || ', Password=' || OLD.Password);
END;
''')

# Create triggers for the messages table
cursor.execute('''
CREATE TRIGGER message_insert AFTER INSERT ON messages
BEGIN
    INSERT INTO logs (action, data) VALUES ('Message inserted', 'ID_message=' || NEW.ID_message || ', Content=' || NEW.Content || ', Type=' || NEW.Type || ', ID_user=' || NEW.ID_user || ', ID_channel=' || NEW.ID_channel || ', Timestamp=' || NEW.timestamp);
END;
''')

cursor.execute('''
CREATE TRIGGER message_update AFTER UPDATE ON messages
BEGIN
    INSERT INTO logs (action, data) VALUES ('Message updated', 
        'Old: ID_message=' || OLD.ID_message || ', Content=' || OLD.Content || ', Type=' || OLD.Type || ', ID_user=' || OLD.ID_user || ', ID_channel=' || OLD.ID_channel || ', Timestamp=' || OLD.timestamp ||
        '; New: ID_message=' || NEW.ID_message || ', Content=' || NEW.Content || ', Type=' || NEW.Type || ', ID_user=' || NEW.ID_user || ', ID_channel=' || NEW.ID_channel || ', Timestamp=' || NEW.timestamp);
END;
''')

cursor.execute('''
CREATE TRIGGER message_delete AFTER DELETE ON messages
BEGIN
    INSERT INTO logs (action, data) VALUES ('Message deleted', 'ID_message=' || OLD.ID_message || ', Content=' || OLD.Content || ', Type=' || OLD.Type || ', ID_user=' || OLD.ID_user || ', ID_channel=' || OLD.ID_channel || ', Timestamp=' || OLD.timestamp);
END;
''')

# Create triggers for the authorized_users table
cursor.execute('''
CREATE TRIGGER authorized_user_insert AFTER INSERT ON authorized_users
BEGIN
    INSERT INTO logs (action, data) VALUES ('Authorized user inserted', 'ID_user=' || NEW.ID_user || ', ID_channel=' || NEW.ID_channel || ', Role=' || NEW.role);
END;
''')

cursor.execute('''
CREATE TRIGGER authorized_user_update AFTER UPDATE ON authorized_users
BEGIN
    INSERT INTO logs (action, data) VALUES ('Authorized user updated', 
        'Old: ID_user=' || OLD.ID_user || ', ID_channel=' || OLD.ID_channel || ', Role=' || OLD.role ||
        '; New: ID_user=' || NEW.ID_user || ', ID_channel=' || NEW.ID_channel || ', Role=' || NEW.role);
END;
''')

cursor.execute('''
CREATE TRIGGER authorized_user_delete AFTER DELETE ON authorized_users
BEGIN
    INSERT INTO logs (action, data) VALUES ('Authorized user deleted', 'ID_user=' || OLD.ID_user || ', ID_channel=' || OLD.ID_channel || ', Role=' || OLD.role);
END;
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
