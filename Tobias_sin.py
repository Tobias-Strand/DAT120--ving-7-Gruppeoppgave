#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Studieplan-menyprogram

Funksjoner:
1. Lag et nytt emne
2. Legg til et emne i studieplanen
3. Skriv ut ei liste over alle registrerte emner
4. Skriv ut studieplanen med hvilke emner som er i hvert semester
5. Sjekk om studieplanen er gyldig eller ikke
6. Lagre emnene og studieplanen til fil
7. Les inn emnene og studieplanen fra fil
8. Avslutt

Format/antagelser:
- Et emne har: emnekode (unik), navn, studiepoeng (float), og (frivillig) liste over forkunnskaper/prerequisites som emnekoder.
- Studieplanen er en mapping fra semesternummer (1,2,3,...) til en liste av emnekoder.
- «Gyldig studieplan» sjekker:
    (A) Ingen duplikater av samme emnekode i hele planen.
    (B) Alle emner i planen finnes i emneregisteret.
    (C) Alle forkunnskapskrav er oppfylt i tidligere semester (samme semester teller ikke).
    (D) (Valgfritt) Sjekk at sum studiepoeng per semester er nøyaktig TARGET_ECTS_PER_SEM.
        Dette kan slås av/på med ENFORCE_ECTS_PER_SEM.

Lagring/lesing:
- JSON-fil med to toppnøkler: "courses" og "plan".
- courses: dict[code] -> {"code","name","credits","prerequisites": [...]}.
- plan: dict[str(sem)] -> [course_code,...] (lagres med str-nøkler for JSON, konverteres til int ved lesing).

Kjøring:
    python3 studieplan.py

"""
from __future__ import annotations
from dataclasses import dataclass, asdict, field
import json
from typing import Dict, List, Tuple

# --- Konfig ---
TARGET_ECTS_PER_SEM: float = 30.0
ENFORCE_ECTS_PER_SEM: bool = False  # Sett til True hvis du vil kreve nøyaktig 30 studiepoeng per semester.


@dataclass
class Course:
    code: str
    name: str
    credits: float
    prerequisites: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        # Normaliser kode og forkunnskaper til UPPER case for konsistens
        d["code"] = self.code.upper()
        d["prerequisites"] = [p.upper() for p in self.prerequisites]
        return d

    @staticmethod
    def from_dict(d: dict) -> "Course":
        return Course(
            code=str(d.get("code", "")).upper(),
            name=str(d.get("name", "")),
            credits=float(d.get("credits", 0.0)),
            prerequisites=[str(p).upper() for p in d.get("prerequisites", [])],
        )


class StudyPlan:
    def __init__(self) -> None:
        self.courses: Dict[str, Course] = {}  # code -> Course
        self.plan: Dict[int, List[str]] = {}  # semester -> [course_code]

    # --- Emner ---
    def add_course(self, course: Course) -> bool:
        code = course.code.upper()
        if not code:
            print("[Feil] Emnekode kan ikke være tom.")
            return False
        if code in self.courses:
            print(f"[Feil] Emnekode {code} finnes allerede.")
            return False
        self.courses[code] = course
        print(f"[OK] La til emne {code}: {course.name} ({course.credits} sp)")
        return True

    def list_courses(self) -> None:
        if not self.courses:
            print("Ingen emner registrert ennå.")
            return
        print("\nAlle registrerte emner:")
        for code in sorted(self.courses.keys()):
            c = self.courses[code]
            prereq = ", ".join(c.prerequisites) if c.prerequisites else "(ingen)"
            print(f"- {c.code}: {c.name} – {c.credits} sp – forkunnskaper: {prereq}")
        print()

    # --- Studieplan ---
    def add_to_semester(self, semester: int, code: str) -> bool:
        code = code.upper()
        if code not in self.courses:
            print(f"[Feil] Emnet {code} finnes ikke i emneregisteret. Legg det til først (valg 1).")
            return False
        if semester <= 0:
            print("[Feil] Semester må være et positivt heltall (1,2,3,...).")
            return False
        # opprett semesterliste ved behov
        self.plan.setdefault(semester, [])
        # sjekk om finnes allerede i samme semester
        if code in self.plan[semester]:
            print(f"[Feil] Emnet {code} ligger allerede i semester {semester}.")
            return False
        # sjekk om emnet ligger i en annen semester fra før (globale duplikater)
        for sem, codes in self.plan.items():
            if sem != semester and code in codes:
                print(f"[Feil] Emnet {code} ligger allerede i semester {sem}. Samme emne kan ikke være i flere semester.")
                return False
        self.plan[semester].append(code)
        print(f"[OK] La {code} til i semester {semester}.")
        return True

    def print_plan(self) -> None:
        if not self.plan:
            print("Ingen emner i studieplanen ennå.")
            return
        print("\nStudieplan:")
        for sem in sorted(self.plan.keys()):
            codes = self.plan[sem]
            total = sum(self.courses[c].credits for c in codes if c in self.courses)
            print(f"Semester {sem} (sum {total} sp):")
            if not codes:
                print("  (tomt)")
            for ccode in codes:
                c = self.courses.get(ccode)
                if c is None:
                    print(f"  - {ccode} (ADVARSEL: ikke funnet i emneregisteret)")
                else:
                    print(f"  - {c.code}: {c.name} ({c.credits} sp)")
        print()

    # --- Validering ---
    def validate(self) -> Tuple[bool, List[str]]:
        messages: List[str] = []
        ok = True

        # (A) globale duplikater
        seen: Dict[str, int] = {}
        for sem, codes in self.plan.items():
            for code in codes:
                codeU = code.upper()
                if codeU in seen:
                    messages.append(f"Duplikat: {codeU} finnes i semester {seen[codeU]} og {sem}.")
                    ok = False
                else:
                    seen[codeU] = sem

        # (B) finnes alle emner?
        for sem, codes in self.plan.items():
            for code in codes:
                if code.upper() not in self.courses:
                    messages.append(f"Ukjent emne i planen: {code} i semester {sem}.")
                    ok = False

        # (C) forkunnskaper oppfylt?
        # bygg mengde med alle emner ferdig før gitt semester
        completed_before: Dict[int, set[str]] = {}
        accumulated: set[str] = set()
        for sem in sorted(self.plan.keys()):
            completed_before[sem] = accumulated.copy()
            # oppdater for neste runde
            for code in self.plan[sem]:
                accumulated.add(code.upper())

        for sem in sorted(self.plan.keys()):
            before = completed_before[sem]
            for code in self.plan[sem]:
                c = self.courses.get(code.upper())
                if not c:
                    continue
                missing = [p for p in c.prerequisites if p.upper() not in before]
                if missing:
                    messages.append(
                        f"Forkunnskaper ikke oppfylt for {c.code} i sem {sem}: mangler {', '.join(missing)} før dette semesteret."
                    )
                    ok = False

        # (D) (valgfritt) sum studiepoeng per sem = TARGET_ECTS_PER_SEM
        if ENFORCE_ECTS_PER_SEM:
            for sem in sorted(self.plan.keys()):
                total = 0.0
                unknown: List[str] = []
                for code in self.plan[sem]:
                    course = self.courses.get(code.upper())
                    if course:
                        total += course.credits
                    else:
                        unknown.append(code)
                if unknown:
                    messages.append(
                        f"Advarsel sem {sem}: ukjente emner {', '.join(unknown)} – kan ikke verifisere studiepoeng."
                    )
                    ok = False
                if abs(total - TARGET_ECTS_PER_SEM) > 1e-6:
                    messages.append(
                        f"Semester {sem} har {total} sp (må være {TARGET_ECTS_PER_SEM} sp hvis ECTS-regel håndheves)."
                    )
                    ok = False

        if ok:
            messages.append("Studieplanen er GYLDIG. ✔")
        else:
            messages.append("Studieplanen er IKKE gyldig. ✖")
        return ok, messages

    # --- Lagring/lesing ---
    def save(self, filename: str) -> bool:
        try:
            data = {
                "courses": {code: c.to_dict() for code, c in self.courses.items()},
                "plan": {str(sem): [code for code in codes] for sem, codes in self.plan.items()},
            }
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[OK] Lagret til {filename}")
            return True
        except Exception as e:
            print(f"[Feil] Klarte ikke å lagre: {e}")
            return False

    def load(self, filename: str) -> bool:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            # last emner
            courses_dict = data.get("courses", {})
            self.courses = {code.upper(): Course.from_dict(cd) for code, cd in courses_dict.items()}
            # last plan
            plan_dict = data.get("plan", {})
            plan_tmp: Dict[int, List[str]] = {}
            for sem_str, codes in plan_dict.items():
                try:
                    sem = int(sem_str)
                except ValueError:
                    print(f"[Advarsel] Ignorerer ugyldig semesternøkkel: {sem_str}")
                    continue
                plan_tmp[sem] = [str(c).upper() for c in codes]
            self.plan = plan_tmp
            print(f"[OK] Leste inn data fra {filename}")
            return True
        except FileNotFoundError:
            print(f"[Feil] Fant ikke filen: {filename}")
            return False
        except Exception as e:
            print(f"[Feil] Klarte ikke å lese fil: {e}")
            return False


# --- Hjelpefunksjoner for input ---
def prompt_nonempty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Input kan ikke være tom. Prøv igjen.")


def prompt_float(prompt: str) -> float:
    while True:
        s = input(prompt).strip().replace(",", ".")
        try:
            return float(s)
        except ValueError:
            print("Skriv et tall (bruk . eller , for desimaler).")


def prompt_int(prompt: str) -> int:
    while True:
        s = input(prompt).strip()
        try:
            return int(s)
        except ValueError:
            print("Skriv et heltall, f.eks. 1, 2, 3 ...")


def parse_prereq_list(s: str) -> List[str]:
    if not s.strip():
        return []
    parts = [p.strip().upper() for p in s.split(",")]
    return [p for p in parts if p]


# --- Menyhandling ---
def print_menu() -> None:
    print("""
==================== MENY ====================
1. Lag et nytt emne
2. Legg til et emne i studieplanen
3. Skriv ut ei liste over alle registrerte emner
4. Skriv ut studieplanen med hvilke emner som er i hvert semester
5. Sjekk om studieplanen er gyldig eller ikke
6. Lagre emnene og studieplanen til fil
7. Les inn emnene og studieplanen fra fil
8. Avslutt
==============================================
""")


def handle_choice(sp: StudyPlan, choice: int) -> bool:
    if choice == 1:
        code = prompt_nonempty("Emnekode (f.eks. MAT100): ").upper()
        name = prompt_nonempty("Navn (f.eks. Matematikk 1): ")
        credits = prompt_float("Studiepoeng (f.eks. 7.5 eller 10): ")
        prereq_raw = input("Forkunnskaper/prereq (kommadelt liste med emnekoder, valgfritt): ")
        prereq = parse_prereq_list(prereq_raw)
        sp.add_course(Course(code=code, name=name, credits=credits, prerequisites=prereq))
        return True

    elif choice == 2:
        semester = prompt_int("Hvilket semester (1,2,3,...): ")
        code = prompt_nonempty("Hvilket emne (emnekode): ")
        sp.add_to_semester(semester, code)
        return True

    elif choice == 3:
        sp.list_courses()
        return True

    elif choice == 4:
        sp.print_plan()
        return True

    elif choice == 5:
        ok, msgs = sp.validate()
        print("\nValideringsrapport:")
        for m in msgs:
            print("-", m)
        print()
        return True

    elif choice == 6:
        filename = input("Filnavn å lagre til (Enter for 'studieplan.json'): ").strip()
        if not filename:
            filename = "studieplan.json"
        sp.save(filename)
        return True

    elif choice == 7:
        filename = input("Filnavn å lese fra (Enter for 'studieplan.json'): ").strip()
        if not filename:
            filename = "studieplan.json"
        sp.load(filename)
        return True

    elif choice == 8:
        print("Avslutter. Ha en fin dag!")
        return False

    else:
        print("Ugyldig valg. Velg 1-8.")
        return True


def main():
    sp = StudyPlan()
    # (Frivillig) legg inn noen eksempel-emner ved behov
    # sp.add_course(Course("MAT100", "Matematikk 1", 10, []))
    # sp.add_course(Course("FYS100", "Fysikk 1", 10, ["MAT100"]))

    running = True
    while running:
        print_menu()
        choice = prompt_int("Velg (1-8): ")
        running = handle_choice(sp, choice)


if __name__ == "__main__":
    main()
