# 🗺️ Location-Based Demo Story

## Setup: Multiple Clinic Locations

### Metro PT Clinic Network
1. **Metro PT Downtown** (1.2 miles from Maria)
   - Dr. Sarah Johnson (T001) - The departing therapist
   
2. **Metro PT Main Clinic** (2-3.5 miles from Maria)
   - Dr. Emily Ross (P001) - 2.0 miles
   - Dr. Michael Lee (P004) - 3.5 miles
   
3. **Metro PT Westside** (12.5 miles from Maria)
   - Dr. James Wilson (P003) - TOO FAR!

---

## 📋 Demo Scenario

### Situation
**Dr. Sarah Johnson (T001)** at **Metro PT Downtown** calls in sick.

She has 3 appointments today:
1. **Maria Rodriguez** (PAT001) - Prefers Main Clinic, max 5 miles
2. **John Davis** (PAT002) - Prefers Downtown, max 3 miles  
3. **Susan Lee** (PAT003) - Prefers Westside, max 15 miles

---

## 🎯 Expected Matching Results

### Patient 1: Maria Rodriguez
- **Preferred**: Metro PT Main Clinic
- **Max Distance**: 5.0 miles
- **Preferred Gender**: Female

**Candidates:**
- ✅ **Dr. Emily Ross** (P001) - Main Clinic, 2.0 miles, Female - **PERFECT MATCH!**
- ✅ Dr. Michael Lee (P004) - Main Clinic, 3.5 miles, Male - Good
- ❌ Dr. James Wilson (P003) - Westside, 12.5 miles - **TOO FAR!**

**Winner**: Dr. Emily Ross (P001)
- ✅ Right location (Main Clinic)
- ✅ Within distance (2.0 < 5.0 miles)
- ✅ Gender preference match (Female)
- ✅ Good availability (60% capacity)

---

### Patient 2: John Davis
- **Preferred**: Metro PT Downtown
- **Max Distance**: 3.0 miles
- **Prior Provider**: T001 (continuity important)

**Candidates:**
- ✅ Dr. Emily Ross (P001) - Main Clinic, 2.0 miles - **CLOSE ENOUGH**
- ❌ Dr. Michael Lee (P004) - Main Clinic, 3.5 miles - **TOO FAR!** (3.5 > 3.0)
- ❌ Dr. James Wilson (P003) - Westside, 12.5 miles - **WAY TOO FAR!**

**Winner**: Dr. Emily Ross (P001)
- ✅ Within distance constraint (2.0 < 3.0 miles)
- ✅ Has worked with T001 patients before (continuity)

---

### Patient 3: Susan Lee
- **Preferred**: Metro PT Westside
- **Max Distance**: 15.0 miles
- **Flexible** on location

**Candidates:**
- ✅ Dr. Emily Ross (P001) - Main Clinic, 2.0 miles - Far from preferred
- ✅ Dr. James Wilson (P003) - **Westside, 12.5 miles** - **PREFERRED LOCATION!**
- ✅ Dr. Michael Lee (P004) - Main Clinic, 3.5 miles - Far from preferred

**Winner**: Dr. James Wilson (P003)
- ✅ Matches preferred location (Westside)
- ✅ Within distance (12.5 < 15.0 miles)
- ✅ Low capacity (45% - plenty of availability)
- ✅ Sports Medicine specialist

---

## 💡 Demo Highlights

### 1. Location-Based Filtering
```
System filters out Dr. James Wilson (P003) for Maria and John
because he's at Westside (12.5 miles), which is:
- Beyond Maria's 5-mile limit
- Beyond John's 3-mile limit
```

### 2. Patient Preference Matching
```
Maria prefers "Main Clinic" → Gets Dr. Emily Ross at Main Clinic ✅
John prefers "Downtown" → Gets closest option (Main Clinic, 2 mi) ✅
Susan prefers "Westside" → Gets Dr. James Wilson at Westside ✅
```

### 3. Distance Constraints
```
Max Distance Rules:
- Maria: 5.0 miles → Can see P001 (2.0 mi) ✅, P004 (3.5 mi) ✅
- John:  3.0 miles → Can see P001 (2.0 mi) ✅ only
- Susan: 15.0 miles → Can see everyone ✅
```

### 4. Smart Scoring
```
For Maria:
- P001 (Emily Ross):  85/100 points
  + Location match (Main Clinic): +30 pts
  + Distance (2.0 mi): +25 pts
  + Gender match (Female): +20 pts
  + Availability (60%): +10 pts

- P004 (Michael Lee): 52/100 points
  + Location match (Main Clinic): +30 pts
  + Distance (3.5 mi): +15 pts
  + Gender mismatch: +0 pts
  + Availability (88% - busy): +7 pts
```

---

## 🧪 Test Commands

### Test Location Filtering
```bash
# In UI: http://localhost:8501
therapist departed T001

# Watch the system:
1. Identify 3 affected patients
2. Filter candidates by location/distance
3. Rank by preferences
4. Match optimally
```

### Test API Endpoints
```bash
# See all locations
curl http://localhost:8000/api/providers | jq '.[].primary_location'

# See patient preferences
curl http://localhost:8000/api/patients | jq '.[] | {name, preferred_location, max_distance_miles}'

# Filter providers by location
curl http://localhost:8000/api/providers | jq '.[] | select(.primary_location == "Metro PT Main Clinic")'
```

---

## 📊 Expected Outcome

| Patient | Departed From | Reassigned To | Location | Distance | Match Quality |
|---------|---------------|---------------|----------|----------|---------------|
| Maria | T001 (Downtown) | **P001 (Emily Ross)** | Main Clinic | 2.0 mi | ⭐⭐⭐⭐⭐ Excellent |
| John | T001 (Downtown) | **P001 (Emily Ross)** | Main Clinic | 2.0 mi | ⭐⭐⭐⭐ Good |
| Susan | T001 (Downtown) | **P003 (James Wilson)** | **Westside** | 12.5 mi | ⭐⭐⭐⭐⭐ Preferred! |

### Why This Demo Works Well

1. **Shows Location Filtering** ✅
   - P003 eliminated for Maria and John (too far)
   - P003 preferred for Susan (matches her location preference)

2. **Shows Distance Constraints** ✅
   - John's 3-mile limit eliminates P004
   - Susan's 15-mile limit allows Westside option

3. **Shows Preference Matching** ✅
   - Maria gets female provider at preferred location
   - Susan gets provider at her preferred Westside location

4. **Shows Smart Capacity Distribution** ✅
   - Dr. Emily Ross (60% capacity) gets 2 patients
   - Dr. James Wilson (45% capacity) gets 1 patient
   - Dr. Michael Lee (88% capacity) gets none (too busy)

5. **Realistic Scenario** ✅
   - Multi-location clinic network
   - Different patient preferences
   - Distance-based filtering
   - Optimal redistribution

---

## 🎬 Demo Script

**You say:** "Dr. Sarah Johnson at our Downtown location called in sick. She has 3 patients today."

**System does:**
1. Identifies 3 affected appointments across different patient types
2. Filters providers by distance constraints
3. Matches based on location preferences
4. Considers gender preferences and capacity
5. Optimally distributes patients

**Result:**
- 2 patients go to Main Clinic (Emily Ross) - good capacity fit
- 1 patient goes to Westside (James Wilson) - her preferred location!
- All patients stay within their distance limits
- Preferences are honored where possible

**Impact:**
- ✅ 3 appointments rescheduled automatically
- ✅ Location preferences considered
- ✅ Distance constraints enforced
- ✅ 10 minutes of manual work → 30 seconds automated

