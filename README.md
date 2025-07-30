****Python Bank****

Python Bank is an application that seeks to simulate a small bank that accepts transactions between it's own users. User's can transfer money from one account to another, and only beginning from their own accounts and assuming they have the proper funds. Employees have their own custom dashboard, that allows them to create users, as well as deleting them. This is also where interest is applied, an employee is able to apply the interest to all user's savings accounts. Admins also have their own hub, allowing them all the perks of employees, but also being able to see all employees. There is also a basic integration of a chatroom.


**Libraries Required**

Flask

Flask_Limiter

Flask_Limiter.Util

Flask_Socketio

datetime

functools

decimal

bcrypt

psycopg2

multiprocessing

concurrent.futures

****FURTHER REQUIREMENTS TO RUN****
This program requires postgres. You do not need to do anything on your end aside from have a valid postgres install, for the purpose of this project it simply places the tables in the main postgres table, so it should always work. If you want it in a specific database, you may edit the code in database.py so that ("dbname=*yourdbhere* user=postgres password=x"), as long as said database exists in your local postgres. For simplicity and easy of this project, we chose to just place it directly into postgres db. 

****Beyond Scope****


A basic chatroom was created which was beyond the original scope. The intention was to allow a secure connection between a user and an employee. This feature was not fully completed by the end, but the scaffold is there and messages are able to be sent. Scaffold of code set up for parallelizing processing pending transactions was also created, though this was never finalized. 


****Role Distribution****


Everybody did well assisting everywhere, however areas of focus were: 

Isaac: Majority of database functions. Created scaffold and beginning of flask frontend/backend implementation. Created ability to send transactions to other users. 

Alex: Security, used bcrypt and implemented security and hashing of passwords. Additionally introduced a limiter and chatroom scaffold. 

Ben: Created functions to allow for implementation of parellelization of pending transactions. This would allow for an overhaul of the transaction system and sending them.

Ayah: Worked in flask development, cleaning up and writing correct html scaffolding for flask apps and adding RequiredRole decorators to functions. Additionally, corrected and enhanced elements of the database.

Miguel: Added security decorators and also implemented parallelization in the form of the interest calculator, writing the entire process of that.

Landon: Created admin role, did work with the employee and admin pages, adding in the feature to create other accounts. Bug fixes and correcting a lot of code in app.py to be more standard and correct. Added back buttons.
