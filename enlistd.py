from app import app, db
from app.models import Realm, BasicAccount


@app.shell_context_processor
def sh():
    return {"db": db, "Realm": Realm, "Account": BasicAccount}


if __name__ == '__main__':
    app.run(debug=True)
