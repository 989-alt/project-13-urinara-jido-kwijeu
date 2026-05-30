# UI/UX 설계 — 우리나라 지도 퀴즈

## 디자인 브랜드: Airbnb (메인) + Linear (보조)

이유:
- **Airbnb** — 토픽이 "지리감"이라는 친숙한 마켓플레이스적 탐색 감각. 흰 캔버스 + 단일 voltage(Rausch #ff385c)로 정·오답·CTA 모두 표현.
- **Linear** (보조) — 진행 표시(progress chip), 결과 통계 카드의 단정한 수치 정렬.

## 화면 구조 (3 모드 + 1 결과)

```
┌─────────────────────────────────────────┐
│  [로고] 우리나라 지도 퀴즈   [학습지 인쇄]│  ← top-nav
├─────────────────────────────────────────┤
│                                          │
│   "강원특별자치도를 찾으세요"            │  ← 출제 카드
│   [진행: 5 / 17]  [정답 3]  [오답 1]     │
│                                          │
│         ┌─────────────────┐              │
│         │                  │              │
│         │   SVG 지도       │              │
│         │  (클릭 가능 17 광역)│            │
│         │                  │              │
│         └─────────────────┘              │
│                                          │
│   [힌트: 시·도 이름 표시]                 │  ← 토글 chip
└─────────────────────────────────────────┘
```

### 모드
1. **시작 화면** — 큰 타이틀 + "퀴즈 시작" 1차 CTA + "학습지 인쇄" 2차 CTA.
2. **퀴즈 진행** — 출제·지도·진행률.
3. **결과 화면** — 정답률·소요 시간·오답 목록·"오답 재시험"·"처음부터".
4. **인쇄 모드** — 지도만 (시·도 이름 없음, 번호만), `@media print`로 UI 제거.

## 색·타이포 결정 (Airbnb 토큰 차용)

| 역할 | 색 | 사용처 |
|---|---|---|
| Primary CTA | #ff385c (Rausch) | "퀴즈 시작", "다음 문제", "재도전" |
| Primary Active | #e00b41 | 버튼 press |
| Ink | #222222 | 본문·헤딩 |
| Body | #3f3f3f | 부가 설명 |
| Muted | #6a6a6a | "현재 문제 N/17" 라벨 |
| Canvas | #ffffff | 페이지 배경 |
| Surface Soft | #f7f7f7 | 지도 영역 기본 채우기 |
| Surface Strong | #f2f2f2 | 미답 시·도 path |
| Hairline | #dddddd | 시·도 경계선 |
| Correct (자체) | #008a05 (초록, 4.5:1 OK on white) | 정답 영역 일시 채우기 |
| Wrong (자체) | #c13515 (Airbnb error red) | 오답 영역 |
| Highlight | #ffb400 (보조 노랑) | 오답 후 정답 위치 외곽선 |

타이포(시스템 폴백, Cereal·Inter 없으니 system stack):
- 헤딩 28px / 700 → 문제 제시문(예: "강원특별자치도를 찾으세요")
- 본문 16px / 400 → 안내·버튼
- 캡션 14px / 500 → 진행률·결과 stats
- 결과 정답률 64px / 700 → Airbnb의 rating-display 차용 (커다란 숫자 trust signal)

폰트 스택 (CDN 0):
```
font-family: -apple-system, "Apple SD Gothic Neo", "Pretendard", system-ui,
             "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans KR", sans-serif;
```

## 모서리·간격

- 버튼: 8px (Airbnb rounded.sm)
- 카드 (출제·결과): 14px (rounded.md)
- 칩 / 배지 (진행률, 정/오답 카운터): 9999px (rounded.full)
- spacing: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 (Airbnb 토큰)

## 핵심 컴포넌트

### 1. 출제 카드 (`question-card`)
- 흰색 배경, 14px 라운드, 24px padding.
- 28px / 700 ink 헤딩("○○을 찾으세요").
- 우측: 진행률 chip (white 배경, 1px hairline 보더, 14px / 500).

### 2. 지도 (`korea-svg-map`)
- viewBox 800×800, 흰 캔버스.
- 17개 path: 기본 fill `#f2f2f2`(Surface Strong), stroke `#dddddd` 1px.
- :hover → fill `#f7f7f7` + cursor pointer.
- :focus-visible → 2px 검정 dashed outline (키보드 접근성).
- 정답 클릭 → 0.4s 동안 `#008a05` 80% opacity overlay.
- 오답 클릭 → 클릭 path `#c13515` 60% opacity 0.4s + 정답 path `#ffb400` 외곽선 1s.

### 3. 진행 chip + 카운터
- 좌: "5 / 17" 진행률 (Linear inspired — 단정한 수치).
- 우: "정답 N" 초록 점, "오답 N" 빨강 점 (작은 dot 4px + 14px 텍스트).

### 4. 결과 카드
- 64px / 700 정답률 (예: "94%") — Airbnb rating-display 미러.
- 그 아래 통계 row: "17문제 중 16문제 정답 · 1분 23초 소요".
- 오답 목록: 칩 그리드 ("강원특별자치도", "경상북도" 칩).
- "오답 재시험" primary CTA + "처음부터" secondary.

### 5. 학습지 인쇄 모드
- 단독 페이지(별도 라우트 X — body class 토글).
- `@media print`: 헤더·푸터·버튼 `display: none`, 지도는 A4 가운데, path stroke `#000`, fill `#fff`.
- 번호 라벨: 각 시·도 path 중심점에 ①②③ 같은 원형 번호 + 페이지 하단에 정답 목록.

## 접근성 결정

- 모든 path에 `role="button"`, `tabindex="0"`, `aria-label="{시·도 이름} 영역 클릭"`.
- 출제 텍스트는 `aria-live="polite"`로 변경 시 스크린리더에 알림.
- 색만으로 정·오답 구분하지 않음 — 정답 시 ✓ 아이콘 + 오답 시 ✗ 아이콘 + 정답 영역 텍스트 라벨.
- 대비 4.5:1 모두 충족: ink #222 on white = 16.1:1, Rausch on white CTA text white = 5.4:1 (대신 size > 18px), green #008a05 on white = 4.7:1.
- `prefers-reduced-motion`: 깜빡임·트랜지션 0으로.
- 키보드: Tab으로 path 순회, Enter/Space로 "클릭" 트리거.
- focus-visible: 검정 2px dashed outline.

## 인터랙션 상태표

| 상태 | 시각 |
|---|---|
| 미답 path | fill #f2f2f2, stroke #ddd 1px |
| Hover | fill #f7f7f7, cursor pointer |
| Focus (키보드) | 2px dashed #222 outline |
| 정답 click | fill #008a05 (0.4s ease-out, fade) |
| 오답 click | 클릭 fill #c13515 (0.4s) + 정답 outline #ffb400 dashed 3px (1s) |
| 출제 완료된 시·도 | fill #ebebeb (Hairline Soft) — 비활성 |

## design.md vs ui-ux-pro-max 충돌
- ui-ux-pro-max의 "no-emoji-icons" → 본 프로젝트 SVG inline icon만 사용 (✓ ✗ 도 SVG).
- design.md의 "Rausch 단일 voltage" 우선 → 모든 primary CTA Rausch, 오직 정/오답 피드백만 별색 (의미적 분리).
