import csv
import requests
import pytest
import os

BACKEND_URL = "https://rag-eval-backend.onrender.com/api/chat"

def load_test_cases():
    print('current path:', os.getcwd())
    # test_dir = os.path.dirname(__file__)
    # test_cases_path = os.path.join(test_dir, "test_case.csv")
    with open("./test_case.csv", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

@pytest.mark.parametrize("case", load_test_cases(), ids=lambda c: c["id"])
def test_chatbot_answer(case):
    resp = requests.post(BACKEND_URL, json={"message": case["question"]}, timeout=60)
    resp.raise_for_status()
    actual = resp.json().get("answer", "").lower()

    # simple keyword check: does the answer contain the key expected fact?
    expected = case["expected_answer"].lower()
    assert expected in actual, (
        f"\n{case['id']} FAILED"
        f"\nQ: {case['question']}"
        f"\nExpected to contain: {expected}"
        f"\nGot: {actual}"
    )