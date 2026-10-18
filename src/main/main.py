import csv
import os
import sqlite3

# Resolve the resources folder relative to this file, so paths work
# no matter what directory the script is run from.
_RESOURCES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'resources')

# Connect to the SQLite in-memory database
conn = sqlite3.connect(':memory:')

# A cursor object to execute SQL commands
cursor = conn.cursor()

def main():

    # users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        userId INTEGER PRIMARY KEY,
                        firstName TEXT,
                        lastName TEXT
                      )'''
                   )

    # callLogs table (with FK to users table)
    cursor.execute('''CREATE TABLE IF NOT EXISTS callLogs (
        callId INTEGER PRIMARY KEY,
        phoneNumber TEXT,
        startTime INTEGER,
        endTime INTEGER,
        direction TEXT,
        userId INTEGER,
        FOREIGN KEY (userId) REFERENCES users(userId)
    )''')

    # You will implement these methods below. They just print TO-DO messages for now.
    load_and_clean_users(os.path.join(_RESOURCES_DIR, 'users.csv'))
    load_and_clean_call_logs(os.path.join(_RESOURCES_DIR, 'callLogs.csv'))
    write_user_analytics(os.path.join(_RESOURCES_DIR, 'userAnalytics.csv'))
    write_ordered_calls(os.path.join(_RESOURCES_DIR, 'orderedCalls.csv'))

    # Helper method that prints the contents of the users and callLogs tables. Uncomment to see data.
    # select_from_users_and_call_logs()

    # Close the cursor and connection. main function ends here.
    cursor.close()
    conn.close()


# TODO: Implement the following 4 functions. The functions must pass the unit tests to complete the project.


# This function will load the users.csv file into the users table, discarding any records with incomplete data
def load_and_clean_users(file_path):
    #calls read_file to begin reading file
    read_file(file_path, "user")


# This function will load the callLogs.csv file into the callLogs table, discarding any records with incomplete data
def load_and_clean_call_logs(file_path):
    #calls read_file to begin reading file
    read_file(file_path, "call")


# This function will write analytics data to testUserAnalytics.csv - average call time, and number of calls per user.
# You must save records consisting of each userId, avgDuration, and numCalls
# example: 1,105.0,4 - where 1 is the userId, 105.0 is the avgDuration, and 4 is the numCalls.
def write_user_analytics(csv_file_path):

    #query callLogs table then save the output to user_analytics
    cursor.execute("""
        SELECT userId, sum(startTime) AS sum_start_time, sum(endTime) AS sum_end_time, count(userId) AS num_calls
        FROM callLogs
        GROUP BY userId;
    """)
    user_analytics = cursor.fetchall()
    
    #open file found at csv_file_path and write the data found in user_analytics into it
    with open(csv_file_path, "w") as new_file:
        #add header to file
        new_file.write("userId,aveCallTime,numCalls,THISISATEST\n")

        #for each row in user_analytics, calculate call time and write userId, avgDuration, and numCalls into new_file
        for index, row in enumerate(user_analytics):
            call_time = (row[2] - row[1]) / row[3]
            if index != len(user_analytics) - 1:
                new_file.write(f"{row[0]},{call_time},{row[3]}\n")
            #if this is the last row in user_analytics, don't add new line character
            else:
                new_file.write(f"{row[0]},{call_time},{row[3]}")
        


# This function will write the callLogs ordered by userId, then start time.
# Then, write the ordered callLogs to orderedCalls.csv
def write_ordered_calls(csv_file_path):
    #query callLogs table then save output in ordered_calls
    cursor.execute("""
        SELECT * 
        FROM callLogs
        ORDER BY userId, startTime;

    """)
    ordered_calls = cursor.fetchall()

    #open file found at csv_file_path then write the data found in ordered_calls to it
    with open(csv_file_path, "w") as new_file:
        #add header
        new_file.write("callId,phoneNumber,startTime,endTime,direction,userId")
        for index, row in enumerate(ordered_calls):
            if index != len(ordered_calls) - 1:
                new_file.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}\n")
            else:
                new_file.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]}")
    
    with open("resources/orderedCalls.csv", "r") as file:
        for line in file:
            print(line)
        
             
#opens file located at file_path. 
#extracts and cleans data then passes clean data to insert_user or insert_call based on user_or_call
def read_file(file_path, user_or_call):
    header_list = []
    header_size = 0
    header_read = False

    #opens file at file_path for reading
    with open(file_path, "r") as my_file:
        #for each line in file. extract and clean the data. then call an insert function
        for line in my_file:
            #removes new line characters
            bad_record = False
            line = line.replace("\n", "")
            #if this is the first line, extract header
            if header_read == False:
                header_list = line.split(",")
                header_size = len(header_list)
                header_read = True
                continue

            #parse data. if data doesn't match up with the header or a data point is blank, go to next line
            new_record = line.split(",")

            for element in new_record:
                if not element.strip():
                    bad_record = True
                    break
            if bad_record == True:
                continue

            if len(new_record) != header_size or any(element == "" or element.startswith(" ") for element in new_record):
                continue

            

            
            #call insert_user or insert_call based on user_or_call. pass the cleaned line as an argument
            if user_or_call == "user":
                insert_users(new_record)
            elif user_or_call == "call":
                insert_call(new_record)
            #if neither 'user' or 'call' was found in user_or_call, raise an error
            else:
                print("ERROR: call or user not selected")
                return

#inserts a new user into users table
def insert_users(new_user):
    
    cursor.execute(f"""
        INSERT INTO users (firstName, lastName)
        VALUES ('{new_user[0]}', '{new_user[1]}');
    """)

#inserts a new call log into callLog table
def insert_call(new_call_log):

    cursor.execute(f"""
        INSERT INTO callLogs (phoneNumber, startTime, endTime, direction, userId)
        VALUES ('{new_call_log[0]}', '{new_call_log[1]}', '{new_call_log[2]}', '{new_call_log[3]}', '{new_call_log[4]}');
    """)
    

# No need to touch the functions below!------------------------------------------

# This function is for debugs/validation - uncomment the function invocation in main() to see the data in the database.
def select_from_users_and_call_logs():

    print()
    print("PRINTING DATA FROM USERS")
    print("-------------------------")

    # Select and print users data
    cursor.execute('''SELECT * FROM users''')
    for row in cursor:
        print(row)

    # new line
    print()
    print("PRINTING DATA FROM CALLLOGS")
    print("-------------------------")

    # Select and print callLogs data
    cursor.execute('''SELECT * FROM callLogs''')
    for row in cursor:
        print(row)

    


def return_cursor():
    return cursor


if __name__ == '__main__':
    main()