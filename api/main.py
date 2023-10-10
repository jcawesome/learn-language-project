import os
import sys

from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from pymongo.errors import OperationFailure
from pymongo.mongo_client import MongoClient
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL

# Definition of MongoDB Database
uri = os.environ.get('MONGODB_CONNECTION')
# Create a new client and connect to the server
client = MongoClient(uri)

# use a database named "LANG_DB"
db = client.LANG_DB

# use a collection named "LANG_COLLECTION"
my_collection = db["LANG_COLLECTION"]

# Definition of Flask WebApp front-end
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class AddWordForm(FlaskForm):
    language = SelectField('Language', choices=["Cantonese", "Filipino"], validators=[DataRequired()])
    word_english = StringField("Word in English", validators=[DataRequired()])
    word_alt = StringField("Word to Learn (i.e. Cantonese in Jyutping)", validators=[DataRequired()])
    definition = StringField("Definition of the Word", validators=[DataRequired()])
    audio_uri = StringField("Audio", validators=[DataRequired(), URL()])
    submit = SubmitField('Submit')


# define all Flask routes below
@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_word():
    form = AddWordForm()
    if form.validate_on_submit():
        add_word_json = [
            {"language": f"{form.language.data}",
             "word_english": f"{form.word_english.data}",
             "word_alt": f"{form.word_alt.data}",
             "definition": f"{form.definition.data}",
             "audio_uri": f"{form.audio_uri.data}"
             }
        ]
        print(add_word_json)
        try:
            result = my_collection.insert_many(add_word_json)
        except OperationFailure:
            print(
                "An authentication error was received. Are you sure your database user is authorized to perform write operations?")
            sys.exit(1)
        else:
            inserted_count = len(result.inserted_ids)
            print("I inserted %x documents." % inserted_count)
            print("\n")
        return redirect(url_for('dictionary'))
    print('Invalid')
    return render_template('add.html', form=form)


@app.route('/dictionary')
def dictionary():
    data = my_collection.find()

    column_values = []
    for idx, document in enumerate(data):
        if idx == 0:
            # Add column names as first row
            columns = [column for column in document.keys() if column != '_id']
            column_values.append(list(columns))

        # Exclude the _id column
        columns = [column for column in document.keys() if column != '_id']
        column_values.append([document[column] for column in columns])

    # Print the list of column values
    # for row in column_values:
    #     print(row)

    return render_template('dictionary.html', words=column_values)


if __name__ == '__main__':
    app.run(debug=True)
