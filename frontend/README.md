## Frontend for Lakehouse Sharing

### Frontend setup and walkthrough

- To show the value of the backend RestAPI built a quick and simple Streamlit APP. which is just a client for this Lakehouse-sharing, offloading all the authentication, admin related activities to the backend server.

#### As discussed above, the setup should straight forward.

- Step 1:  if you are using docker, docker-compose up (recommended approach for quick setup). otherwise, if you are adventurous set up the local server based on the installation and readme guide.

- Step 2: once the server and DB instance are ready, Run the python script to create and populate the database tables. Sample  entry population script was present inside the sqls folder of the root directory

- Step 3:  Start the backend server after installing the required dependencies (Skip if you are using docker-compose which will take care of this step already)

- Step 4: Start the Frontend APP. using the appropriate makefile command. (Skip if you are using docker-compose which will take care of this step already)

- Step 5: Log in to the Frontend APP using superuser credentials: (username: admin, password: admin@123)

- Step 6: Once Superuser was logged in, he/she can create n number of users and create a logical grouping under one namespace and share that with other teams or organizations.
