from flask import request, abort
from app import app


@app.route("/")
@app.route("/index")
def index():
    print(f"index request args: {request.args}")
    return "index"
    # abort(404)

#     pa = """<profile game_version="144" username="MR. BANG" digest="" sid="53219938" rid="559FC7A6561CFAFD47DA04470E84D681B54652FCF30F728F27FB47A2AEF3F2BA" squad_tag="" color="1 1 1 0">
#     <stats kills="0" deaths="0" time_played="64.000000" player_kills="0" teamkills="0" longest_kill_streak="0" targets_destroyed="0" vehicles_destroyed="0" soldiers_healed="0" times_got_healed="0" distance_moved="127.977203" shots_fired="2" throwables_thrown="0" rank_progression="0.000000">
#         <monitor name="kill combo" />
#         <monitor name="death streak" longest_death_streak="0" />
#     </stats>
# </profile>"""

@app.route("/get_profile.php")
def get_profile():
    print(f"get_profile req args: {request.args}")
    # return """<data ok="0" issue="fuck"/>"""  # gives `failed, disconnect, reason=11`
    # return """<data ok="1"/>"""  # gives `failed, disconnect, reason=11`
    pt = """<profile username="MR. BONG" digest="" rid="7ABBB093027BD34020852D8E3684AA01590715B981BB954000DCA04B0E0C1888"/>"""
    # return f"""<data ok="1">{pt}</data>"""  # gives `failed, disconnect, reason=11`
    return f"""<data ok="1">{pt}</data>\n"""  # works!!! the \n terminator is essential


@app.route("/set_profile.php")
def set_profile():
    return "set"
