from flask import Flask, render_template, redirect, flash, request, session
from melons import get_all, get_by_id
from forms import LoginForm
from customers import get_by_username, customers
import jinja2

app = Flask(__name__)
app.secret_key = 'dev'

app.jinja_env.undefined = jinja2.StrictUndefined #for debugging purposes

### Flask Routes here. ###

@app.route("/")
def homepage():
    return render_template("base.html")

@app.route("/melons")
def all_melons():
    '''
    Return a page listing all the melons available for purchase.
    '''
    melon_list = get_all()
    return render_template("all_melons.html", melon_list=melon_list)

@app.route("/melon/<melon_id>")
def melon_details(melon_id):
    '''
    Return a page showing all info about a melon. Also, provide a button to buy that melon.
    '''
    melon = get_by_id(melon_id)
    return render_template("melon_details.html", melon=melon)

@app.route("/add_to_cart/<melon_id>")
def add_to_cart(melon_id):
    '''
    Add a melon to the shopping cart and redirect to the shopping cart page.
    '''

    if 'username' not in session: 
        return redirect("/login")

    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart'] #store cart in local variable to make things easier

    cart[melon_id] = cart.get(melon_id, 0) + 1
    session.modified = True
    flash(f"Melon {melon_id} successfully added to cart.")

    return redirect("/cart")


@app.route("/cart")
def show_shopping_cart():
    '''
    Display contents of shopping cart.
    '''
    if 'username' not in session: 
        return redirect("/login")

    order_total = 0
    cart_melons = []


    #Get cart dict from session (or an empty one if none exists yet)
    cart = session.get("cart", {})

    for melon_id, quantity in cart.items():
        melon = get_by_id(melon_id)

        #calculate total cost for this type of melon and add to order total
        total_cost = quantity * melon.price
        order_total += total_cost

        #Add the quantity and total cost as attributes on the Melon object
        melon.quantity = quantity
        melon.total_cost = total_cost

        cart_melons.append(melon)

    return render_template("cart.html", cart_melons=cart_melons, order_total=order_total)

@app.route("/empty-cart")
def empty_cart():
    session["cart"] = {}

    return redirect("/cart")

@app.route("/login", methods=["GET", "POST"])
def login():
    ''' Log user into site. '''
    form = LoginForm(request.form)

    if form.validate_on_submit():
        #Form has been submitted with valid data
        username = form.username.data
        password = form.password.data

        #Check to see if a registered user exists with this username
        user = get_by_username(username)

        if not user or user['password'] != password:
            flash("Invalid username or password")
            return redirect('/login')

        #Store username in session to keep track of logged in user 
        session["username"] = user["username"]
        flash("Logged in.")
        return redirect("/melons")
    
    #Form has not been submitted or data was not valid
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    ''' Log user out. '''

    del session["username"]
    flash("Logged out.")
    return redirect("/login")

@app.errorhandler(404)
def error_404(e):
    return render_template("404.html")







if __name__ == "__main__":
    app.env = "development"
    app.run(debug = True, port = 8000, host = "localhost")