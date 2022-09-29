'''
    This is a file that configures how your server runs
    You may eventually wish to have your own explicit config file
    that this reads from.

    For now this should be sufficient.

    Keep it clean and keep it simple, you're going to have
    Up to 5 people running around breaking this constantly
    If it's all in one file, then things are going to be hard to fix

    If in doubt, `import this`
'''

#-----------------------------------------------------------------------------
import os
import sys
from bottle import run
from bottle import Bottle

#-----------------------------------------------------------------------------
# You may eventually wish to put these in their own directories and then load 
# Each file separately

# For the template, we will keep them together

import model
import view
import controller
import os
# import requests

#-----------------------------------------------------------------------------

# It might be a good idea to move the following settings to a config file and then load them
# Change this to your IP address or 0.0.0.0 when actually hosting
host = 'localhost'

# Test port, change to the appropriate port to host
port = 8081

# Turn this off for production
debug = True
# def verify_cert():
#     requests.get('https://somesite.com', cert='/path/server.crt', verify=True)

def run_server():    
    '''
        run_server
        Runs a bottle server
    '''
    # run(host=host, port=port, debug=debug)
    # file_path = os.path.basename(os.path.dirname(__file__))
    key_path =  './info2222.go.key'
    cert_path =  './info2222.go.crt'
    config_path =  './info2222.go.ext'
    run(host=host, port=port, debug=debug, server='gunicorn', keyfile=key_path, certfile=cert_path, config=config_path)

#-----------------------------------------------------------------------------
# Optional SQL support
# Comment out the current manage_db function, and 
# uncomment the following one to load an SQLite3 database

"""
def manage_db():
    '''
        Blank function for database support, use as needed
    '''
    # no_sql_db.database
    
    # Create initial table entry for admin ('users', "id", "username", "password")
    database.create_table_entry('users', ["0", "admin", "password"])
    print(database.search_table('users', "id", "0"))
    
    
    pass

"""
import sql
    
def manage_db():
    '''
        manage_db
        Starts up and re-initialises an SQL databse for the server
    '''
    database_args = "user1.db" # Currently runs in RAM, might want to change this to a file if you use it
    sql_db = sql.SQLDatabase(database_args)
    sql_db.database_setup()
    sql_db.commit()

    # sql_db.execute("SELECT * FROM Users")
    # print(sql_db.cur.fetchall())

    return


#-----------------------------------------------------------------------------

# What commands can be run with this python file
# Add your own here as you see fit

command_list = {
    'manage_db' : manage_db,
    'server'    : run_server
}

# The default command if none other is given
default_command = 'server'

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''
    commands = args[1:]

    # Default command
    if len(commands) == 0:
        commands = ['manage_db', default_command]

    for command in commands:
        if command in command_list:
            command_list[command]()
        else:
            print("Command '{command}' not found".format(command=command))

    

    

#-----------------------------------------------------------------------------
run_commands(sys.argv)
