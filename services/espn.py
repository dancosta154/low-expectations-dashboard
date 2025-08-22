# app/services/espn.py
from __future__ import annotations
from typing import Dict, List, Tuple
import requests
from ..keeper import PlayerRec
from ..config.team_map import TEAM_ID_MAP, SEASONS_KEPT_OVERRIDES

API_HOSTS = [
    "https://lm-api-reads.fantasy.espn.com",  # authenticates reliably
    "https://fantasy.espn.com",  # fallback (may 302)
]
API_PATH = "/apis/v3/games/ffl/seasons/{season}/segments/0/leagues/{league}"


def _cookies(cfg) -> Dict[str, str]:
    # ESPN expects lowercase s2 key
    return {"SWID": cfg["ESPN_SWID"], "espn_s2": cfg["ESPN_S2"]}


def _headers(cfg) -> Dict[str, str]:
    league = cfg["LEAGUE_ID"]
    return {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://fantasy.espn.com/football/league?leagueId={league}",
        "Origin": "https://fantasy.espn.com",
        "x-fantasy-platform": "kona",
        "x-fantasy-source": "kona",
        "Connection": "keep-alive",
    }


def _get_json(cfg, params: Dict[str, str], season: int):
    last_err = None
    for host in API_HOSTS:
        url = host + API_PATH.format(season=season, league=cfg["LEAGUE_ID"])
        r = requests.get(
            url,
            params=params,
            cookies=_cookies(cfg),
            headers=_headers(cfg),
            timeout=25,
            allow_redirects=False,
        )
        ct = r.headers.get("Content-Type", "")
        if 300 <= r.status_code < 400:
            last_err = requests.HTTPError(
                f"Redirected ({r.status_code}) to {r.headers.get('Location')} @ {url}"
            )
            continue
        if r.status_code == 200 and "application/json" in ct:
            return r.json()
        last_err = requests.HTTPError(
            f"{r.status_code} for {url} (CT={ct}) — {(r.text or '')[:200]!r}"
        )
    raise last_err


def _best_final_period(cfg, season: int, hint: int | None) -> int:
    # probe late-season periods; choose the one with the most total rostered entries
    candidates: List[Tuple[int, int]] = []
    for sp in range(22, max(12, (hint or 0)) - 1, -1):  # 22→hint (or 12)
        try:
            data = _get_json(
                cfg, {"view": "mRoster", "scoringPeriodId": str(sp)}, season
            )
        except Exception:
            continue
        total = sum(
            len((t.get("roster") or {}).get("entries") or [])
            for t in data.get("teams", [])
        )
        if total:
            candidates.append((sp, total))
    if candidates:
        candidates.sort(key=lambda x: (x[1], x[0]))  # by total, then highest sp
        return candidates[-1][0]
    return hint or 17


def fetch_league_blob(cfg) -> Dict:
    # For keeper eligibility, we need data from the season that just ended
    # If we're checking eligibility for 2025 season, we need 2024 data
    # So LAST_SEASON should be the season we want data from
    season = cfg["LAST_SEASON"]  # Use the specified season for all data

    settings = _get_json(cfg, {"view": "mSettings"}, season)
    final_sp = (settings.get("status") or {}).get("finalScoringPeriod")
    if not isinstance(final_sp, int) or final_sp <= 0:
        final_sp = 19  # safe fallback for 2023

    # Get draft data from the same season (2023)
    draft = _get_json(cfg, {"view": "mDraftDetail"}, season)

    # IMPORTANT: fetch rosters using only mRoster, at ESPN's final period
    roster = _get_json(
        cfg, {"view": "mRoster", "scoringPeriodId": str(final_sp)}, season
    )

    # Team names/metadata (separate call) - use same season
    teams_meta = _get_json(cfg, {"view": "mTeam"}, season)

    return {
        "settings": settings,
        "draft": draft,
        "roster": roster,
        "teams_meta": teams_meta,
        "final_scoring_period": final_sp,
    }


def build_player_index(cfg) -> Dict[str, PlayerRec]:
    blob = fetch_league_blob(cfg)

    # draft picks → playerId → round
    picks = (blob.get("draft", {}) or {}).get("draftDetail", {}).get("picks", []) or []
    draft_round_by_player: Dict[int, int] = {}
    for p in picks:
        pid, rnd = p.get("playerId"), p.get("roundId")  # Use roundId instead of round
        if isinstance(pid, int) and isinstance(rnd, int):
            draft_round_by_player[pid] = rnd

    players: Dict[int, PlayerRec] = {}
    for t in (blob.get("roster", {}) or {}).get("teams", []) or []:
        espn_tid = t.get("id")
        entries = (t.get("roster", {}) or {}).get("entries", []) or []
        for entry in entries:
            athlete = (entry.get("playerPoolEntry", {}) or {}).get("player", {}) or {}
            pid, full = athlete.get("id"), athlete.get("fullName")
            if not isinstance(pid, int) or not full:
                continue
            rec = players.get(pid) or PlayerRec(pid, full)
            rec.espn_team_id = espn_tid
            rec.final_team_id = TEAM_ID_MAP.get(
                espn_tid
            )  # numeric ESPN id → your internal key
            rec.draft_round = draft_round_by_player.get(pid)
            players[pid] = rec

    for rec in players.values():
        if rec.draft_round is None:
            rec.originally_undrafted = True
    for pid, count in SEASONS_KEPT_OVERRIDES.items():
        if pid in players:
            players[pid].seasons_kept = count

    return {rec.name.lower(): rec for rec in players.values()}


def player_index_by_name(cfg) -> Dict[str, PlayerRec]:
    return build_player_index(cfg)


def dropdown_teams(cfg) -> List[Dict[str, str]]:
    """Return dropdown items built from ESPN team names, mapped to your stable keys."""
    # Use the same season data for team names
    season = cfg["LAST_SEASON"]
    teams_meta = _get_json(cfg, {"view": "mTeam"}, season)
    items = []
    for t in teams_meta.get("teams") or []:
        tid = t.get("id")
        key = TEAM_ID_MAP.get(tid)
        if not key:
            continue
        # Prefer full name; fallback to location+nickname
        name = (
            t.get("name")
            or f"{(t.get('location') or '').strip()} {(t.get('nickname') or '').strip()}".strip()
        )
        items.append({"id": key, "name": name})
    return items
