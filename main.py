from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
db.init_app(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[float] = mapped_column(Float)

    def __repr__(self):
        return f"<Book({self.id} , {self.title} , {self.author} , {self.rating})>"


with app.app_context():
    db.create_all()



@app.route('/')
def home():

    all_books = db.session.execute(db.select(Book).order_by(Book.id)).scalars().all()
    return  render_template("index.html", all_books=all_books)


@app.route("/add", methods=['GET','POST'])
def add():
    if request.method == 'POST':
        new_book = Book(
            title = request.form.get("book_name"),
            author = request.form.get("book_author"),
            rating = request.form.get("book_rating")
        )

        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("add.html")


@app.route("/edit-rating/<int:curr_book_id>", methods=['GET', 'POST'])
def edit_rating(curr_book_id):
    if request.method == 'GET':
        curr_book = db.get_or_404(Book, curr_book_id)
        return render_template("edit_rating.html", book=curr_book)

    if request.method == 'POST':
        new_rating = float(request.form.get("new_rating"))

        book_to_update = db.get_or_404(Book, curr_book_id)
        book_to_update.rating = new_rating
        db.session.commit()
        return redirect(url_for('home'))


@app.route("/delete-book", methods=['POST', 'GET'])
def delete_book():
    curr_book_id = request.args.get("curr_book_id")
    book_to_delete = db.get_or_404(Book, curr_book_id)
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)

