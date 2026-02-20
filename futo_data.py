"""
FUTO Schools and Departments Data (2025/2026)
Source: https://legacy.futo.edu.ng/faculties-departments/
SPGS and Directorate of General Studies excluded as requested.
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
    "School of Basic Medical Science (SBMS)": {
        "departments": [
            "Human Anatomy",
            "Human Physiology",
        ],
        "levels": ["100", "200", "300"],
    },
    "School of Biological Science (SOBS)": {
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
            "Agricultural and Bio Resources Engineering",
            "Biomedical Engineering",
            "Chemical Engineering",
            "Civil Engineering",
            "Food Science and Technology",
            "Material and Metallurgical Engineering",
            "Mechanical Engineering",
            "Petroleum Engineering",
            "Polymer and Textile Engineering",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Electrical Systems and Engineering Technology (SESET)": {
        "departments": [
            "Computer Engineering",
            "Electrical (Power Systems) Engineering",
            "Electrical and Electronic Engineering",
            "Electronics Engineering",
            "Mechatronics Engineering",
            "Telecommunications Engineering",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Environmental Science (SOES)": {
        "departments": [
            "Architecture",
            "Building Technology",
            "Environmental Management",
            "Environmental Management and Evaluation",
            "Quantity Surveying",
            "Surveying and Geoinformatics",
            "Urban and Regional Planning",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Health Technology (SOHT)": {
        "departments": [
            "Dental Technology",
            "Environmental Health Science",
            "Optometry",
            "Prosthetics and Orthotics",
            "Public Health Technology",
        ],
        "levels_override": {
            "Optometry": ["100", "200", "300", "400", "500", "600"],
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
            "Entrepreneurship and Innovation",
            "Logistics and Transport Technology",
            "Maritime Technology and Logistics",
            "Project Management Technology",
            "Supply Chain Management",
        ],
        "levels": ["100", "200", "300", "400", "500"],
    },
    "School of Physical Science (SOPS)": {
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
