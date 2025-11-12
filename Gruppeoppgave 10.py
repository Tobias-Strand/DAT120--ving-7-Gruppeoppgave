# DAT120 Øving 7 – Gruppeprosjekt del 2
# Gruppe: Tobias, Mika, Bonaa, Daniel

import json

# =========================================================
# Del 1 – Tobias: I/O-hjelpere, meny og hovedloop
# =========================================================

def ask_int(prompt, lo=None, hi=None):
    while True:
        s = input(prompt).strip()
        try:
            v = int(s)
            if lo is not None and v < lo:
                print(f"Må være >= {lo}."); continue
            if hi is not None and v > hi:
                print(f"Må være <= {hi}."); continue
            return v
        except ValueError:
            print("Ugyldig tall, prøv igjen.")

def ask_str(prompt):
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Kan ikke være tomt.")

def ask_opt_str(prompt):
    return input(prompt).strip()

def ask_term(prompt="Termin (H/V): "):
    while True:
        s = input(prompt).strip().upper()
        if s in ("H", "V"):
            return s
        print("Skriv H (høst) eller V (vår).")

def sem_type(semnr: int) -> str:
    return "H" if semnr in (1, 3, 5) else "V"

def skriv_meny():
    print("\nMeny:")
    print("1. Lag et nytt emne")
    print("2. Legg til et emne i en studieplan")
    print("3. Fjern et emne fra en studieplan")
    print("4. Skriv ut ei liste over alle registrerte emner")
    print("5. Lag en ny tom studieplan")
    print("6. Skriv ut en studieplan")
    print("7. Sjekk om en studieplan er gyldig")
    print("8. Finn studieplaner som bruker et emne")
    print("9. Lagre emner og studieplaner til fil")
    print("10. Les inn emner og studieplaner fra fil")
    print("11. Avslutt")

def velg_studieplan(studieplaner: dict):
    if not studieplaner:
        print("Ingen studieplaner finnes. Opprett først (valg 5).")
        return None
    print("\nTilgjengelige studieplaner:")
    for pid, sp in studieplaner.items():
        print(f"- {pid}: {sp.tittel}")
    pid = ask_str("Skriv id for studieplan: ")
    sp = studieplaner.get(pid)
    if not sp:
        print("Fant ikke studieplan.")
    return sp

def velg_emne(emneregister: dict):
    if not emneregister:
        print("Ingen emner registrert. Lag emner først (valg 1).")
        return None
    kode = ask_str("Emnekode: ").upper()
    emne = emneregister.get(kode)
    if not emne:
        print("Emnet finnes ikke.")
    return emne

# =========================================================
# Del 2 – Mika: Emne-klassen og emneregister (valg 1 & 4)
# =========================================================

class Emne:
    def __init__(self, kode: str, navn: str, termin: str, sp: int,
                 eksamensform: str = "", beskrivelse: str = ""):
        self.kode = kode.upper()
        self.navn = navn
        self.termin = termin.upper()   # 'H' eller 'V'
        self.sp = int(sp)
        self.eksamensform = eksamensform
        self.beskrivelse = beskrivelse

    def passer_i_semester(self, semnr: int) -> bool:
        return self.termin == sem_type(semnr)

    def to_dict(self) -> dict:
        return {
            "kode": self.kode,
            "navn": self.navn,
            "termin": self.termin,
            "sp": self.sp,
            "eksamensform": self.eksamensform,
            "beskrivelse": self.beskrivelse,
        }

    @staticmethod
    def from_dict(d: dict) -> "Emne":
        return Emne(
            d["kode"], d.get("navn", ""),
            d.get("termin", "H"), d.get("sp", 0),
            d.get("eksamensform", ""), d.get("beskrivelse", "")
        )

    def __str__(self):
        return (f"{self.kode:10s} | navn: {self.navn} | termin: {self.termin} "
                f"| sp: {self.sp:>2} | eksamen: {self.eksamensform or '-'}")

def v1_lag_emne(emneregister: dict):
    kode = ask_str("Emnekode (f.eks. MAT100): ").upper()
    if kode in emneregister:
        print("Emnet finnes allerede.")
        return
    navn = ask_str("Navn: ")
    termin = ask_term("Termin (H/V): ")
    sp = ask_int("Studiepoeng (heltall): ", lo=1)
    eks = ask_opt_str("Eksamensform (valgfritt): ")
    bes = ask_opt_str("Beskrivelse (valgfritt): ")
    emneregister[kode] = Emne(kode, navn, termin, sp, eks, bes)
    print(f"Lagret {kode}.")

def v4_skriv_emner(emneregister: dict):
    if not emneregister:
        print("Ingen emner registrert."); return
    print("\nRegistrerte emner\n" + "-"*72)
    for kode in sorted(emneregister):
        print(str(emneregister[kode]))
    print("-"*72)

# =========================================================
# Del 3 – Bonaa: Meny 2 & 3 (legg til / fjern emne i studieplan)
#         + enkel støttefunksjon
# =========================================================

def finn_emne_i_semester(sp_liste, kode: str):
    for idx, e in enumerate(sp_liste):
        if e.kode == kode:
            return idx
    return -1

def v2_legg_til_emne_i_studieplan(studieplaner: dict, emneregister: dict):
    sp = velg_studieplan(studieplaner)
    if not sp: return
    emne = velg_emne(emneregister)
    if not emne: return
    sem = ask_int("Semester (1–6): ", lo=1, hi=6)

    ok, msg = sp.legg_til_emne(emne, sem)
    if ok:
        print(f"La til {emne.kode} i semester {sem}. (Sum nå: {sp.sum_sp(sem)} sp)")
    else:
        print("Kunne ikke legge til:", msg)

def v3_fjern_emne_fra_studieplan(studieplaner: dict):
    sp = velg_studieplan(studieplaner)
    if not sp: return
    kode = ask_str("Emnekode å fjerne: ").upper()
    sem = ask_int("Fra hvilket semester (1–6): ", lo=1, hi=6)
    if sp.fjern_emne(kode, sem):
        print(f"Fjernet {kode} fra semester {sem}.")
    else:
        print("Fant ikke emnet i angitt semester.")

# =========================================================
# Del 4 – Daniel: Studieplan-klassen + meny 5–10 (plan/lagre/les)
# =========================================================

class Studieplan:
    def __init__(self, plan_id: str, tittel: str):
        self.plan_id = plan_id
        self.tittel = tittel
        # Lagrer Emne-objekter per semester
        self.semestre = {i: [] for i in range(1, 7)}

    # ---- Kjernefunksjoner som metoder ----
    def sum_sp(self, sem: int) -> int:
        return sum(e.sp for e in self.semestre.get(sem, []))

    def finnes(self, kode: str) -> bool:
        return any(any(e.kode == kode for e in lst) for lst in self.semestre.values())

    def legg_til_emne(self, emne: Emne, sem: int):
        if self.finnes(emne.kode):
            return False, "Emnet finnes allerede i denne studieplanen."
        if not emne.passer_i_semester(sem):
            return False, f"Termin passer ikke: {emne.kode} har {emne.termin}, sem {sem} er {sem_type(sem)}."
        ny_sum = self.sum_sp(sem) + emne.sp
        if ny_sum > 30:
            return False, f"Overskrider 30 sp i semester {sem} (ville blitt {ny_sum} sp)."
        self.semestre[sem].append(emne)
        return True, ""

    def fjern_emne(self, kode: str, sem: int) -> bool:
        lst = self.semestre.get(sem, [])
        idx = finn_emne_i_semester(lst, kode)
        if idx >= 0:
            lst.pop(idx)
            return True
        return False

    def skriv_ut(self):
        print(f"\nStudieplan: {self.tittel} (id: {self.plan_id})\n" + "="*72)
        for sem in range(1, 7):
            sesong = "Høst" if sem_type(sem) == "H" else "Vår"
            print(f"Semester {sem} ({sesong})")
            if not self.semestre[sem]:
                print("  (Ingen emner)")
            else:
                for e in self.semestre[sem]:
                    print(f"  - {e.kode} {e.navn} ({e.sp} sp)")
            print(f"  Sum: {self.sum_sp(sem)} sp\n" + "-"*72)

    def er_gyldig(self):
        avvik = []
        for sem in range(1, 7):
            total = self.sum_sp(sem)
            if total != 30:
                avvik.append(f"Semester {sem}: {total} sp (skal være 30 sp)")
            # Ensartet termin-sjekk for alle emner
            for e in self.semestre[sem]:
                if not e.passer_i_semester(sem):
                    avvik.append(f"{e.kode} i sem {sem}: termin {e.termin} passer ikke {sem_type(sem)}")
        return (len(avvik) == 0), avvik

    # ---- Serialisering ----
    def to_dict(self):
        # Lagre emnereferanser som koder per semester
        return {
            "plan_id": self.plan_id,
            "tittel": self.tittel,
            "semestre": {str(k): [e.kode for e in v] for k, v in self.semestre.items()}
        }

    @staticmethod
    def from_dict(d: dict, emneregister: dict) -> "Studieplan":
        sp = Studieplan(d["plan_id"], d.get("tittel", "Uten tittel"))
        sem = d.get("semestre", {})
        for k, kodeliste in sem.items():
            semnr = int(k)
            for kode in kodeliste:
                e = emneregister.get(kode.upper())
                if e:
                    sp.semestre[semnr].append(e)
        return sp

# ---- Menyvalg styrt av Daniel ----

def v5_ny_studieplan(studieplaner: dict):
    plan_id = ask_str("Ny studieplan id: ")
    if plan_id in studieplaner:
        print("Id er allerede i bruk."); return
    tittel = ask_str("Tittel: ")
    studieplaner[plan_id] = Studieplan(plan_id, tittel)
    print(f"Laget studieplan '{tittel}' (id: {plan_id}).")

def v6_skriv_studieplan(studieplaner: dict):
    sp = velg_studieplan(studieplaner)
    if sp: sp.skriv_ut()

def v7_sjekk_gyldig(studieplaner: dict):
    sp = velg_studieplan(studieplaner)
    if not sp: return
    ok, avvik = sp.er_gyldig()
    if ok:
        print("Studieplanen er gyldig. ✔")
    else:
        print("Studieplanen er IKKE gyldig. Avvik:")
        for a in avvik:
            print("  -", a)

def v8_finn_planer_for_emne(studieplaner: dict):
    if not studieplaner:
        print("Ingen studieplaner finnes."); return
    kode = ask_str("Emnekode: ").upper()
    brukere = [sp.tittel for sp in studieplaner.values() if sp.finnes(kode)]
    if brukere:
        print("Studieplaner som bruker emnet:")
        for t in brukere:
            print(" -", t)
    else:
        print("Ingen studieplaner bruker dette emnet.")

def v9_lagre(emneregister: dict, studieplaner: dict):
    fil = ask_str("Filnavn (f.eks. data.json): ")
    try:
        data = {
            "emner": [e.to_dict() for e in emneregister.values()],
            "studieplaner": [sp.to_dict() for sp in studieplaner.values()]
        }
        with open(fil, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Lagret til '{fil}'.")
    except OSError as e:
        print("Feil ved lagring:", e)

def v10_les():
    fil = ask_str("Filnavn (f.eks. data.json): ")
    try:
        with open(fil, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Bygg emneregister først
        emneregister = {}
        for d in data.get("emner", []):
            e = Emne.from_dict(d)
            emneregister[e.kode] = e
        # Bygg studieplaner og knytt emner
        studieplaner = {}
        for pd in data.get("studieplaner", []):
            sp = Studieplan.from_dict(pd, emneregister)
            studieplaner[sp.plan_id] = sp
        print(f"Lest fra '{fil}'.")
        return emneregister, studieplaner
    except (OSError, json.JSONDecodeError) as e:
        print("Feil ved lesing:", e)
        return None, None

# =========================================================
# Tobias – hovedprogram
# =========================================================

def main():
    emneregister = {}      # dict[str, Emne]
    studieplaner = {}      # dict[str, Studieplan]

    while True:
        skriv_meny()
        valg = ask_int("Velg (1–11): ", lo=1, hi=11)

        if valg == 1:
            v1_lag_emne(emneregister)
        elif valg == 2:
            v2_legg_til_emne_i_studieplan(studieplaner, emneregister)
        elif valg == 3:
            v3_fjern_emne_fra_studieplan(studieplaner)
        elif valg == 4:
            v4_skriv_emner(emneregister)
        elif valg == 5:
            v5_ny_studieplan(studieplaner)
        elif valg == 6:
            v6_skriv_studieplan(studieplaner)
        elif valg == 7:
            v7_sjekk_gyldig(studieplaner)
        elif valg == 8:
            v8_finn_planer_for_emne(studieplaner)
        elif valg == 9:
            v9_lagre(emneregister, studieplaner)
        elif valg == 10:
            e, sp = v10_les()
            if e is not None:
                emneregister, studieplaner = e, sp
        elif valg == 11:
            print("Avslutter programmet.")
            break

if __name__ == "__main__":
    main()