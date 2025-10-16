
# DAT120 Øving 7 – Gruppeprosjekt del 1
# Gruppe: Tobias, Mika, Bonaa, Daniel

import json

# Del 1: Tobias 
# Input-funksjoner og hovedloop

# En "funksjon" er en liten bit kode som kan brukes flere ganger.
# "Input" betyr at brukeren skriver inn noe, for eksempel tekst eller tall.
# En "while True"-løkke kjører helt til vi stopper den med "break".
# "return" sender verdien tilbake til stedet der funksjonen ble kalt.
# I hovedloopen brukes tallene (1–8) for å velge hva programmet skal gjøre.


def ask_int(prompt, lo=None, hi=None):
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if lo is not None and v < lo:
                print(f"Må være >= {lo}.")
                continue
            if hi is not None and v > hi:
                print(f"Må være <= {hi}.")
                continue
            return v
        except ValueError:
            print("Ugyldig tall, prøv igjen.")

def ask_str(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Kan ikke være tomt.")

def ask_term(prompt="Semester (H/V): "):
    while True:
        s = input(prompt).strip().upper()
        if s in ("H", "V"):
            return s
        print("Skriv H (høst) eller V (vår).")

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

# ============================================
# === Del 2: Mika =============================
# Domenelogikk, hjelpefunksjoner og menyvalg 1
# --------------------------------------------
# Forklaring:
# En ordbok brukes til å lagre informasjon med nøkkel og verdi.
# bruker en ordbok til å lagre hvilke emner som ligger i hvert semester.
# ============================================

def tom_plan():
    # Seks semestre (1–6), starter med tomme lister
    return {i: [] for i in range(1, 7)}

def sem_type(sem):
    # 1/3/5 = Høst, 2/4/6 = Vår
    return "H" if sem in (1, 3, 5) else "V"

def sum_sp(emner, plan, sem):
    # summerer studiepoengene for semester
    return sum(emner[k]["sp"] for k in plan.get(sem, []))

def finnes_i_plan(plan, kode):
    # sjekker om fagkoden finnes fra før, returnerer hvis den eksiterer i en annen liste fra før.
    return any(kode in lst for lst in plan.values())


def v1_nytt_emne(emner):
    kode = ask_str("Emnekode (f.eks. MAT100): ").upper()
    term = ask_term("Undervises H/V: ")
    sp = ask_int("Studiepoeng (heltall): ", lo=1)
    emner[kode] = {"t": term, "sp": sp}
    print(f"Lagret {kode}: {term}, {sp} sp.")


#Del 3: Bonaa



def v2_legge_til_i_plan(emner, plan):
    if not emner:
        print("Ingen emner registrert. Lag emner først (1).")
        return
    kode = ask_str("Emnekode å legge til: ").upper()
    if kode not in emner:
        print("Emnet finnes ikke i registeret.")   ##Avsnittet kontrollerer at brukeren bare kan legge til et gyldig emne i studieplanen.
        return                             #Først sjekkes det at det finnes registrerte emner. Deretter ber programmet brukeren skrive inn en emnekode 
                                             #Så sjekkes det at emnet faktisk finnes i registeret, og at det ikke allerede ligger i studieplanen.
                                         #Hvis noe av dette ikke stemmer, får brukeren en feilmelding og funksjonen stopper.
        
    if finnes_i_plan(plan, kode):
        print("Emnet er allerede i studieplanen.")  #hvis den allerede ligg i studieplanen så printes det "emnet er allerede i studieplanen"
        return

    sem = ask_int("Semester (1–6): ", lo=1, hi=6) #hvillket semester emnet skal legges inn i

    # Sjekk termin
    if emner[kode]["t"] != sem_type(sem): # Sjekker om termin for emnet ikke passer med semesteret
        print(f"Ugyldig semester: {kode} har {emner[kode]['t']}, " # Skriver hvilken termin emnet har
              f"men semester {sem} er {sem_type(sem)}.") # Skriver hvilken termin semesteret er
        return # hvis emneets termin ikke passer med semesteret så stopper funksjonen

    # Sjekk 30-sp-grense
    ny_sum = sum_sp(emner, plan, sem) + emner[kode]["sp"]
    if ny_sum > 30:   # dette avsnittet passer på at et semester ikke får mer enn 30 studiepoeng # hvis du prøver å legge inn
        print(f"Overskrider 30 sp i semester {sem} (ville blitt {ny_sum} sp).") # et emne som gir over 30 poeng så får du advarsel og det avsluttes 
        return

    plan[sem].append(kode) 
    print(f"La til {kode} i semester {sem}. (Sum nå: {ny_sum} sp)") #dette avsnittet legger emne i studieplanen

def v3_skriv_emner(emner): # Sjekk om listen med emner er tom
    if not emner:
        print("Ingen emner registrert.") # hvis ingen emner finnes så stoppes funksjonen her
        return
    print("\nRegistrerte emner\n" + "-"*36) # \n lager ny linje, "-"*36 lager en horisontal linje
    for kode in sorted(emner): # går gjennom emnene i alfabetisk rekkefølge
        d = emner[kode]
        print(f"{kode:10s} | termin: {d['t']} | sp: {d['sp']}") # skriv ut en linkje for hvert emne med kode termin og studiepoeng
    print("-"*36) # avsluttes med å skrive en strek for listen

def v4_skriv_plan(emner, plan):
    print("\nStudieplan\n" + "="*36)
    for sem in range(1, 7): # går gjennom alle semester fra 1 til 6
        sesong = "Høst" if sem_type(sem) == "H" else "Vår" # finner ut om semesteret er høst eller vår
        print(f"Semester {sem} ({sesong})") #printer ut semester og sesong
        if not plan[sem]: #hvis listen er tom så finnes det ikke noe emner
            print("  (Ingen emner)")
        else:
            for k in plan[sem]: # Hvis det finnes emner, så skrives hvert emne med studiepoeng
                print(f"  - {k} ({emner[k]['sp']} sp)") 
        print(f"  Sum: {sum_sp(emner, plan, sem)} sp\n" + "-"*36) # Skrives totalsum for semesteret og avslutt med en linje for ryddighet


# Del 4: Daniel 
# Menyvalg 5–7 og filoperasjoner



def v5_sjekk_gyldig(emner, plan):
    avvik = []
    for sem in range(1, 7):
        total = sum_sp(emner, plan, sem)
        if total != 30:
            avvik.append((sem, total))
    if not avvik:
        print("Studieplanen er gyldig. (30 sp i alle semestre)")
    else:
        print("Studieplanen er IKKE gyldig. Avvik funnet:")
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
        for i in range(1, 7):
            plan.setdefault(i, [])
        print(f"Lest fra '{fil}'.")
        return emner, plan
    except (OSError, json.JSONDecodeError) as e:
        print("Feil ved lesing:", e)
        return None, None


#Tobias: avslutter hovedloop

def main():
    emner = {}
    plan = tom_plan()

    while True:
        skriv_meny()
        valg = ask_int("Velg (1–8): ", lo=1, hi=8)

        if valg == 1:
            v1_nytt_emne(emner)
        elif valg == 2:
            v2_legge_til_i_plan(emner, plan)
        elif valg == 3:
            v3_skriv_emner(emner)
        elif valg == 4:
            v4_skriv_plan(emner, plan)
        elif valg == 5:
            v5_sjekk_gyldig(emner, plan)
        elif valg == 6:
            v6_lagre(emner, plan)
        elif valg == 7:
            e, p = v7_les()
            if e is not None:
                emner, plan = e, p
        elif valg == 8:
            print("Avslutter programmet.")
            break

if __name__ == "__main__":
    main()
