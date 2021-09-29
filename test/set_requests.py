import pathlib
import requests

ENDPOINT = "http://127.0.0.1:5000/set_profile.php"
REALM = "INCURSION"
REALM_DIGEST = "17E615D232B76E060567D3327F2D31758F9CCF8ACE0319E1AD49C626F766CA5B"

SCRIPT_DIR = pathlib.Path(__file__).parent
TEST_XML = SCRIPT_DIR / "test_set_profile.xml"

data = TEST_XML.read_text(encoding="utf-8")

r = requests.post(url=f"{ENDPOINT}?realm={REALM}&realm_digest={REALM_DIGEST}",
                  data={f"{data}": ""})
print(r.text)
