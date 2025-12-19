from flask import Flask, render_template, request, jsonify  
from collections import defaultdict  
import pyttsx3  
import threading  
import time   
app = Flask(__name__)   
tts_engine = pyttsx3.init()  
tts_engine.setProperty('rate', 150)  
tts_engine.setProperty('volume', 0.6)  
current_start = None  
current_goal = None    
class CampusGraph:  
    def _init_(self):  
        self.graph = defaultdict(set)     
    def connect(self, a, b):  
        self.graph[a].add(b)  
        self.graph[b].add(a)    
g = CampusGraph()   
g.connect("Main Gate", "MRD Block")  
g.connect("MRD Block", "Placement Central")  
g.connect("Placement Central", "OAT")  
g.connect("OAT", "BE Block Turn")  
g.connect("BE Block Turn", "BE Block")  
g.connect("Main Gate", "Second Left After Parking")  
g.connect("Second Left After Parking", "Immediate Right Into GJB")  
g.connect("Immediate Right Into GJB", "GJB Corridor Straight")  
g.connect("GJB Corridor Straight", "Admission Office")  
g.connect("Main Gate", "Straight Path to GJB")  
g.connect("Straight Path to GJB", "GJB Entrance Left")  
g.connect("GJB Entrance Left", "GJB")  
g.connect("Main Gate", "Second Left (Canteen Route)")  
g.connect("Second Left (Canteen Route)", "First Seating Lot")  
g.connect("First Seating Lot", "Second Seating Lot")  
g.connect("Second Seating Lot", "GJB Canteen Entrance")  
g.connect("GJB Canteen Entrance", "GJB Canteen")  
g.connect("Main Gate", "Second Left Footpath")  
g.connect("Second Left Footpath", "F Block")  
g.connect("Main Gate", "First Left Parking")  
g.connect("First Left Parking", "Upper Parking")  
g.connect("Upper Parking", "Lower Parking")  
g.connect("Lower Parking", "Sitting Area")  
g.connect("Sitting Area", "F Block")  
g.connect("Main Gate", "GJB Library")  
g.connect("GJB Library", "GJB Canteen")  
g.connect("GJB", "GJB Canteen")  
g.connect("GJB", "Admission Office")  
g.connect("F Block", "BE Block")  
g.connect("F Block", "Boys Hostel")  
g.connect("BE Block", "Boys Hostel")  
g.connect("Boys Hostel", "SKM Bakery and MealStation")  
g.connect("SKM Bakery and MealStation", "SKM")  
g.connect("F Block", "SKM Bakery and MealStation")   
major_places = [  
    "Main Gate",  
    "GJB",  
    "GJB Canteen",  
    "OAT",  
    "BE Block",  
    "F Block",  
    "Admission Office",  
    "GJB Library",  
    "Boys Hostel",  
    "SKM Bakery and MealStation"  
]  
def clean_text_for_speech(text):  
    """Clean HTML tags and format text for better speech output"""   
    clean_text = text.replace('<br><br>', '. ').replace('<br>', '. ')  
    clean_text = clean_text.replace('<strong>', '').replace('</strong>', '')  
    clean_text = clean_text.replace('&', 'and') 
    clean_text = clean_text.replace('→',' ')  
    clean_text = ' '.join(clean_text.split())    
    if len(clean_text) > 400:  
        clean_text = clean_text[:400] + "..."   
    return clean_text.strip()  
def speak_directions(start, goal, instructions):  
    """Function to speak directions using pyttsx3 in a separate thread"""  
    def _speak():  
        try:    
            intro = f"Directions from {start} to {goal}. "  
            clean_instructions = clean_text_for_speech(instructions)  
            full_text = intro + clean_instructions  
            tts_engine.setProperty('rate', 140)  
            tts_engine.setProperty('volume', 0.9)   
            tts_engine.say(full_text)  
            tts_engine.runAndWait()  
        except Exception as e:  
            print(f"TTS Error: {e}")    
    thread = threading.Thread(target=_speak)  
    thread.daemon = True  
    thread.start()  
@app.route("/")  
def index():  
    return render_template("index.html", locations=sorted(major_places))  
@app.route("/find_path", methods=["POST"])  
def find_path():  
    global current_start, current_goal  
    data = request.json  
    start = data.get("start")  
    goal = data.get("goal")  
    audio_enabled = data.get("audio_enabled", False)   
    current_start = start  
    current_goal = goal  
    if start == goal:  
        result = {"route": "You're already here!"}  
        if audio_enabled:  
            speak_directions(start, goal, "You are already at your destination!")  
        return jsonify(result)    
    def has_path(cur, tgt, visited=None):  
        if visited is None:   
            visited = set()  
        if cur == tgt:   
            return True  
        if cur in visited:   
            return False  
        visited.add(cur)  
        return any(has_path(n, tgt, visited) for n in g.graph[cur])   
    if not has_path(start, goal):  
        return jsonify({"error": "No route yet"}), 400  
    instructions = ""   
    if start == "Main Gate" and goal == "GJB":
        instructions = ( "Enter Main Gate → go <strong>straight</strong><br><br>""Ignore the second left (canteen path)<br><br>""Keep walking → big entrance on your <strong>left</strong><br><br>""That’s <strong>GJB main building</strong> — you’ve arrived!")
    elif start == "Main Gate" and goal == "GJB Canteen":
        instructions = ( "Enter Main Gate<br><br>""Take <strong>first left</strong> after parking lot<br><br>""Pass first seating lot<br>"" entarnace Opposite to <strong>second seating lot</strong> → enter there<br><br>""Straight → take <strong>second right</strong><br><br>""Welcome to <strong>GJB Canteen</strong>")
    elif start=="GJB Canteen" and goal=="Main Gate":
        instructions=("come out of GJB Canteen<br><br>""walk out of GJB towards seating lot<br><br>" "take left→ Go striaght<br><br>""take right as you reach the end of footpath<br><br>""GO striaght you will be at main gate</strong><br><br>")
    elif start=="GJB" and goal=="Main Gate":
        instructions=("come out of GJB <br><br>" "Take right turn and go striaght till you reach main gate<br><br>" "You've arrived at main gate</strong><br><br>")
    elif start == "Main Gate" and goal == "OAT":
        instructions = ("Go straight <br><br>"" pass MRD Block (white buliding on your right)<br><br>" " OAT on your right </strong><br><br>")
    elif start=="OAT" and goal== "Main Gate":
        instructions=("Come out of OAT<br><br>""Take left→Go striaght for 500m<br><br> " "you have reached main gate</strong><br><br>")  
    elif start == "Main Gate" and goal == "BE Block":
        instructions = ("Go Straight <br><br>" " you will see white building(mrd block),placement central and oat on your way <br><br>"" after OAT <br><br>""first right → walk 50m <br><br>" " BE Block on left </strong><br><br>")
    elif start=="BE Block" and goal=="Main Gate":
        instructions=("Come out of BE Block <br><br>""take right towards main road<br><br>""Take left after you reach end of road<br><br>""Go straight for 650m<br><br>""You've reached main gate</strong><br><br>")
    elif start == "Main Gate" and goal == "F Block":
        instructions = ("Go straight  <br><br>""Take first left after parking lot  <br><br>"" long footpath deadend →Go straight  <br><br>"" Reach  F Block(red bricked building) buliding </strong><br><br>")
    elif start=="F Block" and goal=="Main Gate":
        instructions=("Come out of F Block<br><br>""Go straight till end of the pathway<br><br>""Take right as at end of pathway<br><br>""Go straight for 300m<br><br>""you have reached your destination</strong><br><br>")
    elif start== "Main Gate" and goal== "Boys Hostel":
        instructions =("Go straight <br><br>""Take first left after parking lot  <br><br>" " long footpath deadend →Go straight  <br><br>" "take right→ Walk 100m forwad you will see skm  <br><br>""take right → Go straight  <br><br>" "boys hostel is on your left side </strong> <br><br>")
    elif start=="Boys Hostel" and goal=="Main Gate":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""Take right and go straight<br><br>""You have reached main gate</strong><br><br>")
    elif start== "Main Gate" and goal== "SKM Bakery and MealStation":
        instructions =("Go straight <br><br>" "Take first left after parking lot  <br><br>"" long footpath deadend→Go straight  <br><br>""take right→ Go straight <br><br>""You've arrived at SKM</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="Main Gate":
        instructions=("come out of SKM <br><br>""Go straight → take left <br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""Take right and go straight<br><br>""You have reached main gate</strong><br><br>")
    elif start== "Main Gate" and goal== "GJB Library":
        instructions =("Go Straight <br><br>" "Take the right upper footpath <br><br>" "Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walking for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="GJB Library" and goal=="Main Gate":
        instructions=("come out of GJB Library → take left<br><br>""walk towards quadrangle then take left towards open area<br><br>""Take right after reaching open area<br><br>""go straight and take left towards statue<br><br>""walk till statue and then take right down the footpath<br><br>""Go straight <br><br> ""you are at main gate</strong><br><br>")
    elif start=="Main Gate" and goal=="Admission Office":
        instructions=("Go straight<br><br>""take first left after parking lot <br><br> ""Take immediate right into the GJB <br><br>""ignore stairs left to you and go straight<br><br>"  "Admission block is on your left side</strong><br><br>")
    elif start=="Admission Office" and goal=="Main Gate":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""Take left walk staright for 10m and immediate right <br><br>""Go straight<br><br>""You've reached your destination</strong><br><br>")
    elif start == "F Block" and goal == "BE Block":
        instructions = ( "Exit F Block → take footpath <strong>towards Main Gate</strong><br><br>" "Reach main road → <strong>turn left</strong><br><br>" "Walk straight → pass Placement Central → pass OAT (on right)<br><br>""Take the <strong>next right</strong> after OAT<br><br>""Walk ~50 meters → <strong>BE Block</strong> on your <strong>left</strong><br><br>""You’ve arrived!")
    elif start=="GJB" and goal=="OAT":
        instructions=("Come out of GJB<br><br>""get down the stairs on left and go right<br><br>""you are at OAT</strong><br><br>")
    elif start=="GJB" and goal=="BE Block":
        instructions=("Come out of GJB<br><br>""Take left stairs<br><br>""Take left and cross the road<br><br>""Take right after OAT<br><br>""Walk straight BE Block is on your left side</strong><br><br>")
    elif start == "BE Block" and goal == "F Block":
        instructions = ( "Exit BE Block → go towards main road<br><br>""At junction → turn <strong>left</strong><br><br>""Walk straight → pass OAT & Placement Central (on left)<br><br>""Look for long footpath going inside → take it<br><br>""Keep walking → reach <strong>F Block</strong>")
    elif start == "GJB" and goal == "GJB Canteen":
        instructions = ( "Exit GJB→ take right as you come out of GJB<br><br>""Go straight → take first right<br><br>""Walk straight → till second seating lot (on left)<br><br>""take right at second seating lot<br><br>""Go straight → at second right  you are at GJB Canteen</strong><br><br>")
    elif start=="GJB" and goal=="Admission Office":
        instructions=("Come to the GJB entrance<br><br>""If you are facing GJB take left stairs<br><br>""Walk for 100m Admission Office is on your right</strong><br><br>")
    elif start=="GJB" and goal=="GJB Library":
        instructions=("Come out of GJB take right stairs<br><br>""Go straight and take left when you reach end of footpath<br><br>""Go straight and take upper footpath on your left <br><br> ""Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walikng for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="GJB" and goal=="Boys Hostel":
        instructions=("Come out of GJB Take right stairs<br><br>""Go straight and take first right<br><br>""Take the long pathway till F Block<br><br>""take right→ Walk 100m forwad you will see skm  <br><br>""take right → Go straight  <br><br>" "boys hostel is on your left side </strong> <br><br>")
    elif start=="GJB" and goal=="SKM Bakery and MealStation":
        instructions=("Come out of GJB Take right stairs<br><br> "" Go straight and take first right<br><br>"" long footpath →Go straight  <br><br>""take right→ Go straight <br><br>""You've arrived at SKM</strong><br><br>")
    elif start=="GJB Canteen" and goal=="GJB":
        instructions=("come out of GJB Canteen towards seating lot<br><br>""Take left as you reach seating lot<br><br>""go straight to the main road and take left<br><br>""GJB is at your left side</strong><br><br>")
    elif start=="GJB Canteen" and goal=="OAT":
        instructions=("come out of GJB Canteen towards seating lot<br><br>""Take left as you reach seating lot<br><br>""go straight to the main road and cross the road<br><br>""after crossing take left walk straight<br><br>""OAT is on your left side</strong><br><br>")
    elif start=="GJB Canteen" and goal=="BE Block":
        instructions=("come out of GJB Canteen towards seating lot<br><br>""Take left as you reach seating lot<br><br>""go straight to the main road and cross the road<br><br>""after crossing take left walk straight<br><br>""Take first right after OAT<br><br>""walk for 100m and BE Block is on your left side</strong><br><br>")
    elif start=="GJB Canteen" and goal=="Admission Office":
        instructions=("come out of GJB Canteen towards seating lot<br><br>""Take left as you reach seating lot<br><br>""GO straight till few steps behind end of footpath<br><br>""take left into GJB <br><br>""go straight igronring the stairs left to you <br><br>""Admission Office is on your left side</strong><br><br>")
    elif start=="GJB Canteen" and goal=="GJB Library":
        instructions=("take stairs inside GJB Canteen which is near secound counter beside fire extinguisher <br><br>""go to next floor come out of CLIC hallway<br><br>""go to opposite side of quadrangle<br><br> ""go straight for 200m GJB Library is on your right side</strong><br><br>")
    elif start=="GJB Canteen" and goal=="Boys Hostel":
        instructions=("come out of GJB Canteen towards seating lot<br><br>""take right and reach F Block (red brick building)<br><br>""take right→ Walk 100m forwad you will see skm  <br><br>""take right → Go straight  <br><br>" "boys hostel is on your left side </strong> <br><br>")
    elif start=="GJB Canteen" and goal=="SKM Bakery and MealStation":
        instructions=("come out of GJB Canteen towards seating lot<br><br>""take right and reach F Block (red brick building)<br><br>""take right→ Go straight <br><br>""You've arrived at SKM</strong><br><br>")
    elif start=="OAT" and goal=="GJB":
        instructions=("Come out of the OAT the building infront of you is the GJB building<br><br>""Cross the road <br><br>""you've arrived at your destination</strong><br><br>")
    elif start=="OAT" and goal=="GJB Canteen":
        instructions=("Come out of OAT<br><br>""Take left and go forward till you reach upper footpath then take right and cross<br><br>""take footpath till the second seating lot<br><br>""the entrance opposite to the second seating lot is GJB Canteen entrance <br><br>""go inside and the second right is the canteen</strong><br><br>")
    elif start=="OAT" and goal=="BE Block":
        intsructions=("Come out of OAT<br><br>""take right and take right after OAT<br><br>""walk for 100m BE Block is on your left side</strong><br><br>")
    elif start=="OAT" and goal=="Adimission Office":
        instructions=("Come out of the OAT and take left<br><br>""when you reach upper footpath Cross the road <br><br>""Take few steps forward you will find a entrance at your right<br><br>""Take that right and enter the building <br><br>""go straight ignoring the stairs left to you<br><br>""walk 50m Admission Office is at your left side</strong><br><br>")
    elif start=="OAT" and goal=="GJB Library":
       instructions=("Come out of the OAT and take left<br><br>""GO straight<br><br>"" take upper footpath which is at your left<br><br> ""Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walikng for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="OAT" and goal=="Boys Hostel":
        instructions=("Come out of OAT and take left<br><br>""go straight till you reach upper footpath<br><br>""take right and cross road<br><br>""Go straight→  long footpath deadend    <br><br>" "take right→ Walk 100m forwad you will see skm  <br><br>""take right → Go straight  <br><br>" "boys hostel is on your left side </strong> <br><br>")
    elif start=="OAT" and goal=="SKM Bakery and MealStation":
        instructions=("Come out of OAT and take left<br><br>""go straight till you reach upper footpath<br><br>""take right and cross road<br><br>"" Go straight→  long footpath deadend    <br><br>""take right→ Go straight <br><br>""You've arrived at SKM</strong><br><br>")
    elif start=="BE Block" and goal=="GJB":
        instructions=("Come out of BE Block<br><br>""take right till main road then cross road<br><br>""take left go 50m and take stairs on your right <br><br>""you are at GJB</strong><br><br>")
    elif start=="BE Block" and goal=="GJB Canteen":
        instructions=("Come out of BE Block<br><br>""take right till you reach main road then take left<br><br>""go straight till upper footpath<br><br>""then take right and cross<br><br>""take footpath till the second seating lot<br><br>""the entrance opposite to the second seating lot is GJB Canteen entrance <br><br>""go inside and the second right is the canteen</strong><br><br>")
    elif start=="BE Block" and goal=="OAT":
        instructions=("Come out of BE Block<br><br>""take right till you reach main road<br><br>""take left again walk 50m<br><br>""OAT is at your left side</strong><br><br>")
    elif start=="BE Block" and goal=="Admission Office":
        instructions=("Come out of BE Block and take right till you reach main road<br><br>""take left and go straight till you reach upper footpath<br><br>""take right and cross road<br><br>""Take few steps forward you will find a entrance at your right<br><br>""Take that right and enter the building <br><br>""go straight ignoring the stairs left to you<br><br>""walk 50m Admission Office is at your left side</strong><br><br>")
    elif start=="BE Block" and goal=="GJB Library":
        instructions=("Come out of BE Block and take right till you reach main road<br><br>""take left and go straight till you reach upper footpath<br><br>"" take upper footpath which is at your left<br><br> ""Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walikng for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="BE Block" and goal=="Boys Hostel":
        instructions=("Come out of BE Block and take right till you reach main road<br><br>""take left and go straight till you reach upper footpath<br><br>""take right and cross road<br><br>"" long footpath →Go straight  <br><br>" "take right→ Walk 100m forwad you will see skm  <br><br>""take right → Go straight  <br><br>" "boys hostel is on your left side </strong> <br><br>")
    elif start=="BE Block" and goal=="SKM Bakery and MealStation":
        instructions=("Come out of BE Block and take right till you reach main road<br><br>""take left and go straight till you reach upper footpath<br><br>""take right and cross road<br><br>"" long footpath →Go straight  <br><br>" "take right→ Go straight <br><br>""You've arrived at SKM</strong><br><br>")
    elif start=="Admission Office" and goal=="GJB":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take left walk few steps forward and again take left<br><br>""go straight till stairs and take stairs<br><br>""you are at your destination</stong><br><br>")
    elif start=="Admission Office" and goal=="GJB Canteen":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take right walk till second seating lot<br><br>""the entrance opposite to the second seating lot is GJB Canteen entrance <br><br>""go inside and the second right is the canteen</strong><br><br>")
    elif start=="Admission Office" and goal=="OAT":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take left and cross the road<br><br>""take left and go straight for 200m<br><br>""OAT is at your right side</strong><br><br>")
    elif start=="Admission Office" and goal=="BE Block":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take left and cross the road<br><br>""take left and go straight till end<br><br>""take first right after OAT go straight BE Block is at your left side</strong><br><br>")
    elif start=="Admission Office" and goal=="GJB Library":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take left and cross the road<br><br>"" take upper footpath in front on by taking right<br><br> ""Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walikng for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="Admission Office" and goal=="Boys Hostel":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take right till the F block(red bricked building)<br><br>"" footpath →Go straight  <br><br>" "take right→ Walk 100m forwad you will see skm  <br><br>""take right → Go straight  <br><br>" "boys hostel is on your left side </strong> <br><br>")
    elif start=="Admission Office" and goal=="SKM Bakery and MealStation":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take right till the F block(red bricked building)<br><br>"" footpath →Go straight  <br><br>""take right→ Go straight <br><br>""You've arrived at SKM</strong><br><br>")
    elif start=="Boys Hostel" and goal=="GJB":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""take left go straight till stairs and then take stairs on your left<br><br>""You've arrived at GJB</strong><br><br>")
    elif start=="Boys Hostel" and goal=="GJB Canteen":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight → take left<br><br>""go straight till first seating lot on your way take left and enter the entrance<br><br>""go inside and the second right is the canteen</strong><br><br>")
    elif start=="Boys Hostel" and goal=="OAT":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""cross road take left <br><br>""Go straight for 200m you have arrived at OAT</strong><br><br>")
    elif start=="Boys Hostel" and goal=="BE Block":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""cross road take left <br><br>""Go straight till end and take first right after OAT<br><br>""go staight for 150m BE Block is on your left</strong><br><br>")
    elif start=="Boys Hostel" and goal=="Admission Office":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight → take left<br><br> ""GO straight till few steps behind end of footpath<br><br>""take left into GJB <br><br>""go straight igronring the stairs left to you <br><br>""Admission Office is on your left side</strong><br><br>")
    elif start=="Boys Hostel" and goal=="GJB Library":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""cross road  take upper footpath in front on by taking right<br><br> ""Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walikng for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="Boys Hostel" and goal=="SKM Bakery and MealStation":
        instructions=("Come out of Boys Hostel <br><br>""Can't you see skm on your right side you want directions for this???</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="GJB":
        instructions=("come out of SKM <br><br>""Go straight → take left <br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""Take left and go straight<br><br>""you've reached GJB</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="GJB Canteen":
        instructions=("come out of SKM <br><br>""Go straight → take left <br><br>""go straight till first seating lot on your way take left and enter the entrance<br><br>""go inside and the second right is the canteen</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="OAT":
        instructions=("Come out of skm  Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""cross road take left<br><br> ""Go straight  → OAT is on your right side</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="BE Block":
        instructions=("Come out of skm  Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""cross road take left <br><br>""Go straight till end and take first right after OAT<br><br>""go staight for 150m BE Block is on your left</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="Admission Office":
        instructions=("Come out of skm  Go straight → take left<br><br>""Go straight till few steps behind end of footpath<br><br>""take left into GJB <br><br>""go straight igronring the stairs left to you <br><br>""Admission Office is on your left side</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="GJB Library":
        instructions=("Come out of skm  Go straight → take left<br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""cross road  take upper footpath in front  by taking right<br><br> ""Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walking for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="Boys Hostel":
        instructions=("come out of SKM turn towards skm<br><br>""Can't you see boys hotel at your right side you want directions for this??</strong><br><br>")
    elif start=="GJB Library" and goal=="GJB":
        instructions=("Come  out of GJB library take left towards quadrangle<br><br>""after reaching the other side take left towards open area<br><br>""after reaching open area take right go straight and take left toward statue<br><br>""walk towards statue and then take right go down the foothpath<br><br>""take right and cross the road <br><br>""after crossing take right go down the foothpath<br><br>""the entrance at you left is GJB</strong><br><br>")
    elif start=="GJB Library" and goal=="GJB Canteen":
        instructions=("come out of GJB Library take left and cross quadrangle<br><br>""take the entrance to CLIC hallway and take stairs<br><br>""go one floor downstairs come out of the stairs <br><br>""you ar einside the GJB Canteen</strong><br><br>")
    elif start=="GJB Library" and goal=="OAT":
        instructions=("Come  out of GJB library take left towards quadrangle<br><br>""after reaching the other side take left towards open area<br><br>""after reaching open area take right go straight and take left toward statue<br><br>""walk towards statue and then take right go down the foothpath<br><br>""Then take right side footpath next to upper footpath go straight <br><br>""OAT is on your right side</strong><br><br>")
    elif start=="GJB Library" and goal=="BE Block":
        instructions=("Come  out of GJB library take left towards quadrangle<br><br>""after reaching the other side take left towards open area<br><br>""after reaching open area take right go straight and take left toward statue<br><br>""walk towards statue and then take right go down the foothpath<br><br>""Then take right side footpath next to upper footpath go straight till end of foothpath<br><br>""take first right after OAT<br><br>""go straight BE Block is  on your left side</strong><br><br>")
    elif start=="GJB Library" and goal=="Admission Office":
        instructions=("Come  out of GJB library take left towards quadrangle<br><br>""after reaching the other side take left towards open area<br><br>""after reaching open area take right go straight and take left toward statue<br><br>""walk towards statue and then take right go down the foothpath<br><br>""take right and cross the road <br><br>""take few steps forward you will see entrance at your right<br><br>""take right into the building ,go straight<br><br>""lgnore the stairs on your left side go straight <br><br>""Admission Office is at your left side</strong><br><br>")
    elif start=="GJB Library" and goal=="Boys Hostel":
        instructions=("come out of GJB Library take left and cross the quadrangle<br><br>""take entrance to CLIC hallway and take right at end of hallway<br><br>""go straight till you reach stairs <br><br>""go one floor down stairs and come out stairs and take left and come out of building<br><br>""take right as you come out of building <br><br>""take right after you reach F Block and go straight and take right as you reach skm <br><br>""take few steps forward you have arrived at Boys Hostel</strong><br><br>")
    elif start=="GJB Library" and goal=="SKM Bakery and MealStation":
        instructions=("come out of GJB Library take left and cross the quadrangle<br><br>""take entrance to CLIC hallway and take right at end of hallway<br><br>""go straight till you reach stairs <br><br>""go one floor down stairs and come out stairs and take left and come out of building<br><br>""take right as you come out of building <br><br>""take right after you reach F Block and go straight <br><br>""you are arrived at SKM</strong><br><br>")
    elif start=="GJB" and goal=="F Block":
        instructions=("come out of GJB take right using stairs<br><br>""go straight 100m and take right<br><br>""Go straight→  long footpath deadend  <br><br>"" Reach  F Block(red bricked building) buliding </strong><br><br>")
    elif start=="GJB Canteen" and goal=="F Block":
        instructions=("come out of GJB Canteen towards seating lot<br><br>""take right and reach F Block (red brick building)</strong><br><br>")
    elif start=="OAT" and goal=="F Block":
        instructions=("Come out of OAT and take left<br><br>""go straight till you reach upper footpath<br><br>""take right and cross road<br><br>"" Go straight→  long footpath deadend  <br><br>""F Block (red brick building)is infront of you</strong><br><br>")
    elif start=="BE Block" and goal=="F Block":
        instructions=("Come out of BE Block and take right till you reach main road<br><br>""take left and go straight till you reach upper footpath<br><br>""take right and cross road<br><br>"" Go straight→  long footpath deadend <br><br>" "F Block (red brick building)is infront of you</strong> <br><br>")
    elif start=="Admission Office" and goal=="F Block":
        instructions=("Come out of admission office<br><br>""take right and come out of GJB building<br><br>""take right and walk straight till the F block(red bricked building)</strong><br><br>")
    elif start=="GJB Library" and goal=="F Block":
        instructions=("come out of GJB Library take left and cross the quadrangle<br><br>""take entrance to CLIC hallway and take right at end of hallway<br><br>""go straight till you reach stairs <br><br>""go one floor down stairs and come out stairs and take left and come out of building<br><br>""take right as you come out of building <br><br>""go straight you have arrived at F Block</strong><br><br>")
    elif start=="Boys Hostel" and goal=="F Block":
        instructions=("Come right towards SKM after coming out of Boys Hostel<br><br>""take left and Go straight<br><br>""F Block (red brick building)is on your right</strong><br><br>")
    elif start=="SKM Bakery and MealStation" and goal=="F Block":
        instructions=("come out of skm can you see red brick building??<br><br>""that is the F Block you want me to give direction for that??</strong><br><br>")
    elif start=="F Block" and goal=="GJB":
        instructions=("come out of F Block go straight till the end of footpath<br><br>""take left after reaching main road <br><br>""go straight take stairs left to you <br><br>""You are at GJB</strong><br><br>")
    elif start=="F Block" and goal=="GJB Canteen":
        instructions=("Come out of F Block go straight till the first seating lot<br><br>""take left at seating lot into building<br><br>""Go straight and take second right <br><br>""you are at the GJB Canteen</strong><br><br>")
    elif start=="F Block" and goal=="OAT":
        instructions=("come out of F Block go straight till the end of footpath <br><br>""cross the road after reaching the main road<br><br>""take left and go straight walk for 250m <br><br>""you are at OAT</strong><br><br>")
    elif start=="F Block" and goal=="BE Block":
        instructions=("come out of F Block go straight till the end of footpath <br><br>""cross the road after reaching the main road<br><br>""take left and go straight till the end of footpath<br><br>""take first right after OAT walk straight<br><br>""BE Block is at your left side</strong><br><br>")
    elif start=="F Block" and goal=="Admission Office":
        instructions=("Come out of F block go straight till few steps behind end of footpath<br><br>""take left at the entrance left to you <br><br>""go inside the building lgnore the stairs left to you and walk forward<br><br>""you are at Admssion Office</strong><br><br>")
    elif start=="F Block" and goal=="GJB Library":
        instructions=("Come out of F Block <br><br> ""walk straight for 500m till end of pathway(footpath)<br><br>""cross road  take upper footpath in front on by taking right<br><br> ""Go straight  → Take left as you reach the statue <br><br>" "Going straight will lead you to hornbill so take right <br><br>" "Go straight and take left to quadrangle <br><br>" "After walikng for 150m take right →Go straight <br><br>" "GJB Library is on your right side</strong><br><br>")
    elif start=="F Block" and goal=="Boys Hostel":
        instructions=("Come out of F Block<br><br>""take left→ Walk 100m forwad you will see skm  <br><br>""take right → Go straight  <br><br>" "boys hostel is on your left side </strong> <br><br>")
    elif start=="F Block" and goal=="SKM Bakery and MealStation":
        instructions=("Come out of F Block<br><br>""take left→ Go straight <br><br>""You've arrived at SKM</strong><br><br>")  
    else:
        instructions = f"Path exists! Just follow the main campus road from {start} to {goal}."  
    if audio_enabled:  
        speak_directions(start, goal, instructions)      
    return jsonify({  
        "route": f"{start} to {goal}",  
        "instructions": instructions,  
        "audio_enabled": audio_enabled  
    })   
@app.route("/stop_speech", methods=["POST"])  
def stop_speech():  
    """Endpoint to stop current speech"""  
    try:  
        tts_engine.stop()  
        return jsonify({"status": "Speech stopped"})  
    except:  
        return jsonify({"status": "No speech to stop"}), 400   
if __name__ == "__main__":  
    app.run(debug=True, host='0.0.0.0', port=5000)