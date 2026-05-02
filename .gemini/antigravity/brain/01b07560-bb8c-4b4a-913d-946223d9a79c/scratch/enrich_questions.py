import json
import os

existing_path = r"c:\Users\User\Documents\HabitCore\backend\app\services\reflection_engine\data\questions_v2.json"
new_questions_raw = [
{"id":61,"category":"awareness","depth":1,"question":"What subtle emotion did I notice today?"},
{"id":62,"category":"awareness","depth":2,"question":"When did I feel mentally scattered?"},
{"id":63,"category":"awareness","depth":2,"question":"When did I feel calm without effort?"},
{"id":64,"category":"awareness","depth":1,"question":"What moment changed my energy today?"},
{"id":65,"category":"awareness","depth":2,"question":"What did I notice about my mood patterns?"},
{"id":66,"category":"awareness","depth":2,"question":"When did I feel tension in my body?"},
{"id":67,"category":"awareness","depth":1,"question":"What was I most aware of today?"},
{"id":68,"category":"awareness","depth":2,"question":"What situation made me uncomfortable?"},
{"id":69,"category":"awareness","depth":3,"question":"What emotion did I try to suppress?"},
{"id":70,"category":"awareness","depth":2,"question":"What surprised me about my reactions?"},

{"id":71,"category":"thoughts","depth":1,"question":"What thought distracted me most today?"},
{"id":72,"category":"thoughts","depth":2,"question":"What belief limited my actions today?"},
{"id":73,"category":"thoughts","depth":2,"question":"What assumption turned out to be wrong?"},
{"id":74,"category":"thoughts","depth":1,"question":"What thought created doubt?"},
{"id":75,"category":"thoughts","depth":2,"question":"What thought did I question today?"},
{"id":76,"category":"thoughts","depth":1,"question":"What thought kept repeating?"},
{"id":77,"category":"thoughts","depth":2,"question":"What internal dialogue did I notice?"},
{"id":78,"category":"thoughts","depth":2,"question":"What thought triggered emotion?"},
{"id":79,"category":"thoughts","depth":1,"question":"What thought slowed me down?"},
{"id":80,"category":"thoughts","depth":2,"question":"What thought helped me act?"},

{"id":81,"category":"cognitive_distortions","depth":2,"question":"Did I jump to conclusions today?"},
{"id":82,"category":"cognitive_distortions","depth":2,"question":"Did I assume things would go wrong?"},
{"id":83,"category":"cognitive_distortions","depth":2,"question":"Did I focus only on negatives?"},
{"id":84,"category":"cognitive_distortions","depth":2,"question":"Did I ignore evidence that contradicted me?"},
{"id":85,"category":"cognitive_distortions","depth":2,"question":"Did I blame myself unfairly?"},
{"id":86,"category":"cognitive_distortions","depth":2,"question":"Did I think others had negative intent?"},
{"id":87,"category":"cognitive_distortions","depth":2,"question":"Did I treat feelings as facts?"},
{"id":88,"category":"cognitive_distortions","depth":2,"question":"Did I expect perfection?"},
{"id":89,"category":"cognitive_distortions","depth":2,"question":"Did I exaggerate mistakes?"},
{"id":90,"category":"cognitive_distortions","depth":2,"question":"Did I minimize successes?"},

{"id":91,"category":"behavior","depth":1,"question":"What task did I delay the most?"},
{"id":92,"category":"behavior","depth":2,"question":"What behavior felt automatic?"},
{"id":93,"category":"behavior","depth":2,"question":"Where did I act without thinking?"},
{"id":94,"category":"behavior","depth":1,"question":"What action took effort?"},
{"id":95,"category":"behavior","depth":2,"question":"What behavior helped me progress?"},
{"id":96,"category":"behavior","depth":2,"question":"What behavior held me back?"},
{"id":97,"category":"behavior","depth":1,"question":"What did I finish completely?"},
{"id":98,"category":"behavior","depth":2,"question":"Where did I lose momentum?"},
{"id":99,"category":"behavior","depth":1,"question":"What did I start but not finish?"},
{"id":100,"category":"behavior","depth":2,"question":"Where did I act out of habit?"},

{"id":101,"category":"avoidance","depth":2,"question":"What task did I postpone?"},
{"id":102,"category":"avoidance","depth":3,"question":"What fear caused me to avoid action?"},
{"id":103,"category":"avoidance","depth":2,"question":"What discomfort did I run from?"},
{"id":104,"category":"avoidance","depth":2,"question":"What excuse did I use?"},
{"id":105,"category":"avoidance","depth":3,"question":"What feeling was I unwilling to face?"},
{"id":106,"category":"avoidance","depth":2,"question":"What did I replace effort with?"},
{"id":107,"category":"avoidance","depth":2,"question":"What was the cost of avoiding?"},
{"id":108,"category":"avoidance","depth":2,"question":"What did I delay unnecessarily?"},
{"id":109,"category":"avoidance","depth":2,"question":"What challenge did I sidestep?"},
{"id":110,"category":"avoidance","depth":2,"question":"Where did I escape into comfort?"},

{"id":111,"category":"emotional_regulation","depth":1,"question":"What emotion lasted the longest?"},
{"id":112,"category":"emotional_regulation","depth":2,"question":"Did I overreact to anything?"},
{"id":113,"category":"emotional_regulation","depth":2,"question":"What helped me regain control?"},
{"id":114,"category":"emotional_regulation","depth":2,"question":"Did I let emotions guide decisions?"},
{"id":115,"category":"emotional_regulation","depth":1,"question":"What stabilized my mood?"},
{"id":116,"category":"emotional_regulation","depth":2,"question":"Did I stay calm under pressure?"},
{"id":117,"category":"emotional_regulation","depth":2,"question":"What triggered frustration?"},
{"id":118,"category":"emotional_regulation","depth":2,"question":"Did I notice emotional patterns?"},
{"id":119,"category":"emotional_regulation","depth":2,"question":"Did I respond thoughtfully?"},
{"id":120,"category":"emotional_regulation","depth":2,"question":"Did I let something go?"},

{"id":121,"category":"control_responsibility","depth":1,"question":"What could I control today?"},
{"id":122,"category":"control_responsibility","depth":2,"question":"What did I try to control unnecessarily?"},
{"id":123,"category":"control_responsibility","depth":2,"question":"Where did I take ownership?"},
{"id":124,"category":"control_responsibility","depth":2,"question":"Where did I avoid responsibility?"},
{"id":125,"category":"control_responsibility","depth":1,"question":"What decision did I make?"},
{"id":126,"category":"control_responsibility","depth":2,"question":"What did I delay deciding?"},
{"id":127,"category":"control_responsibility","depth":2,"question":"Where did I feel stuck?"},
{"id":128,"category":"control_responsibility","depth":2,"question":"What action was in my control?"},
{"id":129,"category":"control_responsibility","depth":2,"question":"Where did I give away control?"},
{"id":130,"category":"control_responsibility","depth":2,"question":"Did I act intentionally?"},

{"id":131,"category":"identity","depth":2,"question":"What identity did I express today?"},
{"id":132,"category":"identity","depth":2,"question":"Did I act with self-respect?"},
{"id":133,"category":"identity","depth":3,"question":"Where did I go against my values?"},
{"id":134,"category":"identity","depth":2,"question":"What version of myself showed up?"},
{"id":135,"category":"identity","depth":2,"question":"Did I act authentically?"},
{"id":136,"category":"identity","depth":2,"question":"What belief about myself influenced me?"},
{"id":137,"category":"identity","depth":3,"question":"Did I betray my standards?"},
{"id":138,"category":"identity","depth":2,"question":"What identity am I reinforcing?"},
{"id":139,"category":"identity","depth":2,"question":"Did I act with integrity?"},
{"id":140,"category":"identity","depth":2,"question":"What kind of person was I today?"},

{"id":141,"category":"discipline_focus","depth":1,"question":"What distracted me most?"},
{"id":142,"category":"discipline_focus","depth":2,"question":"Where did I lose focus?"},
{"id":143,"category":"discipline_focus","depth":2,"question":"What helped me stay focused?"},
{"id":144,"category":"discipline_focus","depth":1,"question":"Did I manage my time well?"},
{"id":145,"category":"discipline_focus","depth":2,"question":"What interrupted my work?"},
{"id":146,"category":"discipline_focus","depth":2,"question":"Did I control my attention?"},
{"id":147,"category":"discipline_focus","depth":1,"question":"What task required discipline?"},
{"id":148,"category":"discipline_focus","depth":2,"question":"Where did I lose discipline?"},
{"id":149,"category":"discipline_focus","depth":2,"question":"What improved my focus?"},
{"id":150,"category":"discipline_focus","depth":2,"question":"Did I avoid hard tasks?"},

{"id":151,"category":"progress_reflection","depth":1,"question":"What did I improve today?"},
{"id":152,"category":"progress_reflection","depth":2,"question":"What lesson did I learn?"},
{"id":153,"category":"progress_reflection","depth":1,"question":"What went well today?"},
{"id":154,"category":"progress_reflection","depth":2,"question":"What could I do better?"},
{"id":155,"category":"progress_reflection","depth":1,"question":"What am I proud of?"},
{"id":156,"category":"progress_reflection","depth":2,"question":"What pattern is forming?"},
{"id":157,"category":"progress_reflection","depth":2,"question":"Am I moving forward?"},
{"id":158,"category":"progress_reflection","depth":1,"question":"What small win did I have?"},
{"id":159,"category":"progress_reflection","depth":2,"question":"What needs adjustment?"},
{"id":160,"category":"progress_reflection","depth":2,"question":"What will I change tomorrow?"}
]

with open(existing_path, "r") as f:
    existing = json.load(f)

# Enrichment Mapping
TRIGGER_MAP = {
    "awareness": ["mood_variability"],
    "thoughts": ["negative_thought"],
    "cognitive_distortions": ["negative_thought", "distortion"],
    "behavior": [],
    "avoidance": ["avoidance_high"],
    "emotional_regulation": ["emotional_spike"],
    "control_responsibility": ["low_integrity"],
    "identity": ["low_integrity"],
    "discipline_focus": ["low_focus"],
    "progress_reflection": []
}

for q in new_questions_raw:
    category = q["category"]
    depth = q["depth"]
    
    enriched = {
        "category": category if category != "cognitive_distortions" else "thoughts",
        "subcategory": category + "_general",
        "depth": depth,
        "intensity": 0.3 + (depth * 0.2),
        "trigger_types": TRIGGER_MAP.get(category, []),
        "priority": 0.5,
        "question": q["question"]
    }
    existing.append(enriched)

with open(existing_path, "w") as f:
    json.dump(existing, f, indent=2)

print(f"Successfully enriched and appended {len(new_questions_raw)} questions.")
