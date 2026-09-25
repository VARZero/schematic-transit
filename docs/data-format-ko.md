# JSON 데이터 구조

[English version](data-format-en.md) · **한국어**

[← 첫 화면](../README.md) · [설치와 사용법](installation-ko.md) · [부산권 예제 데이터](../data/network.json) · [최소 예제](../examples/minimal.json)

노선도는 하나의 JSON 파일로 정의합니다. 아래 좌표는 실제 위도·경도가 아닌 **그림 안의 위치**입니다.

## 전체 예시

```json
{
  "title": "예제 노선도",
  "as_of": "2026-09-26",
  "footer": "실선 운행 · 점선 계획 | 실제 거리와 다름",
  "positions": {"A": [0, 0], "C": [8, 4], "E": [8, 8]},
  "labels": {"C": "중앙역"},
  "label_offsets": {"C": [0.5, 1.0]},
  "lines": [
    {
      "id": "red",
      "name": "빨간선",
      "status": "open",
      "color": "#d84a4a",
      "stations": ["A", "B", "C"],
      "anchors": {"B": [4, 4]},
      "bend_order": "diagonal_first"
    },
    {
      "id": "blue",
      "name": "파란선",
      "status": "planned",
      "color": "#3478ba",
      "stations": ["C", "D", "E"]
    }
  ]
}
```

## 최상위 필드

| 필드 | 필수 | 의미 |
| --- | --- | --- |
| `lines` | 예 | 노선 배열. 각 노선에 역 2개 이상 필요 |
| `positions` | 조건부 | 공통 환승역과 각 노선 양끝 역의 `[x, y]` 좌표. 양끝 역은 노선의 `anchors`로 대신 지정 가능 |
| `title` | 아니요 | 노선도 제목 |
| `as_of` | 아니요 | 기준 날짜 등 부제에 표시할 텍스트 |
| `footer` | 아니요 | 하단 설명 문구 |
| `labels` | 아니요 | 역 ID와 다른 표기명을 사용할 때 `{역ID: 표시명}` |
| `label_offsets` | 아니요 | 겹치는 역명의 위치 조정값 `{역ID: [가로, 세로]}` |

같은 역이 여러 노선에 등장하면 **같은 역 ID**를 쓰고 그 역의 좌표를 `positions`에 한 번 지정합니다. 이름이 같아도 실제로 다른 역이면 서로 다른 ID를 쓰고 `labels`로 원하는 표기명을 지정할 수 있습니다.

## 노선별 필드

| 필드 | 필수 | 의미 |
| --- | --- | --- |
| `id` | 예 | 중복되지 않는 노선 ID |
| `name` | 예 | 범례에 표시할 노선 이름 |
| `status` | 예 | `open`(운행), `planned`(계획), `concept`(구상) |
| `color` | 예 | 선 색상. 예: `#d84a4a` |
| `stations` | 예 | 운행 순서대로 나열한 역 ID 배열 |
| `anchors` | 아니요 | 노선 중간에서 위치를 고정할 역과 `[x, y]` 좌표 |
| `bend_order` | 아니요 | `diagonal_first`(기본값) 또는 `axial_first` |
| `note` | 아니요 | 데이터에 보관하는 메모. 현재 지도에는 직접 출력하지 않음 |

## 좌표와 배치 방식

배치기는 인접한 기준점 사이를 수평·수직·45° 선분으로 잇습니다. `diagonal_first`는 대각선 방향으로 먼저 이동하고, `axial_first`는 수평·수직 방향으로 먼저 이동합니다. 중간 역은 만들어진 경로 위에 순서대로 배치합니다. 기준점을 늘리면 노선 모양을 더 세밀하게 정할 수 있습니다.

역 표식은 경로 위에 놓이지만 역 사이에 꺾임점이 있을 수 있습니다. 따라서 선을 다시 그릴 때는 역 좌표만 직접 이어 붙이지 말고, 배치 결과의 `paths`를 사용해야 합니다. [배치 코드](../src/schematic_transit/layout.py)와 [렌더러](../src/schematic_transit/render.py)가 이를 처리합니다.

두 노선 이상이 정확히 같은 직선 구간을 공유하면 [겹침 구간 검출기](../src/schematic_transit/overlap.py)가 겹친 부분을 찾습니다. 렌더러는 그 구간을 넓혀 노선별 색을 나란히 그리며, 양끝에서는 원래 중심선으로 모아 합류와 분기가 이어져 보이게 합니다. [세 노선 겹침 예제](../examples/overlap.json)를 참고하세요.

현재 버전은 **전체 노선의 교차나 역명 겹침을 자동 최적화하지 않습니다.** 노선 모양은 `positions`와 `anchors`로, 역명 위치는 `label_offsets`로 조정합니다. 잘못된 상태 값, 중복 노선 ID, 좌표가 없는 환승역 등은 [데이터 모델](../src/schematic_transit/model.py)에서 오류로 알려줍니다.

[← 첫 화면](../README.md) · [설치와 사용법 →](installation-ko.md)
