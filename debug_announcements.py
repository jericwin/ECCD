from db import execute_query

# Check all announcements
anns = execute_query('SELECT a.*, t.full_name as teacher_name FROM announcements a JOIN teachers t ON a.teacher_id = t.id', (), fetch_all=True) or []
print(f"Total announcements: {len(anns)}")
for a in anns:
    print(f"  ID={a['id']}, teacher_id={a['teacher_id']}, teacher={a['teacher_name']}, title={a['title']}")

# Check all learners and their classroom enrollments
learners = execute_query("""
    SELECT l.id, l.full_name, cl.classroom_id, c.teacher_id, c.name as classroom_name
    FROM learners l
    LEFT JOIN classroom_learners cl ON cl.learner_id = l.id
    LEFT JOIN classrooms c ON cl.classroom_id = c.id
""", (), fetch_all=True) or []
print(f"\nLearner enrollments: {len(learners)}")
for l in learners:
    print(f"  learner_id={l['id']}, name={l['full_name']}, classroom={l['classroom_name']}, teacher_id={l['teacher_id']}")

# Check if any learner would match an announcement
print("\n--- Matching check ---")
for l in learners:
    if l['teacher_id']:
        matching = [a for a in anns if a['teacher_id'] == l['teacher_id']]
        if matching:
            print(f"  Learner '{l['full_name']}' WOULD see {len(matching)} announcements from teacher_id={l['teacher_id']}")
        else:
            print(f"  Learner '{l['full_name']}' enrolled with teacher_id={l['teacher_id']} but NO matching announcements")
    else:
        print(f"  Learner '{l['full_name']}' is NOT enrolled in any classroom")
