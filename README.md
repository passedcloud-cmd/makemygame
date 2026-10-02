# MakeMyGame (가제)

누군가의 무의식 세계에 갇힌 세 사람이 현실로 돌아가기 위해 탐험하는 탑다운 스토리 게임.
Godot 4로 만들고 스팀 출시를 목표로 한다.

## 실행 방법

1. [Godot 4.7 이상](https://godotengine.org/download) 표준(Standard) 버전을 받는다. (.NET 버전은 필요 없음)
2. Godot를 켜고 **가져오기(Import)** → 이 폴더의 `project.godot` 선택
3. 에디터가 열리면 오른쪽 위 ▶ 버튼(또는 `F5`)으로 실행

## 조작

| 키 | 기능 | 게임패드 |
|---|---|---|
| 방향키 | 이동 | 십자키 / 왼쪽 스틱 |
| Z | 조사 / 대화 넘기기 (조사할 게 없으면 공격) | A |
| X | 보조 스킬 / 취소 | X / B |
| C | 특수 행동 (미정) | Y |
| Esc | 메뉴 | Start |

지금은 이동, 조사, 대화, 선택지, 기본 공격, 문으로 방 이동이 동작한다. 스킬(X, C)은 이름만 등록해 둔 상태.

테스트 방 구성:
- **방 1** (`test_room.tscn`): 상자 조사, 선택지. 위쪽 가운데 문으로 방 2에 갈 수 있다.
- **방 2** (`test_room_2.tscn`): 그림자 몬스터 2마리. 3번 때리면 사라지고, 닿으면 하트가 1개 줄어든다.
  하트가 다 떨어지면 (지금은 임시로) 체력을 채우고 방을 처음부터 다시 시작한다.

## 화면 설정

- 게임 화면은 **640×360**으로 그리고, 모니터에 맞춰 정수 배(2배, 3배…)로 키운다.
- 도트가 뭉개지지 않도록 텍스처 필터는 Nearest(최근접)로 설정돼 있다.
- 스탠딩 일러, CG처럼 고해상도 그림은 1920×1080 기준으로 그려서 넣으면 선명하게 보인다.

## 폴더 구조

```
art/
  sprites/test/   임시 캐릭터 도트 (A, B, C) - 나중에 직접 그린 걸로 교체
  portraits/      대화창 얼굴 그림 (A.png, A_smile.png ...)
  tiles/test/     임시 바닥, 벽, 상자
  fonts/galmuri/  한글 도트 폰트 (갈무리11, OFL 라이선스 - 상업 게임에 써도 됨)
dialogue/         대본 파일 (.txt). 쓰는 법은 dialogue/README.md
scenes/
  characters/     player.tscn (주인공), follower.tscn (따라오는 동료)
  maps/           맵 장면들, 문(door.tscn). test_room*.tscn = 테스트용 방
  monsters/       몬스터 장면
  props/          상자, 조사 영역(interactable.tscn) 같은 소품
  ui/             대화창, 체력 하트, 화면 전환, 비네팅, 테마(폰트/글자색)
scripts/
  autoload/       게임 전체에서 쓰는 것 (GameState = 체력/호감도, Transition = 방 이동)
  combat/         몬스터 코드
  characters/     캐릭터 이동, 애니메이션 코드
  dialogue/       대화창, 대본 읽기 코드
  maps/           맵 공통 코드, 문, 도착 지점
  props/          소품 코드
shaders/          화면 효과 (비네팅 등)
tools/            임시 그림을 만드는 파이썬 스크립트
```

> 나중에 게임을 내보낼(Export) 때 `dialogue/*.txt` 파일이 포함되도록
> 내보내기 설정의 "리소스 외 파일 포함" 칸에 `*.txt`를 넣어야 한다.

## 캐릭터 도트 규격

- 한 칸 **32×48** 픽셀, 발끝이 아래에서 2번째 줄(y=46)에 오도록 그린다.
- 시트 한 장에 **3열 × 4행**:
  - 행: 아래(정면), 왼쪽, 오른쪽, 위(뒷모습)
  - 열: 걷기1, 서 있기, 걷기2
- 이 규격만 맞추면 `art/sprites/test/*.png`를 덮어쓰는 것만으로 게임에 바로 반영된다.

## 새 방 만들기

1. `scenes/maps/test_room_2.tscn`을 복사해서 이름을 바꾼다.
2. 방 노드의 `Room Size`(방 크기), `Ambient Color`(밝기/색감)를 정한다.
3. **문**: `scenes/maps/door.tscn`을 놓고 `Target Scene`(갈 방), `Target Spawn`(도착 지점 이름)을 정한다.
4. **도착 지점**: `Spawns` 아래에 Marker2D를 만들고 `scripts/maps/spawn_point.gd`를 붙인다.
   노드 이름이 곧 지점 이름이고, `Facing`으로 도착했을 때 바라볼 방향을 정한다.
5. 문 판정 영역과 도착 지점은 겹치지 않게 떨어뜨려 둔다. (겹치면 도착하자마자 다시 이동해 버림)
