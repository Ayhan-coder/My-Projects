import os
from fpdf import FPDF

class RecruiterGuidePDF(FPDF):
    def __init__(self, use_unicode=False):
        super().__init__()
        self.use_unicode = use_unicode

    def header(self):
        if self.page_no() > 1:
            font_family = "ArialFont" if self.use_unicode else "helvetica"
            self.set_font(font_family, "", 9)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, self.clean_txt("Recruiter Guide: My Projects Portfolio"), align="R")
            self.ln(12)

    def footer(self):
        self.set_y(-15)
        font_family = "ArialFont" if self.use_unicode else "helvetica"
        self.set_font(font_family, "", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def clean_txt(self, text):
        if not self.use_unicode:
            # Fallback replacements for latin-1 core fonts
            text = text.replace("\u0130", "I") # Turkish Dotted I -> I
            text = text.replace("\u0131", "i") # Turkish dotless i -> i
            text = text.replace("ü", "u").replace("Ü", "U")
            text = text.replace("ğ", "g").replace("Ğ", "G")
            text = text.replace("ş", "s").replace("Ş", "S")
            text = text.replace("ç", "c").replace("Ç", "C")
            text = text.replace("ö", "o").replace("Ö", "O")
        return text

def create_guide():
    # Detect fonts
    font_dir = r"C:\Windows\Fonts"
    arial_path = os.path.join(font_dir, "arial.ttf")
    arial_bold_path = os.path.join(font_dir, "arialbd.ttf")
    courier_path = os.path.join(font_dir, "cour.ttf")
    courier_bold_path = os.path.join(font_dir, "courbd.ttf")
    
    use_unicode = all(os.path.exists(p) for p in [arial_path, arial_bold_path, courier_path, courier_bold_path])
    
    pdf = RecruiterGuidePDF(use_unicode=use_unicode)
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    if use_unicode:
        pdf.add_font("ArialFont", "", arial_path)
        pdf.add_font("ArialFont", "B", arial_bold_path)
        pdf.add_font("CourierFont", "", courier_path)
        pdf.add_font("CourierFont", "B", courier_bold_path)
        main_font = "ArialFont"
        code_font = "CourierFont"
    else:
        main_font = "helvetica"
        code_font = "courier"
        print("Warning: TrueType fonts not found. Using core fonts and replacing Turkish characters.")
        
    # ---------------- PAGE 1: TITLE & TOC & FAST PATH ----------------
    pdf.add_page()
    
    # Title
    pdf.set_font(main_font, "B", 24)
    pdf.set_text_color(26, 82, 118) # Deep Blue
    pdf.cell(0, 15, pdf.clean_txt("Recruiter Guide: My Projects Portfolio"), new_x="LMARGIN", new_y="NEXT", align="L")
    
    # Author & Date
    pdf.set_font(main_font, "B", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, pdf.clean_txt("Ali Ayhan Günder"), new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.set_font(main_font, "", 11)
    pdf.cell(0, 8, "June 28, 2026", new_x="LMARGIN", new_y="NEXT", align="L")
    pdf.ln(5)
    
    # Intro
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, 6, pdf.clean_txt("This document is a quick tour of the repository and where to find the most relevant work."))
    pdf.ln(2)
    
    # Repo Root
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, pdf.clean_txt("Repository root: "))
    pdf.set_font(code_font, "B", 11)
    pdf.write(6, "My-Projects/")
    pdf.ln(10)
    
    # Table of Contents Header
    pdf.set_font(main_font, "B", 14)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    # Table of Contents Rows
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    
    toc_items = [
        ("1 Fast path (25 minutes)", "1"),
        ("2 How this repo is organized", "2"),
        ("  2.1 Main folders and what they contain", "2"),
        ("3 How to review quickly (what to look for)", "3"),
        ("  3.1 Code-first projects", "3"),
        ("  3.2 Report-first projects", "3"),
        ("4 Optional: running the highlight project (GENFIT)", "3"),
        ("5 Contact", "3")
    ]
    
    for item, page in toc_items:
        # Calculate dots
        dots_count = 80 - len(item)
        dots = " ." * (dots_count // 2)
        pdf.cell(140, 6, pdf.clean_txt(item), align="L")
        pdf.cell(10, 6, dots, align="R")
        pdf.cell(20, 6, page, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)
    
    # Section 1: Fast path
    pdf.set_font(main_font, "B", 14)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "1 Fast path (25 minutes)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, 6, "If you only have a short amount of time, start with:")
    pdf.ln(3)
    
    # Item 1
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "1. GENFIT (team full-stack SWE project): ")
    pdf.set_font(main_font, "", 11)
    pdf.write(6, "a fitness-themed platform built with documented setup.\n")
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "   Folder: ")
    pdf.set_font(code_font, "", 10)
    pdf.write(6, pdf.clean_txt("GENFIT_SWE_PROJECT_CMPE451_FINAL_VERS\u0130ON/\n"))
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "   Start here: ")
    pdf.set_font(code_font, "", 10)
    pdf.write(6, ".../bounswe2025group2-main/bounswe2025group2-main/README.md\n\n")
    
    # Item 2
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "2. Operating Systems (C / performance): ")
    pdf.set_font(main_font, "", 11)
    pdf.write(6, "systems programming projects.\n")
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "   Folder: ")
    pdf.set_font(code_font, "", 10)
    pdf.write(6, "OPERATING_SYSTEM_PROJECTS/\n\n")
    
    # Item 3
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "3. Statistics / analytics (Python): ")
    pdf.set_font(main_font, "", 11)
    pdf.write(6, "data analysis scripts and reports.\n")
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "   Folder: ")
    pdf.set_font(code_font, "", 10)
    pdf.write(6, "STATISTICS_PROJECTS/\n")
    
    # ---------------- PAGE 2: ORGANIZATION ----------------
    pdf.add_page()
    
    pdf.set_font(main_font, "B", 14)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "2 How this repo is organized", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, 6, "Projects are grouped mostly by course or topic. The top-level README.md acts as a clickable index.")
    pdf.ln(4)
    
    pdf.set_font(main_font, "B", 12)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "2.1 Main folders and what they contain", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    folders_data = [
        ("Software engineering (team)", [
            ("GENFIT_SWE_PROJECT_CMPE451_FINAL_VERS\u0130ON/", "Final iteration of our team project (full-stack)."),
            ("GENFIT_SWE_PROJECT_V1_CMPE352/", "Earlier iteration of our team project (full-stack).")
        ]),
        ("Systems & low-level", [
            ("OPERATING_SYSTEM_PROJECTS/", "C projects; some are best built/run on Linux/WSL (CMPE322)."),
            ("COMPUTER_ORGANIZATION_LABS/", "Course labs (CMPE344)."),
            ("System Programming_PROJECTS_C,C++,ASSEMBLY/", "C/C++/assembly low-level programming exercises.")
        ]),
        ("Distributed systems", [
            ("DISTRIBUTED_SYSTEMS_CMPE476/", "Sockets and RPC systems programming coursework.")
        ]),
        ("Algorithms & data structures", [
            ("ANALYSIS_OF_ALGORITHMS_PROJECTS/", "Course projects on design & complexity analysis (CMPE300)."),
            ("DATA_STRUCTURES&ALGOR\u0130TMS/", "Fundamental structures and algorithms implementations.")
        ]),
        ("Data", [
            ("DBMS_SQL_PROJECTS/", "SQL-focused database design and query projects."),
            ("STATISTICS_PROJECTS/", "Python statistics and data analytics scripts with reports.")
        ]),
        ("System simulation & modeling", [
            ("SYSTEM_SIMULATION_IE306_projects/", "Discrete event simulations (inventory, clinic, ferry)."),
            ("OPERATION_RESEARCH_PROJECTS_IE310/", "Optimization models and linear programming exercises.")
        ]),
        ("Computational science & simulations", [
            ("PARTICLE_BASED_SIMULATIONS_CMPE_49G/", "Simulations of physical particle movements and interactions.")
        ]),
        ("Signal processing", [
            ("SIGNAL&SYSTEMS_CMPE362_Projects/", "MATLAB and Python signal processing homeworks.")
        ]),
        ("AI & healthcare", [
            ("AI_IN_HEALTCARE_CMPE49T/", "Deep learning applications and reports for healthcare data.")
        ]),
        ("Languages / coursework", [
            ("JAVA_OOP_CMPE160/", "Java OOP projects (Ant Colony Optimization, Map Navigation)."),
            ("PYTHON_PROJECTS_CMPE150/", "Introductory Python projects and tasks."),
            ("PRINCIPLES_OF_PROGRAMMING_LANGUAGES_CMPE 260-PROLOG/", "Logic programming, interpreters and parsing in Prolog.")
        ]),
        ("HCI / UI", [
            ("HUMAN_COMPUTER_INTERACT\u0130ON_PROJECTS_CMPE496/", "UI/UX user studies and interface mockups.")
        ]),
        ("Entrepreneurship / business", [
            ("Entrepreneurship_PROJECT&STARTUP_AD432/", "Pitch decks, business plans, and startup analysis.")
        ])
    ]
    
    for section_title, items in folders_data:
        pdf.set_font(main_font, "B", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 6, pdf.clean_txt(f"* {section_title}"), new_x="LMARGIN", new_y="NEXT")
        
        for folder, desc in items:
            pdf.set_font(main_font, "", 10)
            pdf.set_text_color(33, 33, 33)
            pdf.write(5, "  - ")
            pdf.set_font(code_font, "B", 9.5)
            pdf.write(5, pdf.clean_txt(folder))
            pdf.set_font(main_font, "", 10)
            pdf.write(5, pdf.clean_txt(f": {desc}\n"))
        pdf.ln(2)
        
    # ---------------- PAGE 3: HOW TO REVIEW & CONTACT ----------------
    pdf.add_page()
    
    pdf.set_font(main_font, "B", 14)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "3 How to review quickly (what to look for)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font(main_font, "B", 12)
    pdf.cell(0, 8, "3.1 Code-first projects", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    bullet_points_code = [
        "Look for a project-level README with setup steps.",
        "For C/C++ projects, check for a Makefile and a src/ folder.",
        "For Python projects, check for requirements.txt and runnable scripts (e.g., task1.py)."
    ]
    for bp in bullet_points_code:
        pdf.write(6, "  * ")
        pdf.write(6, pdf.clean_txt(f"{bp}\n"))
    pdf.ln(4)
    
    pdf.set_font(main_font, "B", 12)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "3.2 Report-first projects", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, 6, pdf.clean_txt("  * Some folders include PDFs (reports/specs). Opening the PDF first can be the fastest way to understand the goal and results."))
    pdf.ln(6)
    
    # Section 4
    pdf.set_font(main_font, "B", 14)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "4 Optional: running the highlight project (GENFIT)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    pdf.multi_cell(0, 6, pdf.clean_txt("The GENFIT repository contains detailed Docker instructions in its own README. In general terms, the flow is:"))
    pdf.ln(2)
    pdf.write(6, "  1. Install Docker + Docker Compose.\n")
    pdf.write(6, "  2. Follow the docker-compose commands in the project README.\n")
    pdf.ln(6)
    
    # Section 5: Contact
    pdf.set_font(main_font, "B", 14)
    pdf.set_text_color(26, 82, 118)
    pdf.cell(0, 8, "5 Contact", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    
    pdf.set_font(main_font, "", 11)
    pdf.set_text_color(33, 33, 33)
    pdf.write(6, pdf.clean_txt("You can reach me via email or GitHub for questions regarding these projects.\n"))
    pdf.set_font(main_font, "B", 11)
    pdf.write(6, "GitHub: ")
    pdf.set_font(main_font, "", 11)
    pdf.write(6, "github.com/Ayhan-coder\n")
    
    # Output to file
    pdf.output("recruiter_guide.pdf")
    print("recruiter_guide.pdf generated successfully!")

if __name__ == "__main__":
    create_guide()
