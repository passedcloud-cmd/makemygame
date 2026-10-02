class_name Player
extends CharacterBody2D
## 플레이어가 방향키로 조종하는 캐릭터 (주인공 A).
##
## 지나온 길(발자취)을 기록해 두고, 동료(Follower)들이 그 길을 그대로 따라온다.
## Ib처럼 동료가 졸졸 따라다니는 방식이야.

## 1초에 몇 픽셀 움직일지
@export var speed := 90.0
## 캐릭터 그림 (32x48 칸, 3열 x 4행 스프라이트 시트)
@export var sprite_sheet: Texture2D

## 발자취 점 사이의 간격 (픽셀)
const TRAIL_STEP := 1.0
## 발자취를 몇 개까지 기억할지. 동료가 많거나 간격이 넓으면 늘려야 한다.
const TRAIL_LENGTH := 120

## 지나온 위치들. 0번이 가장 최근 위치.
var trail: Array[Vector2] = []

@onready var sprite: CharacterSprite = $Sprite


func _ready() -> void:
	if sprite_sheet:
		sprite.texture = sprite_sheet
	# 처음엔 동료들이 주인공 바로 뒤(위쪽)에 줄 서 있도록 발자취를 미리 채운다.
	for i in TRAIL_LENGTH:
		trail.append(global_position + Vector2(0, -i * TRAIL_STEP))


func _physics_process(_delta: float) -> void:
	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = input * speed
	move_and_slide()

	sprite.moving = input != Vector2.ZERO
	sprite.face_towards(input)
	_record_trail(global_position)


## 새 위치를 발자취에 추가한다. 1픽셀 간격으로 촘촘하게 채워서
## 동료들이 항상 같은 거리만큼 떨어져서 따라오게 한다.
func _record_trail(pos: Vector2) -> void:
	var last := trail[0]
	var steps := int(last.distance_to(pos) / TRAIL_STEP)
	for i in range(1, steps + 1):
		trail.push_front(last.move_toward(pos, TRAIL_STEP * i))
	while trail.size() > TRAIL_LENGTH:
		trail.pop_back()
