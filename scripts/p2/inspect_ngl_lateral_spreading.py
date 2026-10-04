import getpass
import json
import requests
import pandas as pd

BASE_URL = "https://nextgenerationliquefaction.org"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    ),
}


def get_token():
    print("=" * 70)
    print("NGL API AUTHENTICATION")
    print("=" * 70)

    email = input("NGL email/username: ").strip()
    password = getpass.getpass("NGL password: ")

    url = f"{BASE_URL}/users/api-token"

    response = requests.get(
        url,
        headers=HEADERS,
        auth=(email, password),
        timeout=30,
    )

    if response.status_code != 200:
        print("\nNGL authentication failed.")
        print("Status:", response.status_code)
        print(response.text)
        raise SystemExit(1)

    payload = response.json()
    token = payload.get("token")

    if not token:
        print("Token was not returned.")
        print(payload)
        raise SystemExit(1)

    print("\nNGL authentication: PASS")
    print("Temporary token obtained.")

    return token


def api_get(token, endpoint, params=None):
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {token}"

    url = f"{BASE_URL}{endpoint}"

    response = requests.get(
        url,
        headers=headers,
        params=params or {},
        timeout=60,
    )

    if response.status_code != 200:
        print("\nAPI request failed")
        print("Endpoint:", endpoint)
        print("Status:", response.status_code)
        print(response.text)
        raise SystemExit(1)

    return response.json()


def inspect_endpoint(token, name, endpoint):
    print("\n" + "=" * 70)
    print(name)
    print(endpoint)
    print("=" * 70)

    rows = api_get(
        token,
        endpoint,
        {
            "limit": 5,
            "page": 1,
            "includeUnreviewed": 0,
        },
    )

    print("Rows returned:", len(rows))

    if not rows:
        print("No rows returned.")
        return

    df = pd.DataFrame(rows)

    print("\nColumns:")
    for column in df.columns:
        print("  -", column)

    print("\nFirst rows:")
    print(df.head().to_string(index=False))


def main():
    token = get_token()

    inspect_endpoint(
        token,
        "SITES",
        "/sites/api-index",
    )

    inspect_endpoint(
        token,
        "EVENTS",
        "/events/api-index",
    )

    inspect_endpoint(
        token,
        "LIQUEFACTION MANIFESTATIONS",
        "/liquefaction-manifestations/api-index",
    )

    inspect_endpoint(
        token,
        "DISPLACEMENT VECTORS",
        "/displacement-vectors/api-index",
    )

    inspect_endpoint(
        token,
        "GROUND MOTION",
        "/ground-motion-intensity-measurements/api-index",
    )


if __name__ == "__main__":
    main()