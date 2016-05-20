# Item Catalog Project

## Project Description
-To develop an application that provides a list of items within a variety of categories
-provide a user registration and authentication system. 
-Registered users will have the ability to post, edit and delete their own items.

## Running the program
In order to run the program, Python and a virtual machine are required.

1. Access the vagrant folder through catalog using the virtual machine `cd catalog/vagrant/`. 
2. Enter the commands `vagrant up` and `vagrant ssh`. 
3. Access the vagrant folder using `cd /vagrant/catalog/`.
4. Now run `python application.py` to run the project.
5. Access the homepage http://localhost:5040/catalog/

If the project is running correctly it should return this output:

1. The homepage displays all current categories along with the latest added items.
2. Selecting a specific category shows you all the items available for that category.
3. Selecting a specific item shows you specific information of that item.
4. A login page with the ability to login from facebook or google+
5. After logging in, a user has the ability to add, update, or delete item or category info.
6. The application provides a JSON endpoint
7. A logout button to log out of your account

If it returns the output above, the program has run successfully. To exit the VM
hit ctrl+d twice to logout.

## References

Software:
- Python 2.7.9
- SQLalchemy
- VirtualBox (Latest version)

Cited work:
- Udacity forums
- Github
- http://www.w3schools.com/sql/default.asp
- Udacity tutor: Adarsh Nair

