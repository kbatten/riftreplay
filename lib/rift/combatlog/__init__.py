# todo: see if i can make it just be combatlog() instead of combatlog.combatlog()

def combatlog(name='', create=False, overwrite=False, loc='http://localhost:5984', kind='couchdb'):
    if kind == 'couchdb':
        import rift.combatlog.couchdb.combatlog
        return rift.combatlog.couchdb.combatlog.Combatlog(name, create, overwrite, loc)
    else:
        raise ErrorUnknownDatastoreType

class Error(Exception):
    pass

class ErrorUnknownDatastoreType(Error):
    pass
