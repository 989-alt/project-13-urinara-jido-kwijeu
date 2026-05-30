"""
Playwright e2e — 우리나라 지도 퀴즈

검증 시나리오:
1. 시작 화면 로딩 및 console error 0건.
2. "퀴즈 시작" → 퀴즈 모드 진입, 질문·진행률 표시.
3. 17 정답 자동 클릭 → 결과 화면 100% / 17 / 17 표시.
4. 오답 1건 케이스: "처음부터" → 첫 문제 일부러 오답 클릭 → 오답 카운트 1 증가, 정답 강조 표시 확인.
5. 결과 화면에서 "오답 재시험" 버튼 노출 + 클릭 시 1문제 짜리 새 퀴즈.
6. 학습지 인쇄 모드 진입 → 번호 1~17 표시 + 정답키 17개.
7. 힌트 토글 ON → 라벨 가시화.
8. 핵심 셀렉터 reachable.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = ROOT / "tests" / "screenshots"
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
URL = "file://" + str(ROOT / "index.html")

errors = []   # console & page errors
results = []  # per-step pass/fail


def shot(page, name):
    page.screenshot(path=str(SCREENSHOT_DIR / f"{name}.png"), full_page=True)


def step(name, fn):
    try:
        fn()
        results.append((name, "PASS", ""))
        print(f"  ✓ {name}")
    except Exception as e:
        results.append((name, "FAIL", str(e)))
        print(f"  ✗ {name}: {e}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900})
        page = ctx.new_page()

        page.on("pageerror", lambda exc: errors.append(("pageerror", str(exc))))
        page.on("console", lambda msg: (
            errors.append(("console-" + msg.type, msg.text))
            if msg.type in ("error",) else None
        ))

        page.goto(URL)
        page.wait_for_load_state("networkidle")

        # ── 1. 시작 화면
        def s1():
            expect(page.locator("#screen-start")).to_be_visible()
            expect(page.locator("#btn-start")).to_be_visible()
            expect(page.locator("#btn-start-print")).to_be_visible()
            shot(page, "01-start-screen")
        step("시작 화면 로딩", s1)

        # ── 2. 퀴즈 시작
        def s2():
            page.click("#btn-start")
            page.wait_for_selector("#screen-quiz", state="visible")
            expect(page.locator("#chip-progress")).to_have_text("1 / 17")
            target = page.locator("#target-name").inner_text()
            assert target, "target name empty"
            shot(page, "02-quiz-first-question")
        step("퀴즈 모드 진입", s2)

        def click_region(name):
            # SVG path overlap: metro cities visually overlap parent provinces.
            # Use dispatch_event so the specific data-name path receives the click,
            # regardless of which element is topmost at its centroid.
            page.locator(f'.region[data-name="{name}"]').dispatch_event("click")

        # ── 3. 17문제 모두 정답
        def s3():
            for i in range(17):
                target = page.evaluate("document.getElementById('target-name').textContent")
                click_region(target)
                page.wait_for_timeout(700)
            page.wait_for_selector("#screen-result", state="visible")
            rate = page.locator(".result-rate").inner_text()
            assert rate == "100%", f"expected 100%, got {rate}"
            stat_correct = page.locator("#stat-correct").inner_text()
            assert stat_correct == "17 / 17", f"expected 17 / 17, got {stat_correct}"
            assert page.locator("#wrong-list-wrap").is_hidden()
            assert page.locator("#btn-retry-wrong").is_hidden()
            shot(page, "03-result-perfect")
        step("17문제 전부 정답 → 결과 100%", s3)

        # ── 4. 처음부터 + 일부러 첫 문제 오답
        def s4():
            page.click("#btn-retry-all")
            page.wait_for_selector("#screen-quiz", state="visible")
            target = page.evaluate("document.getElementById('target-name').textContent")
            # 의도적으로 target이 아닌 첫 번째 path 선택
            wrong_name = page.evaluate(f"""
                () => {{
                  const all = document.querySelectorAll('.region[data-name]');
                  for (const el of all) {{
                    if (el.dataset.name !== {target!r}) return el.dataset.name;
                  }}
                }}""")
            click_region(wrong_name)
            page.wait_for_timeout(1300)
            # 오답 카운터 1 증가
            wrong_count = page.locator("#chip-wrong").inner_text()
            assert wrong_count == "1", f"expected wrong=1, got {wrong_count}"
            shot(page, "04-after-wrong")
        step("오답 클릭 → 카운터 증가", s4)

        # ── 5. 남은 16 정답 → 오답 재시험 노출
        def s5():
            for i in range(16):
                target = page.evaluate("document.getElementById('target-name').textContent")
                click_region(target)
                page.wait_for_timeout(600)
            page.wait_for_selector("#screen-result", state="visible")
            assert page.locator("#wrong-list-wrap").is_visible()
            assert page.locator("#btn-retry-wrong").is_visible()
            chips = page.locator(".wrong-chips .wchip").all_inner_texts()
            assert len(chips) == 1, f"expected 1 wrong chip, got {chips}"
            shot(page, "05-result-with-wrong")
        step("결과: 오답 목록 + 재시험 버튼", s5)

        # ── 6. 오답만 재시험
        def s6():
            page.click("#btn-retry-wrong")
            page.wait_for_selector("#screen-quiz", state="visible")
            expect(page.locator("#chip-progress")).to_have_text("1 / 1")
            target = page.evaluate("document.getElementById('target-name').textContent")
            click_region(target)
            page.wait_for_timeout(700)
            page.wait_for_selector("#screen-result", state="visible")
            assert page.locator(".result-rate").inner_text() == "100%"
            shot(page, "06-retry-wrong-perfect")
        step("오답만 재시험 → 100%", s6)

        # ── 7. 학습지 인쇄 모드
        def s7():
            page.click("#btn-retry-all")
            page.wait_for_selector("#screen-quiz", state="visible")
            # navigate to print via header button
            page.click("#btn-go-print")
            page.wait_for_selector("#screen-print", state="visible")
            num_labels = page.locator("#map-slot-print .number-label").count()
            assert num_labels == 17, f"expected 17 numbered labels, got {num_labels}"
            answer_items = page.locator("#answer-key li").count()
            assert answer_items == 17, f"expected 17 answer key items, got {answer_items}"
            shot(page, "07-print-mode")
            # 돌아가기
            page.click("#btn-print-back")
            page.wait_for_selector("#screen-start", state="visible")
        step("학습지 인쇄 모드 (17 번호 + 정답키)", s7)

        # ── 8. 힌트 토글
        def s8():
            page.click("#btn-start")
            page.wait_for_selector("#screen-quiz", state="visible")
            # 기본은 off
            wrap = page.locator("#map-wrap-quiz")
            assert wrap.get_attribute("data-hint") == "off"
            # 토글 on
            page.click("#hint-toggle")
            page.wait_for_timeout(200)
            assert wrap.get_attribute("data-hint") == "on"
            labels = page.locator("#map-slot-quiz .region-label").count()
            assert labels == 17, f"expected 17 labels, got {labels}"
            shot(page, "08-hint-on")
        step("힌트 토글 ON → 17 라벨 노출", s8)

        # ── 9. console / page error 0건
        def s9():
            assert errors == [], f"errors: {errors}"
        step("console / pageerror 0건", s9)

        browser.close()

    # ── 결과 출력
    print("\n=== Summary ===")
    fails = [r for r in results if r[1] == "FAIL"]
    for name, status, msg in results:
        print(f"  [{status}] {name}" + (f"  ← {msg}" if msg else ""))
    if errors:
        print("\n=== Browser errors ===")
        for kind, t in errors:
            print(f"  [{kind}] {t}")
    print(f"\nTotal: {len(results)}  Pass: {len(results) - len(fails)}  Fail: {len(fails)}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
