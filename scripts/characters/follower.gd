class_name Follower
extends Node2D
## 주인공 뒤를 따라다니는 동료 (B, C).
##
## 주인공의 발자취에서 gap 픽셀 뒤의 위치로 이동한다.
## 벽에 부딪힐 일이 없도록 충돌 판정은 따로 두지 않는다.

## 따라갈 대상 (보통 Player)
@export var leader: Player
## 주인공보다 몇 픽셀 뒤에서 따라올지
@export var gap := 26
## 캐릭터 그림 (32x48 칸, 3열 x 4행 스프라이트 시트)
@export var sprite_sheet: Texture2D

@onready var sprite: CharacterSprite = $Sprite


func _ready() -> void:
	if sprite_sheet:
		sprite.texture = sprite_sheet


func _physics_process(_delta: float) -> void:
	if leader == null or leader.trail.is_empty():
		return
	var target: Vector2 = leader.trail[mini(gap, leader.trail.size() - 1)]
	var step := target - global_position
	sprite.moving = not step.is_zero_approx()
	sprite.face_towards(step)
	global_position = target
