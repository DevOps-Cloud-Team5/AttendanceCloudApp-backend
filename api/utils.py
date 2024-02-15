# An example to load mongodb handle

# from pymongo import MongoClient
# from multipledispatch import dispatch

# @dispatch(str, str, int, str, str)
# def get_db_handle(db_name, host, port, username, password):

#     client = MongoClient(host=host,
#                         port=int(port),
#                         username=username,
#                         password=password
#                         )
#     db_handle = client[db_name]
#     return db_handle, client

# @dispatch(str)
# def get_db_handle(db_name):
#     client = MongoClient("mongodb://localhost")
#     db_handle = client[db_name]
#     return db_handle, client
