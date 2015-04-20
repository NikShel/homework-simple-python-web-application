import shelve

UsersDB = shelve.open('users', writeback=True)
LinksDB = shelve.open('links', writeback=True)
for x in UsersDB:
    del UsersDB[x]
for x in LinksDB:
    del LinksDB[x]
LinksDB['Last'] = 0