import os
import pprint
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

from classes import Search, SearchForm, Database, Recipe

app = Flask(__name__)
# mongoDB config
app.config['MONGO_DBNAME'] = os.environ.get("MONGO_DBNAME")
app.config['MONGO_URI'] = os.environ.get("MONGO_URI")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

users_colection = mongo.db.users
recipes_colection = mongo.db.recipes
shemas_colection = mongo.db.schemas
forms_colection = mongo.db.forms
trivia_colection = mongo.db.trivia

recipe_schema_id = "5ba2ded543277a316cbf0ef9"

""" testing """

testing_colection = mongo.db.testing

"""  """

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

    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("index.html", page_title="Cookbook", username=session['user'], user_id=user_in_db['_id'], forms=forms, main_recipe=main_recipe, side_recipes=side_recipes, trivia=trivia)
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
            flash("Sorry there seems to be problem with the data")
            return redirect(url_for('index'))
        if user_in_db:
            if check_password_hash(user_in_db['password'], password):
                session['user'] = username
                flash(f"Logged in as {username}")
                return_url = request.referrer
                return redirect(return_url)
            else:
                flash("Invalid username or password")
                return redirect(url_for('index'))
        else:
            flash(f"Sorry no profile {request.form['username']} found")
            return redirect(url_for('index'))


# Sign up
@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    forms = forms_colection.find()
    if request.method == "POST":
        user_in_db = mongo.db.users.find_one(
            {"username": request.form['username']})
        if user_in_db:
            flash(f"Sorry profile {request.form['username']} already exist")
            return render_template("sign-up.html", page_title="Sign up", forms=forms)

        hashed_pass = generate_password_hash(request.form['user_password'])
        users_colection.insert_one(
            {'username': request.form['username'], 'password': hashed_pass, 'recipes': []})
        user_in_db = users_colection.find_one(
            {"username": request.form['username']})
        session['user'] = request.form['username']
        return redirect(url_for('profile', user_id=user_in_db['_id'], forms=forms))

    if 'user' in session:
        return render_template("sign-up.html", page_title="Sign up", username=session['user'], forms=forms)

    return render_template("sign-up.html", page_title="Sign up", forms=forms)

# Log out


@app.route('/logout')
def logout():
    session.pop('user')
    flash("Successfully logged out ...")
    return_url = request.referrer
    return redirect(return_url)

# Profile Page


@app.route('/profile/<user_id>')
def profile(user_id):
    forms = forms_colection.find()
    if 'user' in session:
        user = Search(users_colection, "users").find_one_by_id(user_id)
        return render_template("profile.html", page_title="profile", user=user, forms=forms)

    return redirect(url_for('index', forms=forms))


"""

Recipes


"""

# Main route for all recipes


@app.route('/recipes')
def recipes():
    recipes_in_db = Search(recipes_colection).sort_find_all()
    forms = forms_colection.find()
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title="Recipes", recipes=recipes_in_db,  user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title="Recipes", recipes=recipes_in_db, forms=forms)

# Main route for single recipe


@app.route('/recipe/<recipe_id>', methods=['GET', 'POST'])
def recipe(recipe_id):
    recipe = Search(recipes_colection).find_one_by_id(recipe_id)
    forms = forms_colection.find()
    if request.method == "POST":
        return render_template("recipe.html", page_title=recipe['title'], recipe_id=recipe_id, recipe=recipe, forms=forms)
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipe.html", page_title=recipe['title'], recipe_id=recipe_id, recipe=recipe, forms=forms,  user_in_db=user_in_db, user_id=user_in_db['_id'])
    return render_template("recipe.html", page_title=recipe['title'], recipe_id=recipe_id, recipe=recipe, forms=forms)

# Add Recipe


@app.route('/add_recipe/<user_id>', methods=['GET', 'POST'])
def add_recipe(user_id):
    forms = forms_colection.find()
    recipe_schema = Search(shemas_colection).find_one_by_id(recipe_schema_id)
    if request.method == "POST":
        form_data = request.form.to_dict()
        data = Recipe(form_data)
        data = data.__dict__
        new_recipe = recipes_colection.insert(data["recipe"])
        recipe_id = str(new_recipe)
        recipe = data["recipe"]
        users_colection.update({"username": session['user']}, {
                               '$push': {'recipes': recipe_id}})
        user_in_db = users_colection.find_one({"username": session['user']})

        flash("Recipe added. Thank you!")
        return redirect(url_for("recipe", recipe_id=recipe_id, recipe=recipe, forms=forms, user_in_db=user_in_db, user_id=user_in_db['_id'], page_title=recipe['title']))
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("add-recipe.html", page_title="Add recipe", user_in_db=user_in_db, user_id=user_in_db['_id'], forms=forms, recipe_schema=recipe_schema)

    return redirect(url_for('index', forms=forms))

# Edit Recipe


@app.route('/edit_recipe/<recipe_id>/<user_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id, user_id):
    forms = forms_colection.find()
    if request.method == "POST":
        form_data = request.form.to_dict()
        data = Recipe(form_data)
        data = data.__dict__
        recipes_colection.update({'_id': ObjectId(recipe_id)}, data["recipe"])
        recipe = data["recipe"]
        flash("Your recipe has been updated")
        user_in_db = users_colection.find_one({"username": session['user']})
        return redirect(url_for("recipe", page_title=recipe['title'], recipe_id=recipe_id, recipe=recipe, forms=forms, user_in_db=user_in_db, user_id=user_in_db['_id']))
    else:
        if 'user' in session:
            recipe = Search(recipes_colection).find_one_by_id(recipe_id)
            user_in_db = Search(users_colection, "").find_one_by_id(user_id)
            for x in user_in_db["recipes"]:
                if x == recipe_id:
                    return render_template("edit-recipe.html", page_title="Edit recipe", recipe_id=recipe_id, recipes=recipe, forms=forms,  user_in_db=user_in_db, user_id=user_in_db['_id'])
    return redirect(url_for('index'))


""" Search  """

# Search view for mobiles


@app.route('/mobile_search', methods=['GET', 'POST'])
def mobile_search():
    forms = forms_colection.find()
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("search-form-sm.html", page_title="Search",  user_id=user_in_db['_id'], forms=forms)
    return render_template("search-form-sm.html", page_title="Search", forms=forms)


# Search via form input


@app.route('/input_form_search', methods=['GET', 'POST'])
def input_form_search():
    if request.method == "POST":
        form_data = request.form.to_dict()
        forms = forms_colection.find()
        recipes = SearchForm(form_data).search_by_input()
        if len(recipes) == 0:
            flash("Sorry did not find any recipes!")
            return_url = request.referrer
            return redirect(return_url)
        else:
            return render_template("recipes.html", recipes=recipes, forms=forms)
    return redirect(url_for('index', forms=forms))

# Search via form tags


@app.route('/tags_form_search', methods=['GET', 'POST'])
def tags_form_search():
    if request.method == "POST":
        form_data = request.form.to_dict()
        pprint.pprint(form_data)
        forms = forms_colection.find()
        recipes = SearchForm(form_data).search_by_tags()
        return render_template("recipes.html", recipes=recipes, forms=forms)
    return redirect(url_for('index', forms=forms))

# Get how many recipes match the input


@app.route('/num_of_input_results', methods=['POSt'])
def num_of_input_results():
    if request.method == "POST":
        form_data = request.form.to_dict()
        recipes = SearchForm(form_data).search_by_input()
        return str(len(recipes))

# Get how many recipes match the tags


@app.route('/num_of_tags_results', methods=['POSt'])
def num_of_tags_results():
    if request.method == "POST":
        form_data = request.form.to_dict()
        recipes = SearchForm(form_data).search_by_tags()
        return str(len(recipes))


# Search by Dish types


@app.route('/dish_types/<dish_type>')
def search_by_type(dish_type):
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection).all_filters(
        key="dishTypes", value=dish_type)
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title=dish_type.capitalize() + "s", recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title=dish_type.capitalize() + "s", recipes=recipes_in_db, forms=forms)


# Search by Diets


@app.route('/diet_types/<diet_type>')
def search_by_diet(diet_type):
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection).all_filters(
        key="diets", value=diet_type)
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title=diet_type.capitalize(), recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title=diet_type.capitalize(), recipes=recipes_in_db, forms=forms)

# Search by Time


@app.route('/search_by_time')
def search_by_time():
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection,
                           order=1, sort="readyInMinutes").sort_find_all()
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title="Time", recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title="Time", recipes=recipes_in_db, forms=forms)

# Search by Cuisines


@app.route('/search_by_cuisine/<cuisine>')
def search_by_cuisines(cuisine):
    forms = forms_colection.find()
    recipes_in_db = Search(colection=recipes_colection).all_filters(
        key="cuisines", value=cuisine)
    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        return render_template("recipes.html", page_title=cuisine.capitalize(), recipes=recipes_in_db, user_id=user_in_db['_id'], forms=forms)
    return render_template("recipes.html", page_title=cuisine.capitalize(), recipes=recipes_in_db, forms=forms)


""" Others """

# Admin Dashboard


@app.route('/admin_dashboard')
def dashboard():
    """ if request.method == "GET":


            hidden_recipes = recipes_colection.delete_many({"visibility": False}) """

    if 'user' in session:
        user_in_db = users_colection.find_one({"username": session['user']})
        users = users_colection.find()
        forms = forms_colection.find()
        hidden_recipes = recipes_colection.find({"visibility": False})
        return render_template("dashboard.html", page_title="dashboard", users=users, forms=forms, hidden_recipes=hidden_recipes, user_id=user_in_db['_id'])
    return redirect(url_for('index'))


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
	if os.environ.get("DEVELOPMENT"):
		app.run(host=os.environ.get('IP'),
				port=os.environ.get('PORT'),
				debug=True)
	else:
		app.run(host=os.environ.get('IP'),
                    port=os.environ.get('PORT'),
                    debug=False)


""" 

Temporary notes

"""


# edit recipes
# search by user names
# profile page
# edit profile
