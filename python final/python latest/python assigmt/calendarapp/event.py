import base64 ,datetime ,os

DATA_FILE = "events.txt"  

def ensure_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            pass

def expand_occurrences(event: "Event"):
    base_date = datetime.date.fromisoformat(event.date)
    if event.cycle <= 0:
        return [base_date]

    days = []
    if event.loop == -1:  
        max_date = base_date + datetime.timedelta(days=365)
        d = base_date
        while d <= max_date:
            days.append(d)
            d += datetime.timedelta(days=event.cycle)
    else:
        for i in range(event.loop):
            days.append(base_date + datetime.timedelta(days=i*event.cycle))
    return days

def b64_encode(s: str) -> str:
    return base64.b64encode(s.encode("utf-8")).decode("ascii")

def b64_decode(s: str) -> str:
    try:
        return base64.b64decode(s.encode("ascii")).decode("utf-8")
    except Exception:
        return ""


class Event:
    def __init__(self, title, date_str, start_time="", end_time="", 
                 category="Other", invitees="", notes="", uid=None,
                 cycle=0, loop=1):
        self.uid = uid or f"ev{int(datetime.datetime.now().timestamp()*1000)}"
        self.title = title
        self.date = date_str
        self.start = start_time
        self.end = end_time
        self.category = category
        self.invitees = invitees
        self.notes = notes

        
        self.cycle = int(cycle) 
        self.loop = int(loop)  
    

    def to_dict(self):
        return {
            "uid": self.uid,
            "title": self.title,
            "date": self.date,
            "start": self.start,
            "end": self.end,
            "category": self.category,
            "invitees": self.invitees,
            "notes": self.notes,
            "cycle": self.cycle,
            "loop": self.loop
        }

    @staticmethod
    def from_dict(d):
        return Event(
            d["title"], d["date"], d.get("start",""), d.get("end",""),
            d.get("category","Other"), d.get("invitees",""), d.get("notes",""),
            d.get("uid"), d.get("cycle",0), d.get("loop",1)
        )

    def to_line(self) -> str:
        parts = [
            b64_encode(self.uid),
            b64_encode(self.title),
            b64_encode(self.date),
            b64_encode(self.start),
            b64_encode(self.end),
            b64_encode(self.category),
            b64_encode(self.invitees),
            b64_encode(self.notes),
            b64_encode(str(self.cycle)),
            b64_encode(str(self.loop))
        ]
        return "|||".join(parts)

    @staticmethod
    def from_line(line: str):
        parts = line.rstrip("\n").split("|||")
        if len(parts) != 10:  
            return None
        try:
            uid = b64_decode(parts[0])
            title = b64_decode(parts[1])
            date = b64_decode(parts[2])
            start = b64_decode(parts[3])
            end = b64_decode(parts[4])
            category = b64_decode(parts[5])
            invitees = b64_decode(parts[6])
            notes = b64_decode(parts[7])
            cycle = int(b64_decode(parts[8]) or 0)
            loop = int(b64_decode(parts[9]) or 1)
            return Event(title, date, start, end, category, invitees, notes, uid=uid, cycle=cycle, loop=loop)
        except Exception:
            return None

   