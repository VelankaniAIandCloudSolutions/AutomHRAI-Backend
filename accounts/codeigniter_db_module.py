# import mysql.connector

# cnx = mysql.connector.connect(
#     user='velankanidb',
#     password='VelanKanidb@2123',
#     host='192.168.30.147',  
#     database='velankanidb'
# )

# def fetch_all_entities():

#     cursor = cnx.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM `dgt_branches`")

#     entities = cursor.fetchall()
#     cursor.close()
#     cnx.close()

#     return [entity for entity in entities]

# def fetch_all_departments():

#     cursor = cnx.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM `dgt_departments`")

#     departments = cursor.fetchall()
#     cursor.close()
#     cnx.close()

#     return [department for department in departments]

# def fetch_all_jobs():
#     cursor = cnx.cursor(dictionary=True)

#     cursor.execute("SELECT * FROM `dgt_jobs`")

#     jobs = cursor.fetchall()
#     cursor.close()
#     cnx.close()

#     return [job for job in jobs]