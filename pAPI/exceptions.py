class UsernameIsNull(Exception):
    '''if a username was not supplied for a DB needing one'''
    pass
    
class PasswordIsNull(Exception):
    '''if a password was not supplied for a DB needing one'''
    pass