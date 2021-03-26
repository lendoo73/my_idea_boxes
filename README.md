#### [Build Python Web Apps with Flask Capstone Project](https://www.codecademy.com/paths/build-python-web-apps-flask/tracks/flask-capstone-project/modules/flask-capstone-project/informationals/flask-capstone-project)
# My Idea Box
1. Register your Company
2. Create some Idea Box
3. Invite your Colleagues to join

Or try how it is works without registration by clicking  
## [ Sample Company]  
button at bottom of the landing page.

### Jhon Do:
He has full privilegs to create, update, delete data from the database or add privilegs to another colleagues.  
To reset the sample database: click on Company, then click on Delete Company.
Heroku working a bit slow, if you reset the sample-database have to wait a bit.

### Jane Do:
She is a colleague without any privilegs. Add them some by log in with Jhon Do and see the differents...

### The third colleague is... also Do:

The above three colleagues are **static**, the rest of **colleagues** and 2 **Idea Boxes** with some **Ideas created randomly**. If you reset the sampe-database, you get different result every time.

## Privilegs:
I built in four different privilegs:
1. **Update Company:** any colleague with this privileg can 
    * update the Company name
    * update the Joining Password (this password required to invite colleagues to join to the Idea Box)
    * delete the Company (Deletion completly remove all colleagues and all Idea Boxes with Ideas belong to this Company)
2. **Update Colleagues:** a colleague with this privileg can 
    * help other colleagues at registration (so this is not a real privilegs...)
    * update any personal data of the joined colleagues (first name, last name, email, position, and also password). So if any colleague forgot password, can ask help from a colleagues with Update Colleague privileg to change the password.
    * update/delete the avatar of the colleague
    * delete any colleague of registration
3. **Update Privilegs:** colleague with this privileg can
    * add or remove Privilegs: minimum one colleague must to hold this privileg. By default only Jhon Do has. If you try to remove this privileg you will get a warning. If you remove Idea Box privileg from a colleague who created an Idea Box, then also the Idea Box will deleted with all of the Ideas. So be carefull before remove Idea Box privileg.
4. **Update Idea Box:** colleague with this privileg can
    * create/update/remove Idea Box
    * edit or remove an Idea by written someone else
    * but cannot to edit the sign of the colleagues.

## Colleagues:
Any colleagues can write/update own Idea if an Idea Box created until the box is opened. If a box already closed, then a colleague with Update Idea Box privileg can reopen it if extend the closing time.

#### [Database diagram](https://github.com/lendoo73/my_idea_boxes/blob/main/my_idea_box.pdf)

### [Run on Heroku](https://my-idea-boxes.herokuapp.com)
