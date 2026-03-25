"""Classify NPPES facilities for map coverage: Orlando Health, lab corporations, or other."""

from __future__ import annotations

from .business import Facility

# National / regional lab chains (uppercase). Avoid bare "QUEST" (false positives).
_LAB_CORP_NAME_FRAGMENTS: tuple[str, ...] = (
    "QUEST DIAGNOSTICS",
    "QUEST DIAGNOSTIC",
    "LABCORP",
    "LABORATORY CORPORATION",
    "BIO-REFERENCE",
    "BIOREFERENCE",
    "SONORA QUEST",
    "ACL LABORATORIES",
    "ACM LAB",
    "ENZO CLINICAL",
    "EXACT SCIENCES",
    "MYRIAD GENETICS",
    "GENESEQ",
    "SYNLAB",
    "MAYO CLINIC LABORATORIES",
    "ARL PATHOLOGY",
    "PATHGROUP",
    "SHERLOCK BIOSCIENCES",
    "INVITAE",
    "NEOGENOMICS",
)


def is_lab_corporation(f: Facility) -> bool:
    """True for freestanding lab companies (not Orlando Health). Uses name + NUCC."""
    if f.owner == "Orlando Health":
        return False
    tax = (f.taxonomy or "").strip().upper()
    # Clinical / medical laboratory supplier orgs (NUCC 291*)
    if tax.startswith("291"):
        return True
    name = (f.name or "").upper()
    return any(s in name for s in _LAB_CORP_NAME_FRAGMENTS)


def coverage_bucket(f: Facility) -> str:
    """orlando_health | lab_corporation | other_facility"""
    if f.owner == "Orlando Health":
        return "orlando_health"
    if is_lab_corporation(f):
        return "lab_corporation"
    return "other_facility"
