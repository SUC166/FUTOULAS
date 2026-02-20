"""
FUTO Schools and Departments Data (2025/2026)
Sources: futo.edu.ng, legacy.futo.edu.ng/faculties-departments, JUPEB/PG admission lists
"""

# Structure: school_name -> { departments: [...], levels: [...] OR levels_override: {dept: [...]} }
SCHOOL_DATA = {
    "School of Agriculture and Agricultural Technology (SAAT)": {
        "departments": [
            "Agribusiness",
            "Agricultural Economics",
            "Agricultural Extension",
            "Animal Science and Technology",
            "Crop Science and Technology",
            "Fisheries and Aquaculture Technology",
            "Forestry and Wildlife Technology",
            "Soil Science and Technology",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Basic Medical Sciences (SBMS)": {
        "departments": [
            "Human Anatomy",
            "Human Physiology",
        ],
        "levels": ["100", "200", "300"],
    },
    "School of Biological Sciences (SOBS)": {
        "departments": [
            "Biochemistry",
            "Biology",
            "Biotechnology",
            "Forensic Science",
            "Microbiology",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Engineering and Engineering Technology (SEET)": {
        "departments": [
            "Agricultural and Bioresources Engineering",
            "Biomedical Engineering",
            "Chemical Engineering",
            "Civil Engineering",
            "Food Science and Technology",
            "Material and Metallurgical Engineering",
            "Mechanical Engineering",
            "Mechatronic Engineering",
            "Petroleum Engineering",
            "Polymer and Textile Engineering",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Electrical Systems Engineering Technology (SESET)": {
        "departments": [
            "Computer Engineering",
            "Electrical and Electronic Engineering",
            "Electronics Engineering",
            "Mechatronics Engineering",
            "Power Systems Engineering",
            "Telecommunications Engineering",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Environmental Sciences (SOES)": {
        "departments": [
            "Architecture",
            "Building Technology",
            "Environmental Management",
            "Quantity Surveying",
            "Surveying and Geoinformatics",
            "Urban and Regional Planning",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Health Technology (SOHT)": {
        "departments": [
            "Biomedical Technology",
            "Dental Technology",
            "Environmental Health Science",
            "Optometry",
            "Prosthetics and Orthotics",
            "Public Health Technology",
        ],
        "levels_override": {
            "Optometry": ["100", "200", "300", "400", "500", "600"],
            "Biomedical Technology": ["100", "200", "300", "400"],
            "Dental Technology": ["100", "200", "300", "400"],
            "Environmental Health Science": ["100", "200", "300", "400"],
            "Prosthetics and Orthotics": ["100", "200", "300", "400"],
            "Public Health Technology": ["100", "200", "300", "400"],
        },
        "levels": ["100", "200", "300", "400"],
    },
    "School of Information and Communication Technology (SICT)": {
        "departments": [
            "Computer Science",
            "Cyber Security",
            "Information Technology",
            "Software Engineering",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Logistics and Innovation Technology (SLIT)": {
        "departments": [
            "Financial Management Technology",
            "Management Technology",
            "Maritime Management Technology",
            "Project Management Technology",
            "Transport Management Technology",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Physical Sciences (SOPS)": {
        "departments": [
            "Chemistry",
            "Geology",
            "Mathematics",
            "Physics",
            "Science Laboratory Technology",
            "Statistics",
        ],
        "levels": ["100", "200", "300", "400"],
    },
    "College of Medicine (COMED)": {
        "departments": [
            "Medicine and Surgery (MBBS)",
        ],
        "levels": ["100", "200", "300", "400", "500", "600"],
    },
}


def get_schools():
    return sorted(SCHOOL_DATA.keys())


def get_departments(school):
    if school in SCHOOL_DATA:
        return SCHOOL_DATA[school]["departments"]
    return []


def get_levels(school, department):
    if school not in SCHOOL_DATA:
        return []
    data = SCHOOL_DATA[school]
    overrides = data.get("levels_override", {})
    if department in overrides:
        return overrides[department]
    return data.get("levels", ["100", "200", "300", "400"])
