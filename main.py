
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, ARRAY
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from form import AddForm, DeleteForm, LoginForm, RegisterForm
from cart import Cart
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
cart = Cart()

cat_dict = {'dairy_bread_eggs': 'Dairy,Bread and Eggs',
            'fruits_vegetables': 'Fruits and Vegetables',
            'cold_drinks_juices': 'Cold Drinks and Juices',
            'snacks': 'Snacks',
            'breakfast': 'Breakfast & Instant Food',
            'tea_coffee': 'Tea & Coffee',
            'masala_oil': 'Masalas and Spices',
            'chicken_meat_fish': 'Chicken, Meat and Fish'}


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


class Item(db.Model):
    __tablename__ = "item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    img: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(250), nullable=False)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(256))


class UserItems(db.Model):
    __tablename__ = 'useritems'
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    user_cart: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def home():
    result = db.session.execute(db.select(Item))
    items = result.scalars().all()
    return render_template('index.html', all_items=items, cat_dict=cat_dict)


@app.route('/add', methods=['GET', 'POST'])
@admin_only
def add():
    add_form = AddForm()
    if add_form.validate_on_submit():
        new_item = Item(
            id=add_form.id.data,
            name=add_form.name.data,
            price=add_form.price.data,
            img=add_form.img.data,
            category=add_form.category.data
        )
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('add'))

    return render_template('add.html', form=add_form)


@app.route('/delete', methods=['GET', 'POST'])
@admin_only
def delete():
    del_form = DeleteForm()
    if del_form.validate_on_submit():
        item_to_delete = db.get_or_404(Item, del_form.id.data)
        db.session.delete(item_to_delete)
        db.session.commit()
        return redirect(url_for('delete'))
    return render_template('delete.html', form=del_form)


@app.route('/shop')
def shop():
    result = db.session.execute(db.select(Item))
    items = result.scalars().all()
    return render_template('shop-grid.html', all_items=items, cat_dict=cat_dict)


@app.route('/item/<int:id>')
def view_item(id):
    item = db.get_or_404(Item, id)
    return render_template('shop-details.html', item=item, cat_dict=cat_dict)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/add/<int:item_id>', methods=['POST', 'GET'])
def add_item(item_id):
    cart.append(item_id)
    return redirect(url_for('shopping_cart'))


@app.route('/delete/<int:item_id>', methods=['POST', 'GET'])
def delete_item(item_id):
    cart.delete(item_id)
    return redirect(url_for('shopping_cart'))


@app.route('/cart')
def shopping_cart():
    ids = cart.view()
    print(ids)
    items = db.session.execute(db.select(Item).where(Item.id.in_(ids))).scalars().all()
    print(items)
    return render_template('shopping-cart.html', items=items, qty=cart.items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        # print('Successful')
        result = db.session.execute(db.select(User).where(User.email == login_form.email.data))
        user = result.scalar()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, login_form.password.data):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            cart.items = retrieve_cart(current_user.id)
        return redirect(url_for('home'))
    return render_template('login.html', form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if not form.conditions.data:
            flash('Please accept terms and conditions')
            return redirect(url_for('register'))
        user_check = db.session.execute(db.select(User).where(User.email == form.email.data))
        if user_check:
            flash("User already exists")
            return redirect(url_for('register'))
        if form.password.data != form.repeat_password.data:
            flash('Password does not match')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(name=form.name.data,
                        email=form.email.data,
                        password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/save')
def save_cart():
    if current_user.is_authenticated:
        cart_string = json.dumps(cart.items)
        user_check = db.session.execute(db.select(UserItems).where(UserItems.user_id == current_user.id))
        if user_check:
            saved_cart = db.get_or_404(UserItems, current_user.id)
            saved_cart.user_cart = cart_string
            db.session.commit()
            flash('Cart Saved!')
            return redirect(url_for('shopping_cart'))
        else:
            new_entry = UserItems(
                user_id=current_user.id,
                user_cart=cart_string
            )
            db.session.add(new_entry)
            db.session.commit()
            flash('Cart Saved!')
            return redirect(url_for('shopping_cart'))
    else:
        flash("Please Log-in to save your cart!")
        return redirect(url_for('shopping_cart'))


def retrieve_cart(id):
    user_check = db.session.execute(db.select(UserItems).where(UserItems.user_id == id))
    if user_check:
        saved_json = user_check.scalar()
        if saved_json==None:
            return {}
        else:
            saved_dict = json.loads(saved_json)
            return saved_dict
    else:
        return {}


if __name__ == '__main__':
    app.run(debug=True)
