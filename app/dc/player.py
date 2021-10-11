import dataclasses
import xml.etree.ElementTree as XmlET

from .exc import XmlLoadKeyError, XmlLoadValueError
from .person import PersonDc
from .profile import ProfileDc


@dataclasses.dataclass
class PlayerDc:
    hash_: int
    rid: str
    person: PersonDc
    profile: ProfileDc

    @classmethod
    def from_element(cls, element: XmlET.Element):
        x = element.attrib
        try:
            hash_ = int(x.get("hash"))
            rid = x.get("rid")
            # todo: more validation
        except KeyError as e:
            print(f"Player attribute key error: {e}")
            raise XmlLoadKeyError() from e
        except ValueError as e:
            print(f"Player attribute value error: {e}")
            raise XmlLoadValueError() from e
        except Exception as e:
            print(f"Player attribute load failed: {e}")
            raise

        person_elem = element.find("person")
        person = PersonDc.from_element(person_elem)

        profile_elem = element.find("profile")
        profile = ProfileDc.from_element(profile_elem)

        return cls(hash_=hash_, rid=rid, person=person, profile=profile)
