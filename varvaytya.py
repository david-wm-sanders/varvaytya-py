from app import app, db
from app.models import World, ItemGroup, ItemDef, Realm, Player, Account


@app.shell_context_processor
def sh():
    return {"db": db,
            "World": World, "ItemGroup": ItemGroup, "ItemDef": ItemDef,
            "Realm": Realm, "Player": Player, "Account": Account}


if __name__ == '__main__':
    app.run(debug=True)
