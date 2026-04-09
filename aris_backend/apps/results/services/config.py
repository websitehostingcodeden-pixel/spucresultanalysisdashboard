# Column name variations that exist in the wild
COLUMN_MAPPINGS = {
    "reg_no": [
        "reg no",
        "reg_no",
        "register number",
        "registration number",
        "roll no",
        "roll number",
        "enrollment number",
        "student id",
        "admn no",
        "adm no",
    ],
    "grand_total": [
        "grand total",
        "total",
        "gt",
        "total marks",
        "grand_total",
        "overall total",
        "final total",
        "aggregate",
    ],
    "percentage": [
        "percentage",
        "%",
        "percent",
        "pct",
        "percentage %",
        "perc",
    ],
    "student_name": [
        "name",
        "student name",
        "student_name",
        "full name",
        "fullname",
    ],
}

# Result classification thresholds
RESULT_CLASSIFICATION = {
    "DISTINCTION": 85,
    "FIRST_CLASS": 60,
    "SECOND_CLASS": 50,
    "PASS": 35,
    "FAIL": 0,
}

# Valid result classes
VALID_RESULT_CLASSES = list(RESULT_CLASSIFICATION.keys()) + ["INCOMPLETE"]

# List of known subject-like columns to exclude
RESERVED_COLUMNS = {
    # Registration identifiers (ONLY use reg_no, ignore others)
    "reg no",
    "reg_no",
    "register number",
    "registration number",
    "roll no",
    "roll number",
    "enrollment number",
    "enrollment no",
    "student id",
    "admn no",
    "adm no",
    "sats no",
    "sat no",
    
    # Metadata
    "name",
    "student name",
    "student_name",
    "full name",
    "fullname",
    "sr no",
    "sr. no",
    "serial",
    
    # Stream/Section
    "stream",
    "section",
    "sect",
    "section code",
    "k/h/s",  # Language choice - not a subject
    
    # All types of totals (CRITICAL - don't misclassify as subjects)
    "grand total",
    "grand_total",
    "total",
    "gt",
    "total marks",
    "overall total",
    "final total",
    "aggregate",
    "part-1 total",
    "part1 total",
    "part 1 total",
    "part-2 total",
    "part2 total",
    "part 2 total",
    "part1_total",
    "part2_total",
    "theory total",
    "practical total",
    
    # Scoring/Classification (don't misclassify)
    "percentage",
    "%",
    "percent",
    "pct",
    "percentage %",
    "perc",
    "result",
    "result class",
    "result_class",
    "class",
    "grade",
    "division",
    "rank",
    
    # Metadata that might appear
    "remarks",
    "status",
    "notes",
    "comments",
    "date",
    "timestamp",
}

# Keywords that if found in column name, exclude from subjects
EXCLUDE_KEYWORDS = [
    "total",
    "grand",
    "result",
    "class",
    "percentage",
    "percent",
    "grade",
    "rank",
    "remarks",
    "notes",
    "comments",
    "date",
    "time",
]

# Additional identifiers to ignore (warn if used instead of reg_no)
OTHER_IDENTIFIERS = [
    "sats no",
    "enrollment number",
    "enrollment no",
]

# Numeric validation: If > 80% of values are numeric, it's likely a subject
NUMERIC_THRESHOLD = 0.8
