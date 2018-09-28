# The Cookbook

## CI project-4

### Changelog

#### 1.0

- Added User registration and Login  
- Added Admin dashboard for testing
- Added @routes for all above
- Added security via hashed password
- Users are now stored in mongoDB database
- Added unique link for every user
- Added sessions for users

#### 1.1

- Connected to API

#### 1.2

- Added fundamentals for recipes page
- Added fundamentals for single recipe page
- Added Search class for searching the database for recipes
- Added functionality to search by dish types, cuisines, time needed and diets
- Redesign  Search class to work for any colection
- helper.py no longer used
- Updating db now via JS for better user experiences
- Added SearchForm class for main search 
- Also connected the form to back-end 

#### 1.3

- Finished index recipes section
- Added random recipes and trivia to this section
- Finished recipe.html

#### 1.4

- Added schema for recipe based on the API
- Added constructor class base on the schema for updating a recipe
- Finished edit recipe
- Added more JS for user experiences
- Fixed many errors along the way
- Added filters and errors handling in add / endit form
- Users are now able to print the recipes 

#### 1.5

- schema.py no longer in use
- Moved Recipe class to classes.py
- Slightly improved database structure for better readability and manipulation with data
- Extended the Search class to be able to search by $match, $text
- Search class now dynamically set the default limit based on documents count
- User is now redirected to the last page viewed when log-in/out
- Add flashed messages for user when login-in / out and search recipes errors
- Moved "Trivia" section to top for better visibility

##### Search form

- Added second button to search form for user to clearly see what he is searching for
- While changing the tags user now see the number of results before searching
- If no recipes found the search button is disabled and user is asked to remove some of the filters
- Removed "Search by" as this was getting too confusing for user. Instead the search input searches fro any matching results
- Added min and max length to imput search. JS also chceking for input length and enabling / disabling search input btn
- JS now also checking how many recipes are found on input change
- Create separate view for mobile devices search

### What could be done better

- Could take the advantege of WTForms which could greatly speed up the development
- MUCH better error handling. Right now minimum to none
- Again tests has been done manualy or with litlle use of automated tests
- Also need to push to GitHub more often and or number the pushes more clearly 
- Still think that this project is "better" done by SQL due to relation between recipes, tags and so on