'''
    Our Model class
    This should control the actual "logic" of your website
    And nicely abstracts away the program logic from your page loading
    It should exist as a separate layer to any database or data structure that you might be using
    Nothing here should be stateful, if it's stateful let the database handle it
'''
import view
import random
# from no_sql_db import database
from sql import SQLDatabase
import hashlib
import json
# RSA encryption
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Random

# Initialise our views, all arguments are defaults for the template
page_view = view.View()

#-----------------------------------------------------------------------------
# Index
#-----------------------------------------------------------------------------

def index():
    '''
        index
        Returns the view for the index
    '''
    return page_view("index")

#-----------------------------------------------------------------------------
# Register
#-----------------------------------------------------------------------------

def register_form():
    return page_view("register")

def register_check(username, password, public_key):
    if not username:
        return(page_view("invalid", reason="Empty Username Field!!!"))
    if not password:
        return(page_view("invalid", reason="Empty Password Field!!!"))
    if public_key == "Error!!!":
        return(page_view("invalid", reason="public key not generated"))

    sql_db = SQLDatabase('user1.db')

    # Random Salt Generation and shuffle it twice
    salt = str(random.randint(0000, 9999)) + username
    rand_salt = ''.join(random.sample(salt,len(salt)))
    rand_salt = ''.join(random.sample(rand_salt,len(rand_salt)))
    # combine the salt with password
    salt_w_password = rand_salt + password
    # hash password
    hashed_password = hashlib.sha256(salt_w_password.encode()).hexdigest()
    
    # Key Generation
    # private_key = RSA.generate(2048, Random.new().read)
    # public_key = private_key.public_key()

    # # Add user into database
    # pub_key_db = convert_pub_key_to_str(public_key)
    # # print(pub_key_db)
    sql_db.add_user(username, hashed_password, rand_salt, public_key)
    sql_db.commit()
    # print(hashed_password)
    # print(tre)
    # private_string = convert_pub_key_to_str(private_key)
    # TODO: Private key handling here, or maybe output it
    # pem_prefix = '-----BEGIN PRIVATE KEY-----\n'
    # pem_suffix = '\n-----END PRIVATE KEY-----'

    # # Export PEM format key to multi-line string format
    # to_convert = private_key.exportKey('PEM').decode('ASCII')
    # # Remove prefixes & suffixes
    # to_convert = to_convert.removeprefix(pem_prefix).removesuffix(pem_suffix)
    # # Remove newline characters
    # # converted_private_key = to_convert.replace('\n','') 
    # file_name = 'static/js/info.json'
    
    # with open(file_name, 'w') as file_object:  #open the file in write mode
    #     json.dump(to_convert, file_object)
    
    return page_view("valid", name=username)

#-----------------------------------------------------------------------------
# Login
#-----------------------------------------------------------------------------

def login_form():
    '''
        login_form
        Returns the view for the login_form
    '''
    return page_view("login")

#-----------------------------------------------------------------------------

# Check the login credentials
def login_check(username, password):
    '''
        login_check
        Checks usernames and passwords

        :: username :: The username
        :: password :: The password

        Returns either a view for valid credentials, or a view for invalid credentials
    '''

    # By default assume good creds
    login = True

    sql_db = SQLDatabase('user1.db')

    # getting the salt of this username
    salt = sql_db.get_salt(username)
    if salt == None:
        return page_view("invalid", reason="error")
    
    # combine the salt with password
    salt_w_password = salt + password
    # hash pwd
    hashed_password = hashlib.sha256(salt_w_password.encode()).hexdigest()
    # print(hashed_password)

    

    if sql_db.check_credentials(username, hashed_password) == False:
        err_str = "Incorrect username or password"
        login = False

        
    if login: 
        friendlist = sql_db.get_user()
        return page_view("login_valid", name=username, list=friendlist)
    else:
        return page_view("invalid", reason=err_str)

#-----------------------------------------------------------------------------
# Key formatting and handling
#-----------------------------------------------------------------------------
# Convert Public Key (PEM format) to string and vice versa
def convert_pub_key_to_str(public_key):
    pem_prefix = '-----BEGIN PUBLIC KEY-----\n'
    pem_suffix = '\n-----END PUBLIC KEY-----'

    # Export PEM format key to multi-line string format
    to_convert = public_key.exportKey('PEM').decode('ASCII')
    # Remove prefixes & suffixes
    to_convert = to_convert.removeprefix(pem_prefix).removesuffix(pem_suffix)
    # Remove newline characters
    converted_pub_key = to_convert.replace('\n','') 
    return converted_pub_key

def read_public_key_as_PEM(public_key_string):
    '''
        read_public_key
        Converts the public key string found in User to a PEM format and imports it

        :: public_key_string :: Public key in ASCII format after retrieval from database
        
        Returns the imported key
    '''
    # Attach prefixes and suffixes back into string
    to_import = '-----BEGIN PUBLIC KEY-----\n{}\n-----END PUBLIC KEY-----'.format(public_key_string)
    imported_key = RSA.import_key(to_import) # May/may not be needed
    return imported_key

    
#-----------------------------------------------------------------------------
# Send message
#-----------------------------------------------------------------------------
def mess_form(username):
    sql_db = SQLDatabase('user1.db')
    pub_k_string = sql_db.get_publickey(username)
    pub_k = read_public_key_as_PEM(pub_k_string)

    if pub_k_string is None:
        return page_view("invalid", reason="no such receiver")

    puo = pub_k.exportKey("PEM")

    return page_view("message_send", pubkey=puo, username=username)

    
def send_mess(receiver, message):
    sql_db = SQLDatabase('user1.db')
    sql_db.add_mess(receiver, message)
    return page_view("send_result", name=receiver)
    # ecrypt mess here and then store it in the database
    # sql_db = SQLDatabase('user1.db')
    # pub_k_string = sql_db.get_publickey(receiver)
    # pub_k = read_public_key_as_PEM(pub_k_string)

    # if pub_k is None:
    #     return page_view("invalid", reason="no such receiver")
    

    # encryptor = PKCS1_OAEP.new(pub_k)
    # encrypted_mess = encryptor.encrypt(message)
    # print(encrypted_mess)

    # sql_db.add_mess(encrypted_mess)
    # puo = pub_k.exportKey("PEM")
    # print(puo)
    # sql_db = SQLDatabase('user1.db')
    # sql_db.add_mess(message)
    # return page_view("send_result", name=receiver)
    # , pubkey=puo)

#-----------------------------------------------------------------------------
# See incoming message
#-----------------------------------------------------------------------------
def incoming(username):
    # get list of message here
    sql_db = SQLDatabase("user1.db")
    mess_list = sql_db.get_user_cipertexts(username)
    if len(mess_list) == 0:
        return page_view("no_mess")
    return page_view("incoming", list=mess_list)


#-----------------------------------------------------------------------------
# TODO: Escape character handling in SQL lines
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# About
#-----------------------------------------------------------------------------

def about():
    '''
        about
        Returns the view for the about page
    '''
    return page_view("about", garble=about_garble())



# Returns a random string each time
def about_garble():
    '''
        about_garble
        Returns one of several strings for the about page
    '''
    garble = ["leverage agile frameworks to provide a robust synopsis for high level overviews.", 
    "iterate approaches to corporate strategy and foster collaborative thinking to further the overall value proposition.",
    "organically grow the holistic world view of disruptive innovation via workplace change management and empowerment.",
    "bring to the table win-win survival strategies to ensure proactive and progressive competitive domination.",
    "ensure the end of the day advancement, a new normal that has evolved from epistemic management approaches and is on the runway towards a streamlined cloud solution.",
    "provide user generated content in real-time will have multiple touchpoints for offshoring."]
    return garble[random.randint(0, len(garble) - 1)]


#-----------------------------------------------------------------------------
# Debug
#-----------------------------------------------------------------------------

def debug(cmd):
    try:
        return str(eval(cmd))
    except:
        pass


#-----------------------------------------------------------------------------
# 404
# Custom 404 error page
#-----------------------------------------------------------------------------

def handle_errors(error):
    error_type = error.status_line
    error_msg = error.body
    return page_view("error", error_type=error_type, error_msg=error_msg)