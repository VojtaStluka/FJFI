from datetime import datetime, date, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# ============================================================
# 1. URČENÍ AKTUÁLNÍHO TÝDNE
# ============================================================

# Pro testování můžeš zadat konkrétní datum.
# Např.:
#
# TESTOVACI_DATUM = date(2026, 11, 18)
#
# Pro běžné používání nastav na None.

TESTOVACI_DATUM = None


if TESTOVACI_DATUM is None:
    DNES = datetime.now().date()
else:
    DNES = TESTOVACI_DATUM


# Pondělí aktuálního týdne
TYDEN_OD = DNES - timedelta(days=DNES.weekday())



# ============================================================
# 2. SVÁTKY
# ============================================================

SVATKY = {
    date(2026, 10, 28): "Státní svátek",
    date(2026, 11, 16): "Děkanské volno",
    date(2026, 11, 17): "Státní svátek",
}


# ============================================================
# 3. PLATNÉ TERMÍNY EZB
# ============================================================

EZB_TERMINY = {
    date(2026, 9, 21),
    date(2026, 10, 12),
    date(2026, 10, 19),
    date(2026, 11, 2),
    date(2026, 11, 23),
    date(2026, 12, 7),
}


# ============================================================
# 4. PLATNÉ TERMÍNY HEB
# ============================================================

HEB_TERMINY = {
    date(2026, 10, 6),
    date(2026, 10, 20),
    date(2026, 10, 27),
    date(2026, 11, 10),
    date(2026, 11, 24),
    date(2026, 12, 1),
    date(2026, 12, 8),
    date(2026, 12, 15),
}


# ============================================================
# 5. ZÁKLADNÍ ROZVRH
# ============================================================

ROZVRH = [

    # ---------- PONDĚLÍ ----------
    ("PO", "08:00", "10:00", "ZPSP",    "Augsten",     "B-009"),
    ("PO", "10:00", "12:00", "MECHcv",  "Cervenka",    "B-11"),
    ("PO", "12:00", "14:00", "MECH",    "Bren",        "B-103"),
    ("PO", "14:00", "16:00", "MAT1",    "Fucik",       "T-101"),
    ("PO", "16:30", "18:00", "EZB",     "Strobach.", "B-215"),
    ("PO", "16:00", "18:00", "šerm",    "",            "Vršovice"),
    ("PO", "18:00", "20:00", "CH1cv",   "Babicky",     "B-103"),

    # ---------- ÚTERÝ ----------
    ("ÚT", "08:00", "10:00", "ZPRO",    "Petrickova",  "T-101"),
    ("ÚT", "12:00", "14:00", "ZM1",     "Chaloupka",   "B-103"),
    ("ÚT", "14:00", "16:00", "HEB",     "Hornakova",   "B-215"),
    ("ÚT", "16:00", "18:00", "MAT1cv",  "Fukova",      "T-209"),

    # ---------- STŘEDA ----------
    ("ST", "08:00", "10:00", "DEF1",       "Jex",       "B-103"),
    ("ST", "10:00", "12:00", "MECH",       "Bren",      "B-103"),
    ("ST", "12:00", "14:00", "MAT1cv",     "Fukova",    "T-208"),
    ("ST", "14:30", "15:30", "Doučování",  "",          "knihovna"),
    ("ST", "16:00", "19:00", "šerm",       "",          "Vršovice"),

    # ---------- ČTVRTEK ----------
    ("ČT", "08:00", "9:30",  "Lezení", "",             "Juliska"),
    ("ČT", "10:00", "12:00", "MAT1",    "Fucik",       "T-101"),
    ("ČT", "13:00", "17:30", "ZBAF1",   "Vaculin",     "B-215"),
    ("ČT", "18:00", "20:00", "CH1",     "Distler",     "B-103"),

    # ---------- PÁTEK ----------
    ("PÁ", "08:00", "10:00", "ZPRO",    "Petrickova",  "T-201"),
    ("PÁ", "14:00", "16:00", "MAM1",    "Bren",        "T-101"),
    ("PÁ", "16:00", "17:40", "MAM2",    "Heriban",     "T-101"),
]


# ============================================================
# 6. VZHLED
# ============================================================

DNY = ["PO", "ÚT", "ST", "ČT", "PÁ"]

NAZVY_DNU = {
    "PO": "Pondělí",
    "ÚT": "Úterý",
    "ST": "Středa",
    "ČT": "Čtvrtek",
    "PÁ": "Pátek",
}

SIRKA = 1800
VYSKA = 1050

FONT = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans.ttf"
FONT_BOLD = "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"

def f(size, bold=False):
    cesta = FONT_BOLD if bold else FONT
    return ImageFont.truetype(cesta, size)

def najdi_font(bold=False):
    nazev = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"

    kandidati = [
        # Termux
        f"/data/data/com.termux/files/usr/share/fonts/truetype/dejavu/{nazev}",

        # Některé linuxové instalace
        f"/usr/share/fonts/truetype/dejavu/{nazev}",
        f"/usr/share/fonts/TTF/{nazev}",

        # Android
        f"/system/fonts/{nazev}",
        f"/system/fonts/Roboto-Regular.ttf" if not bold else
        f"/system/fonts/Roboto-Bold.ttf",
    ]

    for cesta in kandidati:
        if Path(cesta).is_file():
            return cesta

    return None

def minuty(cas):
    h, m = map(int, cas.split(":"))
    return h * 60 + m


def datumy_tyden():
    """
    Vrátí datum pro každý pracovní den aktuálního týdne.
    """

    return {
        den: TYDEN_OD + timedelta(days=i)
        for i, den in enumerate(DNY)
    }


# ============================================================
# 7. KONTROLA, ZDA SE PŘEDMĚT KONÁ
# ============================================================

def zbaF_misto(datum):
    """Vrátí (adresa, místnost) pro konkrétní termín ZBAF1."""
    terminy = {
        date(2026, 9, 24): ("Břehová 7", "215"),
        date(2026, 10, 1): ("Břehová 7", "215"),
        date(2026, 10, 8): ("Břehová 7", "215"),

        date(2026, 10, 15): ("Ruská 87", "503"),
        date(2026, 10, 22): ("Ruská 87", "503"),
        date(2026, 10, 29): ("Ruská 87", "503"),
        date(2026, 11, 5): ("Ruská 87", "503"),

        date(2026, 11, 12): ("Ke Karlovu 4", "seminární m."),
        date(2026, 11, 19): ("Ruská 87", "503"),
        date(2026, 11, 26): ("Ke Karlovu 4", "seminární m."),
        date(2026, 12, 3): ("Ke Karlovu 4", "seminární m."),
        date(2026, 12, 10): ("Ruská 87", "503"),
        date(2026, 12, 17): ("Ke Karlovu 4", "seminární m."),
    }
    return terminy.get(datum, ("", ""))


def predmet_se_kona(predmet, datum):
    """
    Určí, zda se daný předmět v konkrétní den koná.

    EZB a HEB mají pevně stanovené termíny.
    Ostatní předměty se konají podle běžného týdenního rozvrhu.
    """

    # EZB pouze v platných termínech
    if predmet == "EZB":
        return datum in EZB_TERMINY

    # HEB pouze v platných termínech
    if predmet == "HEB":
        return datum in HEB_TERMINY

    # Ostatní předměty se řídí běžným rozvrhem
    return True


def platne_hodiny():
    """
    Vrátí pouze hodiny, které se v aktuálním týdnu skutečně konají.

    Zohledňuje:
    - svátky
    - pevné termíny EZB
    - pevné termíny HEB
    - prioritu EZB před šermem
    """

    vysledek = []

    for hodina in ROZVRH:

        den, zacatek, konec, predmet, vyucujici, mistnost = hodina

        # Datum konkrétního dne
        index_dne = DNY.index(den)
        datum = TYDEN_OD + timedelta(days=index_dne)

        # Svátek – nekoná se nic
        if datum in SVATKY:
            continue

        # EZB pouze v platných termínech
        if predmet == "EZB":
            if datum not in EZB_TERMINY:
                continue

        # HEB pouze v platných termínech
        elif predmet == "HEB":
            if datum not in HEB_TERMINY:
                continue

        # Pokud je v tento den EZB, šerm se nekoná
        elif predmet == "šerm":
            if datum in EZB_TERMINY:
                continue

        vysledek.append(hodina)

    return vysledek


# ============================================================
# 8. TEXT NA STŘED
# ============================================================

def text_na_stred(draw, box, text, font, fill="black"):

    x1, y1, x2, y2 = box

    bb = draw.textbbox(
        (0, 0),
        text,
        font=font
    )

    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]

    draw.text(
        (
            (x1 + x2 - tw) / 2,
            (y1 + y2 - th) / 2 - 2
        ),
        text,
        font=font,
        fill=fill,
    )


# ============================================================
# 9. VYKRESLENÍ
# ============================================================

def vykresli():

    hodiny = platne_hodiny()

    img = Image.new(
        "RGB",
        (SIRKA, VYSKA),
        "white"
    )

    d = ImageDraw.Draw(img)


    # ========================================================
    # NADPIS
    # ========================================================

    d.text(
        (35, 20),
        f"RT — týden od {TYDEN_OD.strftime('%d. %m. %Y')}",
        font=f(30, True),
        fill="black",
    )


    # ========================================================
    # ROZMĚRY TABULKY
    # ========================================================

    levy_okraj = 185
    pravy_okraj = 35
    horni_okraj = 85
    spodni_okraj = 35

    min_cas = 8 * 60
    max_cas = 20 * 60

    pocet_hodin = 12

    sirka_hodiny = (
        SIRKA
        - levy_okraj
        - pravy_okraj
    ) / pocet_hodin

    vyska_dne = (
        VYSKA
        - horni_okraj
        - spodni_okraj
        - 45
    ) / 5

    y0 = horni_okraj + 45


    # ========================================================
    # HLAVIČKA – ČASY
    # ========================================================

    d.rectangle(
        [
            0,
            horni_okraj,
            levy_okraj,
            y0
        ],
        fill="#F1F1F1",
        outline="#AAAAAA",
    )

    text_na_stred(
        d,
        [
            0,
            horni_okraj,
            levy_okraj,
            y0
        ],
        "Den",
        f(17, True),
    )


    for h in range(8, 20):

        x1 = (
            levy_okraj
            + (h - 8) * sirka_hodiny
        )

        x2 = x1 + sirka_hodiny

        d.rectangle(
            [
                x1,
                horni_okraj,
                x2,
                y0
            ],
            fill="#F1F1F1",
            outline="#AAAAAA",
        )

        text_na_stred(
            d,
            [
                x1,
                horni_okraj,
                x2,
                y0
            ],
            f"{h:02d}:00",
            f(15, True),
        )


    # ========================================================
    # SVISLÉ ČASOVÉ ČÁRY
    # ========================================================

    for h in range(13):

        x = (
            levy_okraj
            + h * sirka_hodiny
        )

        d.line(
            [
                x,
                y0,
                x,
                VYSKA - spodni_okraj
            ],
            fill="#D0D0D0",
            width=1,
        )


    # ========================================================
    # DNY
    # ========================================================

    for i, den in enumerate(DNY):

        y1_den = (
            y0
            + i * vyska_dne
        )

        y2_den = y1_den + vyska_dne

        datum = TYDEN_OD + timedelta(days=i)


        # ----------------------------------------------------
        # Název dne
        # ----------------------------------------------------

        d.rectangle(
            [
                0,
                y1_den,
                levy_okraj,
                y2_den
            ],
            fill="#F1F1F1",
            outline="#AAAAAA",
        )

        text_na_stred(
            d,
            [
                0,
                y1_den,
                levy_okraj,
                y2_den
            ],
            f"{NAZVY_DNU[den]}\n"
            f"{datum.strftime('%d. %m.')}",
            f(17, True),
        )


        # ----------------------------------------------------
        # Svátek
        # ----------------------------------------------------

        if datum in SVATKY:

            d.rectangle(
                [
                    levy_okraj,
                    y1_den,
                    SIRKA - pravy_okraj,
                    y2_den
                ],
                fill="#F4F4F4",
            )

            text_na_stred(
                d,
                [
                    levy_okraj,
                    y1_den,
                    SIRKA - pravy_okraj,
                    y2_den
                ],
                SVATKY[datum],
                f(20, True),
                "#777777",
            )


        # ----------------------------------------------------
        # Spodní čára dne
        # ----------------------------------------------------

        d.line(
            [
                0,
                y2_den,
                SIRKA - pravy_okraj,
                y2_den
            ],
            fill="#AAAAAA",
            width=1,
        )


    # ========================================================
    # HODINY
    # ========================================================

    for (
        den,
        zacatek,
        konec,
        predmet,
        vyucujici,
        mistnost
    ) in hodiny:

        i = DNY.index(den)
        datum_hodiny = TYDEN_OD + timedelta(days=i)

        # ZBAF1 má místo podle konkrétního týdne.
        if predmet == "ZBAF1":
            adresa, zbaF_mistnost = zbaF_misto(datum_hodiny)
            if adresa:
                mistnost = f"{adresa}, {zbaF_mistnost}"

        # ----------------------------------------------------
        # Y podle dne
        # ----------------------------------------------------

        y1_den = (
            y0
            + i * vyska_dne
        )

        y2_den = y1_den + vyska_dne

        y1 = y1_den + 5
        y2 = y2_den - 5


        # ----------------------------------------------------
        # X podle času
        # ----------------------------------------------------

        z = minuty(zacatek)
        k = minuty(konec)

        x1 = (
            levy_okraj
            + (z - min_cas)
            / 60
            * sirka_hodiny
            + 4
        )

        x2 = (
            levy_okraj
            + (k - min_cas)
            / 60
            * sirka_hodiny
            - 4
        )


        # ----------------------------------------------------
        # Barvy předmětů
        # ----------------------------------------------------

        barvy = {
            "ZPSP":       "#A8BCD9",
            "MECH":       "#F5B7B9",
            "MECHcv":     "#F5B7B9",
            "MAT1":       "#B7E87D",
            "MAT1cv":     "#B7E87D",
            "EZB":        "#A8BCD9",
            "CH1":        "#BCA8C1",
            "CH1cv":      "#BCA8C1",
            "ZPRO":        "#E3C486",
            "ZM1":         "#F5B7B9",
            "HEB":         "#A8BCD9",
            "DEF1":        "#F5B7B9",
            "Doučování":   "#F3CB49",
            "šerm":        "#728AF5",
            "ZBAF1":       "#A8BCD9",
            "MAM1":        "#C9C9C9",
            "MAM2":        "#C9C9C9",
            "Lezení":      "#00FFFF",
        }

        fill = barvy.get(
            predmet,
            "#E6E6E6"
        )


        # ----------------------------------------------------
        # Blok předmětu
        # ----------------------------------------------------

        d.rectangle(
            [
                x1,
                y1,
                x2,
                y2
            ],
            fill=fill,
            outline="#999999",
            width=1,
        )


        # ----------------------------------------------------
        # Název předmětu
        # ----------------------------------------------------

        text_na_stred(
            d,
            [
                x1 + 5,
                y1 + 3,
                x2 - 5,
                y1 + 35
            ],
            predmet,
            f(17, True),
        )


        # ----------------------------------------------------
        # Vyučující + místnost
        # ----------------------------------------------------

        if x2 - x1 > 100:

            d.line(
                [
                    x1,
                    y2 - 32,
                    x2,
                    y2 - 32
                ],
                fill="#BBBBBB",
                width=1,
            )

            # Vyučující
            d.text(
                [
                    x1 + 7,
                    y2 - 27
                ],
                vyucujici,
                font=f(20),
                fill="#222222",
            )

            # Místnost
            bb = d.textbbox(
                (0, 0),
                mistnost,
                font=f(20)
            )

            tw = bb[2] - bb[0]

            d.text(
                (
                    x2 - tw - 7,
                    y2 - 27
                ),
                mistnost,
                font=f(20),
                fill="#222222",
            )


    # ========================================================
    # PATIČKA
    # ========================================================

    d.text(
        (35, VYSKA - 28),
        "Vygenerováno skriptem",
        font=f(11),
        fill="#AAAAAA",
    )

    return img


# ============================================================
# 10. ULOŽENÍ
# ============================================================

def uloz():

    img = vykresli()
    stem = f"rozvrh_{TYDEN_OD.isoformat()}"
    png = Path(stem + ".png")
    
    img.save(png,quality=95)
    
    print("Hotovo:")
    print(f"  {png}")

# ============================================================
# 11. SPUŠTĚNÍ
# ============================================================

if __name__ == "__main__":
    uloz()
