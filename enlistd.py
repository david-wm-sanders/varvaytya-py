from app import app, db
from app.models import Realm, Player

@app.shell_context_processor
def sh():
    return {"db": db, "Realm": Realm, "Player": Player}


if __name__ == '__main__':
    app.run(debug=True)
