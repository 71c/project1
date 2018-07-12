# Project 1

Web Programming with Python and JavaScript

This is a website where you can log into it and get information such as population, coordinates, and weather, about an area in the US by zipcode.
You can also submit "check-ins" to places along with comments.d

On the `location.html` page, a check-in is a comment. When it says "[number] Check-ins" at the bottom it really means comments, but I wanted to use the word "check-in" to be sure to meet the requirements. It was unclear to me how the check-ins and comments are supposed to work: Can you make a comment before making a check-in? Is the comment part separate from the check-in or is it part of it? I made it so they are the same. Because of this, you can only write one comment per zipcode (since a user can make only one check-in).

## Files
* templates/: contains all the templates for Flask to render
    * error.html: error page
    * index.html: you can choose to log in or sign up from here.
    * layout.html: the basic layout of all the pages
    * location.html: shows information about a location
    * login.html: log-in page
    * results.html: shows the results for a search
    * search.html: where you can search for a location
    * signup.html: sign-up page
* application.py: contains the Flask application that makes the site work
* import.py: was used to put the information from zips.csv into a database.
* README.md: the readme
* reqirements.txt: the required Python modules for running the application
* zips.csv: location about places by zipcode
* danltck14i7gdv.sql: sql database used