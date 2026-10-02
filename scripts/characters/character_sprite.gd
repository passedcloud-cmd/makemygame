class_name CharacterSprite
extends Sprite2D
## 캐릭터 도트의 걷기 애니메이션을 재생한다.
##
## 스프라이트 시트 배치 (RPG 메이커 방식):
##   행(가로줄) = 아래, 왼쪽, 오른쪽, 위
##   열(세로줄) = 걷기1, 서 있기, 걷기2

enum Facing { DOWN, LEFT, RIGHT, UP }

## 걷기1 → 서 있기 → 걷기2 → 서 있기 순서로 반복
const WALK_CYCLE: Array[int] = [0, 1, 2, 1]
const STAND := 1

## 1초에 몇 프레임씩 넘길지 (클수록 발이 빨라 보임)
@export var walk_fps := 7.0

var facing: Facing = Facing.DOWN
## true면 걷는 애니메이션, false면 서 있는 모습
var moving := false

var _walk_time := 0.0


func _ready() -> void:
	hframes = 3
	vframes = 4
	_update_frame()


func _process(delta: float) -> void:
	_walk_time = _walk_time + delta if moving else 0.0
	_update_frame()


## 이동 방향을 보고 캐릭터가 바라볼 방향을 정한다.
func face_towards(dir: Vector2) -> void:
	if dir.is_zero_approx():
		return
	var horizontal := Facing.RIGHT if dir.x > 0 else Facing.LEFT
	var vertical := Facing.DOWN if dir.y > 0 else Facing.UP
	# 대각선으로 움직일 때는 지금 보고 있는 방향을 유지해서 깜빡이지 않게 한다.
	var diagonal := absf(dir.x) > 0.01 and absf(dir.y) > 0.01
	if diagonal and (facing == horizontal or facing == vertical):
		return
	facing = horizontal if absf(dir.x) > absf(dir.y) else vertical


func _update_frame() -> void:
	var col := STAND
	if moving:
		col = WALK_CYCLE[int(_walk_time * walk_fps) % WALK_CYCLE.size()]
	frame = int(facing) * hframes + col
