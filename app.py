import os
from flask import Flask, render_template, redirect, request, url_for, session, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

from werkzeug.security import generate_password_hash, check_password_hash

from schema import RecipeSchema

from key import db_name, uri, log_in_key
from classes import Search, SearchForm, Database

app = Flask(__name__)
# mongoDB config
app.config['MONGO_DBNAME'] = db_name()
app.config['MONGO_URI'] = uri()
app.config['SECRET_KEY'] = log_in_key()

mongo = PyMongo(app)

users_colection = mongo.db.users
recipes_colection = mongo.db.recipes
forms_colection = mongo.db.forms
# jokes_colection = mongo.db.jokes
trivia_colection = mongo.db.trivia

# Index
@app.route('/')
@app.route('/index')
def index():
    forms = forms_colection.find()
    trivia = Search(trivia_colection).random(num_of_results=1)
    random_recipes = [x for x in Search(
        recipes_colection).random(num_of_results=4)]
    main_recipe = random_recipes[0]
    side_recipes = random_recipes[1:]
    	
    if session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("index.html", page_title="Cookbook", username=session['user'], user_id=user_in_db['_id'], forms=forms, main_recipe=main_recipe, recipes=side_recipes, trivia=trivia)
    return render_template("index.html", page_title="Cookbook", forms=forms, main_recipe=main_recipe, side_recipes=side_recipes, trivia=trivia)


""" Users / Log-in / Register """

# Login


@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['user_password']
        try:
            user_in_db = users_colection.find_one({"username": username})
        except:
            return "Sorry there seems to be problem with the data"
        if user_in_db:
            if check_password_hash(user_in_db['password'], password):
                session['user'] = username
                return redirect(url_for('profile', user_id=user_in_db['_id'], username=username))
            else:
                return "Invalid username or password"
        else:
            return f"Sorry no profile {request.form['username']} found"


# Sign up
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    forms = forms_colection.find()
    if request.method == "POST":
        user_in_db = mongo.db.users.find_one(
            {"username": request.form['username']})
        if user_in_db:
            return f"Sorry profile {request.form['username']} already exist"

        hashed_pass = generate_password_hash(request.form['user_password'])
        users_colection.insert_one(
            {'username': request.form['username'], 'password': hashed_pass, 'recipes': []})
        user_in_db = users_colection.find_one(
            {"username": request.form['username']})
        session['user'] = request.form['username']
        return redirect(url_for('profile', user_id=user_in_db['_id'], forms=forms))
    if session:
        return render_template("sign-up.html", page_title="Sign up", username=session['user'], forms=forms)

    return render_template("sign-up.html", page_title="Sign up", forms=forms)

# Log out


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))

# Profile Page


@app.route('/profile/<user_id>')
def profile(user_id):
    forms = forms_colection.find()
    if session:
        user = Search(users_colection, "users").find_one_by_id(user_id)
        return render_template("profile.html", page_title="profile", user=user, forms=forms)

    return redirect(url_for('index', forms=forms))


""" 

Recipes 


"""

# Main route for all recipes


@app.route('/recipes')
def recipes():
    recipes_in_db = Search(recipes_colection, "recipes").sort_find_all()
    forms = forms_colection.find()
    if session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title="Recipes", recipes=recipes_in_db,  user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title="Recipes", recipes=recipes_in_db, forms=forms)

# Main route for single recipe


@app.route('/recipe/<recipe_id>')
def recipe(recipe_id):
	recipe = Search(recipes_colection, "recipes").find_one_by_id(recipe_id)
	forms = forms_colection.find()
	if session:
		user_in_db = users_colection.find_one({"username": session['user']})
		return render_template("recipe.html", page_title=recipe['recipes'][0]['title'], recipe_id=recipe_id, recipe=recipe, forms=forms,  user_in_db=user_in_db)
	return render_template("recipe.html", page_title=recipe['recipes'][0]['title'], recipe_id=recipe_id, recipe=recipe, forms=forms)

# Edit Recipe

@app.route('/edit_recipe/<recipe_id>/<user_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id, user_id):
	if request.method == "POST":
		form_data = request.form.to_dict()
		print(form_data)
		print("-------------------------------------------------")
	else:
		if session:
			recipe = Search(recipes_colection, "recipes").find_one_by_id(recipe_id)
			forms = forms_colection.find()
			user_in_db = Search(users_colection, "").find_one_by_id(user_id)
			for x in user_in_db["recipes"]:
				if x == recipe_id:
					return render_template("edit-recipe.html", page_title="Edit recipe", recipe_id=recipe_id, recipe=recipe, forms=forms,  user_in_db=user_in_db)
	return redirect(url_for('index'))

""" Search  """

# Search via form


@app.route('/search_form', methods=['POST'])
def search_form():
    if request.method == "POST":
        form_data = request.form.to_dict()
        forms = forms_colection.find()
        # For testing only
        mongo.db.pokus.insert_one(form_data)
        return render_template("recipes.html", page_title="Recipes", recipes=SearchForm().search_reluts(form_data), forms=forms)


# Search by Dish types


@app.route('/dish_types/<dish_type>')
def search_by_type(dish_type):
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection,
                           dic_name="recipes").all_filters(key="dishTypes", value=dish_type)
    if session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title=dish_type.capitalize() + "s", recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title=dish_type.capitalize() + "s", recipes=recipes_in_db, forms=forms)


# Search by Diets types


@app.route('/diet_types/<diet_type>')
def search_by_diet(diet_type):
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection,
                           dic_name="recipes").all_filters(key="diets", value=diet_type)
    if session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title=diet_type.capitalize(), recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title=diet_type.capitalize(), recipes=recipes_in_db, forms=forms)

# Search by Time


@app.route('/search_by_time')
def search_by_time():
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection,
                           dic_name="recipes", order=1, sort="readyInMinutes").sort_find_all()
    if session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title="Time", recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title="Time", recipes=recipes_in_db, forms=forms)

# Search by Cuisines


@app.route('/search_by_cuisine/<cuisine>')
def search_by_cuisines(cuisine):
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection,
                           dic_name="recipes").all_filters(key="cuisines", value=cuisine)
    if session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title=cuisine.capitalize(), recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title=cuisine.capitalize(), recipes=recipes_in_db, forms=forms)


""" Others """

# Admin Dashboard


@app.route('/admin_dashboard')
def dashboard():
    users = users_colection.find()
    forms = forms_colection.find()
    hidden_recipes = recipes_colection.find({"recipes.visibility": False})
    return render_template("dashboard.html", page_title="dashboard", users=users, forms=forms, hidden_recipes=hidden_recipes)


# Update db

@app.route('/update-db', methods=['POST'])
def update_db():
    if request.method == "POST":
        Database().update_search_form()
        users = Search(users_colection, "users").sort_find_all()
        forms = forms_colection.find()

        return render_template("dashboard.html", page_title="dashboard", users=users, forms=forms)


# Error page


@app.route('/error')
def error():
    return render_template("error.html")


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=os.environ.get('PORT'),
            debug=True)




""" 

Temporary notes

"""

# add for user to add new category
# edit recipes
# add loop to modify the recepis (add user names)
# search by user names
# profile page 
# edit profile
