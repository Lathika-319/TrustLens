import re
import html
import difflib
import requests
import pandas as pd


NGL_URL = "https://nextgenerationliquefaction.org/mapping/list-view"
P2_FILE = r"data\raw\Database 7.xlsx"

OUT_FILE = r"outputs\kayen_ngl_matching.csv"


def clean_text(x):
    x = html.unescape(str(x))
    x = x.lower()
    x = re.sub(r"[^a-z0-9]+", " ", x)
    x = re.sub(r"\s+", " ", x).strip()
    return x


def extract_ngl_sites(page):
    """
    Extract:
      NGL site ID
      site name
      latitude
      longitude
      reviewed status

    Each NGL site is represented by an <h2> block followed
    by its site table.
    """

    option_pattern = re.compile(
        r'<option value="([0-9]+)">([^<]+)</option>',
        re.I
    )

    option_sites = {
        int(site_id): html.unescape(name).strip()
        for site_id, name in option_pattern.findall(page)
    }

    heading_pattern = re.compile(
        r"<h2>(.*?)</h2>(.*?)(?=<h2>|$)",
        re.I | re.S
    )

    records = []

    for raw_name, block in heading_pattern.findall(page):
        name = html.unescape(re.sub(r"<.*?>", "", raw_name)).strip()

        # Latitude / longitude from first table row
        coord = re.search(
            r"<td>\s*([-+]?\d+(?:\.\d+)?)\s*</td>\s*"
            r"<td>\s*([-+]?\d+(?:\.\d+)?)\s*</td>",
            block,
            re.I | re.S
        )

        if not coord:
            continue

        lat = float(coord.group(1))
        lon = float(coord.group(2))

        # Site ID from download link
        id_match = re.search(
            r"/downloads/download-site-file/(\d+)",
            block,
            re.I
        )

        site_id = int(id_match.group(1)) if id_match else None

        # Reviewed badge
        reviewed = bool(
            re.search(r"&check;|badge-success", block, re.I)
        )

        records.append({
            "ngl_site_id": site_id,
            "ngl_site": name,
            "ngl_latitude": lat,
            "ngl_longitude": lon,
            "ngl_reviewed": reviewed,
        })

    # Remove duplicate headings if any
    result = pd.DataFrame(records).drop_duplicates(
        subset=["ngl_site_id", "ngl_site"],
        keep="first"
    )

    return result


def token_overlap(a, b):
    a_tokens = set(clean_text(a).split())
    b_tokens = set(clean_text(b).split())

    if not a_tokens or not b_tokens:
        return 0.0

    return len(a_tokens & b_tokens) / min(len(a_tokens), len(b_tokens))


def main():

    print("Downloading NGL mapping page...")
    response = requests.get(NGL_URL, timeout=60)
    response.raise_for_status()

    ngl = extract_ngl_sites(response.text)

    print("NGL coordinate records:", len(ngl))

    print("\nLoading Kayen database...")
    p2 = pd.read_excel(
        P2_FILE,
        sheet_name="Liq database"
    )

    kayen = p2[
        (p2["Reference"].astype(str).str.strip() == "Kayen et al. (2013)") &
        (p2["Country"].astype(str).str.strip() == "Japan")
    ].copy()

    kayen["kayen_site"] = kayen["Site"].astype(str)

    unique_sites = kayen[
        ["kayen_site", "Region", "Mw", "PGA(g)", "L"]
    ].drop_duplicates(subset=["kayen_site"])

    print("Unique Japan Kayen sites:", len(unique_sites))

    results = []

    ngl_names = ngl["ngl_site"].tolist()

    for _, row in unique_sites.iterrows():

        kayen_name = row["kayen_site"]
        kayen_clean = clean_text(kayen_name)

        # Exact normalized match
        exact = ngl[
            ngl["ngl_site"].map(clean_text) == kayen_clean
        ]

        if len(exact) > 0:
            for _, n in exact.iterrows():
                results.append({
                    **row.to_dict(),
                    **n.to_dict(),
                    "match_type": "EXACT",
                    "similarity": 1.0,
                    "token_overlap": 1.0,
                })
            continue

        # Fuzzy candidate search
        candidates = []

        for name in ngl_names:
            similarity = difflib.SequenceMatcher(
                None,
                kayen_clean,
                clean_text(name)
            ).ratio()

            overlap = token_overlap(kayen_name, name)

            # Conservative candidate threshold
            if similarity >= 0.70 or overlap >= 0.50:
                candidates.append(
                    (similarity, overlap, name)
                )

        candidates.sort(
            key=lambda x: (x[0], x[1]),
            reverse=True
        )

        # Keep only top 3 candidates
        for similarity, overlap, name in candidates[:3]:

            n = ngl[
                ngl["ngl_site"] == name
            ]

            for _, nr in n.iterrows():

                results.append({
                    **row.to_dict(),
                    **nr.to_dict(),
                    "match_type": "CANDIDATE",
                    "similarity": round(similarity, 4),
                    "token_overlap": round(overlap, 4),
                })

        # If nothing reasonable exists, retain explicit unmatched row
        if not candidates:
            results.append({
                **row.to_dict(),
                "ngl_site_id": None,
                "ngl_site": None,
                "ngl_latitude": None,
                "ngl_longitude": None,
                "ngl_reviewed": None,
                "match_type": "UNMATCHED",
                "similarity": 0.0,
                "token_overlap": 0.0,
            })

    matches = pd.DataFrame(results)

    matches.to_csv(
        OUT_FILE,
        index=False
    )

    print("\nSaved:", OUT_FILE)

    print("\nMatch type counts:")
    print(
        matches["match_type"]
        .value_counts()
        .to_string()
    )

    print("\nTop candidate matches:")
    cols = [
        "kayen_site",
        "ngl_site",
        "similarity",
        "token_overlap",
        "ngl_latitude",
        "ngl_longitude",
        "ngl_reviewed",
        "match_type",
    ]

    print(
        matches[
            matches["match_type"] != "UNMATCHED"
        ][cols]
        .sort_values(
            ["similarity", "token_overlap"],
            ascending=False
        )
        .head(50)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()