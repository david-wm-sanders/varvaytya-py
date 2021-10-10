from app import app, db
from app.models import Realm, Account


@app.shell_context_processor
def sh():
    return {"db": db, "Realm": Realm, "Account": Account}


if __name__ == '__main__':
    app.run(debug=True)
