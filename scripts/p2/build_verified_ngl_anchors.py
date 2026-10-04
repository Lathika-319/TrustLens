import math
import pandas as pd


OUT = r"outputs\verified_ngl_anchors.csv"


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0088

    p1 = math.radians(lat1)
    p2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1)
        * math.cos(p2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


# ---------------------------------------------------------
# VERIFIED / STRONG NGL GEOGRAPHIC ANCHORS
#
# IMPORTANT:
# These are NOT claiming that every Kayen sub-site has
# this exact coordinate.
#
# They represent verified geographic anchors for groups
# of historical case histories.
# ---------------------------------------------------------

anchors = [
    # ---------------- KOBE ----------------

    {
        "scenario": "Kobe",
        "anchor_group": "Port Island",
        "ngl_site": "Port Island",
        "latitude": 34.673385,
        "longitude": 135.205767,
        "evidence": "NGL mapped Port Island; multiple Kayen records explicitly name Port Island",
        "match_level": "AREA_ANCHOR",
    },

    {
        "scenario": "Kobe",
        "anchor_group": "Port Island",
        "ngl_site": "Port Island Site I",
        "latitude": 34.676456,
        "longitude": 135.206203,
        "evidence": "NGL mapped Port Island site; Kayen contains multiple Port Island case histories",
        "match_level": "AREA_ANCHOR",
    },

    {
        "scenario": "Kobe",
        "anchor_group": "Nishinomiya",
        "ngl_site": "Nishinomiya-hama",
        "latitude": 34.716105,
        "longitude": 135.333039,
        "evidence": "NGL mapped Nishinomiya-hama; Kayen contains numerous Nishinomiya/Nishinomiyahama records",
        "match_level": "AREA_ANCHOR",
    },

    # ---------------- NIIGATA ----------------

    {
        "scenario": "Niigata-Chuetsu",
        "anchor_group": "Kawagishi-cho",
        "ngl_site": "Kawagishi-cho",
        "latitude": 37.910429,
        "longitude": 139.027858,
        "evidence": "NGL mapped Kawagishi-cho; Kayen contains Meikun High School Hiroba, Kawagishi-Cho",
        "match_level": "STRONG_SITE_ANCHOR",
    },

    {
        "scenario": "Niigata-Chuetsu",
        "anchor_group": "Showa Bridge",
        "ngl_site": "Site E (Showa Bridge, Left Bank)",
        "latitude": 37.913780,
        "longitude": 139.042030,
        "evidence": "NGL mapped Showa Bridge left bank; Kayen contains South Bank Shinano River, Showa Bridge",
        "match_level": "STRONG_SITE_ANCHOR",
    },

    {
        "scenario": "Niigata-Chuetsu",
        "anchor_group": "Showa Bridge",
        "ngl_site": "Site F (Showa Bridge, Right Bank)",
        "latitude": 37.910380,
        "longitude": 139.042880,
        "evidence": "NGL mapped Showa Bridge right bank; same named Kayen case-history area",
        "match_level": "STRONG_SITE_ANCHOR",
    },

    # ---------------- TOHOKU ----------------

    {
        "scenario": "Tohoku-Oki",
        "anchor_group": "Aomori",
        "ngl_site": "Aomori Railway Station",
        "latitude": 40.828947,
        "longitude": 140.734833,
        "evidence": "NGL mapped Aomori Railway Station; Kayen contains Aomori Station",
        "match_level": "STRONG_SITE_ANCHOR",
    },

    {
        "scenario": "Tohoku-Oki",
        "anchor_group": "Takeda",
        "ngl_site": "Takeda Elementary School",
        "latitude": 40.934310,
        "longitude": 140.415037,
        "evidence": "Exact Kayen/NGL site-name match",
        "match_level": "EXACT",
    },

    {
        "scenario": "Tohoku-Oki",
        "anchor_group": "Arahama",
        "ngl_site": "Arahama (A-9, Sewage Plant)",
        "latitude": 38.042580,
        "longitude": 140.919003,
        "evidence": "Strong Kayen/NGL site-name match",
        "match_level": "STRONG_SITE_ANCHOR",
    },

    {
        "scenario": "Tohoku-Oki",
        "anchor_group": "Yuriage",
        "ngl_site": "Yuriagekami",
        "latitude": 38.189551,
        "longitude": 140.934866,
        "evidence": "NGL mapped Yuriage area; Kayen contains Yuriage case histories",
        "match_level": "AREA_ANCHOR",
    },

    {
        "scenario": "Tohoku-Oki",
        "anchor_group": "Yuriage",
        "ngl_site": "Yuriage Bridge",
        "latitude": 38.182134,
        "longitude": 140.946729,
        "evidence": "NGL mapped Yuriage Bridge; Kayen contains Yuriage-Ohashi",
        "match_level": "STRONG_SITE_ANCHOR",
    },
]


# ---------------------------------------------------------
# QuakeShield earthquake epicenters
# ---------------------------------------------------------

earthquakes = {
    "Kobe": {
        "earthquake_latitude": 34.583,
        "earthquake_longitude": 135.018,
        "magnitude": 6.9,
    },

    "Niigata-Chuetsu": {
        "earthquake_latitude": 37.226,
        "earthquake_longitude": 138.779,
        "magnitude": 6.6,
    },

    "Tohoku-Oki": {
        "earthquake_latitude": 38.297,
        "earthquake_longitude": 142.373,
        "magnitude": 9.1,
    },
}


rows = []

for a in anchors:

    eq = earthquakes[a["scenario"]]

    distance = haversine_km(
        eq["earthquake_latitude"],
        eq["earthquake_longitude"],
        a["latitude"],
        a["longitude"],
    )

    rows.append({
        **a,
        "earthquake_latitude": eq["earthquake_latitude"],
        "earthquake_longitude": eq["earthquake_longitude"],
        "earthquake_magnitude": eq["magnitude"],
        "distance_to_epicenter_km": round(distance, 3),
    })


df = pd.DataFrame(rows)

df.to_csv(OUT, index=False)

print("\nSaved:", OUT)

print("\nVerified NGL anchors:")
print(
    df[
        [
            "scenario",
            "anchor_group",
            "ngl_site",
            "match_level",
            "distance_to_epicenter_km",
        ]
    ].to_string(index=False)
)

print("\nAnchor counts:")
print(
    df.groupby("scenario")
      .size()
      .to_string()
)