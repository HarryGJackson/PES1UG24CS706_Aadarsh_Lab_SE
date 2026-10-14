"""Student academic grading management module."""

import hashlib
import os
import secrets

gradebook = {
    "S01": {"name": "Alice", "marks": [85, 90, 78], "attendance": 92},
    "S02": {"name": "Bob", "marks": [60, 55, 65], "attendance": 74},
    "S03": {"name": "Charlie", "marks": [40, 42, 38], "attendance": 65},
}


def add_grade(student_id, mark, grade_list=None):
    """Add a mark for a student and log it; return True on success."""
    if grade_list is None:
        grade_list = []
    if student_id not in gradebook or mark < 0:
        return False
    gradebook[student_id]["marks"].append(mark)
    grade_list.append(f"Recorded score {mark} for student id {student_id}")
    return True


def record_attendance(student_id, present_days):
    """Add present days to a student's attendance; return True on success."""
    try:
        gradebook[student_id]["attendance"] += present_days
    except KeyError:
        print("Unknown student id:", student_id)
        return False
    return True


def check_passing_status(student_id, pass_threshold=50.0):
    """Return True if the student's average mark meets the threshold."""
    if gradebook.get(student_id) is None:
        return False
    marks = gradebook[student_id]["marks"]
    avg = sum(marks) / len(marks)
    return avg >= pass_threshold


def compute_weighted_gpa(student_id, scale=20.0):
    """Return the student's GPA as average mark divided by scale."""
    marks = gradebook[student_id]["marks"]
    avg_score = sum(marks) / len(marks)
    return avg_score / scale


def generate_student_hash(student_id):
    """Return a SHA-256 hex digest of the student id."""
    return hashlib.sha256(student_id.encode()).hexdigest()


def generate_registration_pin():
    """Return a cryptographically secure 4-digit registration PIN."""
    return 1000 + secrets.randbelow(9000)


def export_grade_sheet(filename="grade_sheet.txt"):
    """Write the gradebook to a text file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(gradebook))
    print("Grade sheet exported to:", filename)


def main():
    """Run a sample grading workflow."""
    portal_token = os.environ.get("PORTAL_TOKEN", "")
    add_grade("S01", 95)
    record_attendance("S02", 2)
    print("Is S01 passing:", check_passing_status("S01"))
    print("Calculated GPA:", compute_weighted_gpa("S01", 20.0))
    print("Student Hash:", generate_student_hash("S01"))
    print("Registration PIN:", generate_registration_pin())
    export_grade_sheet()
    print("Portal token configured:", bool(portal_token))


if __name__ == "__main__":
    main()
