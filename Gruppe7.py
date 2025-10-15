#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DAT120 øving 7 – Del 1 (forenklet løsning for menyvalg 1–8)

- Emner lagres som: emner[kode] = {"t": "H"/"V", "sp": int}
- Studieplan lagres som: plan[semester] = [emnekoder]
- Validering ved innlegging: unikhet, riktig termin (H: 1/3/5, V: 2/4/6), maks 30 sp
- Lagring/lesing på JSON-format
"""

import json

# ---------- Små, gjenbrukbare input-funksjoner ----------

def ask_int(prompt, lo=None, hi=None):
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if lo is not None and v < lo:  print(f"Må være >= {lo}.");  continue
            if hi is not None and v > hi:  print(f"Må være <= {hi}.");  continue
            return v
        except ValueError:
            print("Ugyldig tall, prøv igjen.")

def ask_str(prompt):
    while True:
        s = input(prompt).strip()
        if s: return s
        print("Kan ikke være tomt.")

def ask_term(prompt="Semester (H/V): "):
    while True:
        s = input(prompt).strip().upper()
        if s in ("H","V"): return s
        print("Skriv H (høst) eller V (vår).")

# ---------- Domenelogikk ----------

def tom_plan():
    # Seks semestre (1–6), tomme lister
    return {i: [] for i in range(1, 7)}

def sem_type(sem):
    # 1/3/5 = H, 2/4/6 = V
    return "H" if sem in (1,3,5) else "V"

def sum_sp(emner, plan, sem):
    return sum(emner[k]["sp"] for k in plan.get(sem, []))

def finnes_i_plan(plan, kode):
    return any(kode in lst for lst in plan.values())

# ---------- Menyvalg ----------

def v1_nytt_emne(emner):
    kode = ask_str("Emnekode (f.eks. MAT100): ").upper()
    term = ask_term("Undervises H/V: ")
    sp = ask_int("Studiepoeng (heltall): ", lo=1)
    emner[kode] = {"t": term, "sp": sp}
    print(f"Lagret {kode}: {term}, {sp} sp.")

def v2_legge_til_i_plan(emner, plan):
    if not emner:
        print("Ingen emner registrert. Lag emner først (1).");  return
    kode = ask_str("Emnekode å legge til: ").upper()
    if kode not in emner:
        print("Emnet finnes ikke i registeret.");  return
    if finnes_i_plan(plan, kode):
        print("Emnet er allerede i studieplanen.");  return
    sem = ask_int("Semester (1–6): ", lo=1, hi=6)

    # Sjekk termin
    if emner[kode]["t"] != sem_type(sem):
        print(f"Ugyldig semester: {kode} har {emner[kode]['t']}, "
              f"men semester {sem} er {sem_type(sem)}."); return

    # Sjekk 30-sp-grense
    ny_sum = sum_sp(emner, plan, sem) + emner[kode]["sp"]
    if ny_sum > 30:
        print(f"Overskrider 30 sp i semester {sem} (ville blitt {ny_sum} sp)."); return

    plan[sem].append(kode)
    print(f"La til {kode} i semester {sem}. (Sum nå: {ny_sum} sp)")

def v3_skriv_emner(emner):
    if not emner:
        print("Ingen emner registrert."); return
    print("\nRegistrerte emner\n" + "-"*36)
    for kode in sorted(emner):
        d = emner[kode]
        print(f"{kode:10s} | termin: {d['t']} | sp: {d['sp']}")
    print("-"*36)

def v4_skriv_plan(emner, plan):
    print("\nStudieplan\n" + "="*36)
    for sem in range(1,7):
        sesong = "Høst" if sem_type(sem)=="H" else "Vår"
        print(f"Semester {sem} ({sesong})")
        if not plan[sem]:
            print("  (Ingen emner)")
        else:
            for k in plan[sem]:
                print(f"  - {k} ({emner[k]['sp']} sp)")
        print(f"  Sum: {sum_sp(emner, plan, sem)} sp\n" + "-"*36)

def v5_sjekk_gyldig(emner, plan):
    avvik = [(sem, sum_sp(emner, plan, sem)) for sem in range(1,7) if sum_sp(emner, plan, sem) != 30]
    if not avvik:
        print("Studieplanen er gyldig.(30 sp i alle semestre).")
    else:
        print("Studieplanen er IKKE gyldig. Avvik:")
        for sem, total in avvik:
            print(f"  Semester {sem}: {total} sp (skal være 30 sp)")

def v6_lagre(emner, plan):
    fil = ask_str("Filnavn å lagre til (f.eks. plan.json): ")
    try:
        with open(fil, "w", encoding="utf-8") as f:
            json.dump({"emner": emner, "plan": plan}, f, ensure_ascii=False, indent=2)
        print(f"Lagret til '{fil}'.")
    except OSError as e:
        print("Feil ved lagring:", e)

def v7_les():
    fil = ask_str("Filnavn å lese fra (f.eks. plan.json): ")
    try:
        with open(fil, "r", encoding="utf-8") as f:
            data = json.load(f)
        emner = data.get("emner", {})
        plan = data.get("plan", tom_plan())
        # Sørg for 1–6 finnes
        for i in range(1,7):
            plan.setdefault(i, [])
        print(f"Lest fra '{fil}'.")
        return emner, plan
    except (OSError, json.JSONDecodeError) as e:
        print("Feil ved lesing:", e)
        return None, None

# ---------- Meny/loop ----------

def skriv_meny():
    print("\nMeny:")
    print("1. Lag et nytt emne")
    print("2. Legg til et emne i studieplanen")
    print("3. Skriv ut ei liste over alle registrerte emner")
    print("4. Skriv ut studieplanen med hvilke emner som er i hvert semester")
    print("5. Sjekk om studieplanen er gyldig eller ikke")
    print("6. Lagre emnene og studieplanen til fil")
    print("7. Les inn emnene og studieplanen fra fil")
    print("8. Avslutt")

def main():
    emner = {}
    plan = tom_plan()

    while True:
        skriv_meny()
        valg = ask_int("Velg (1–8): ", lo=1, hi=8)
        if valg == 1: v1_nytt_emne(emner)
        elif valg == 2: v2_legge_til_i_plan(emner, plan)
        elif valg == 3: v3_skriv_emner(emner)
        elif valg == 4: v4_skriv_plan(emner, plan)
        elif valg == 5: v5_sjekk_gyldig(emner, plan)
        elif valg == 6: v6_lagre(emner, plan)
        elif valg == 7:
            e, p = v7_les()
            if e is not None: emner, plan = e, p
        elif valg == 8:
            print("Avslutter. Ha en fin dag!")
            break

if __name__ == "__main__":
    main()
