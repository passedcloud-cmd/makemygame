class_name Player
extends CharacterBody2D
## 플레이어가 방향키로 조종하는 캐릭터 (주인공 A).
##
## 지나온 길(발자취)을 기록해 두고, 동료(Follower)들이 그 길을 그대로 따라온다.
## Ib처럼 동료가 졸졸 따라다니는 방식이야.
##
## Z: 앞에 조사할 물건이 있으면 조사, 없으면 공격.

## 1초에 몇 픽셀 움직일지
@export var speed := 90.0
## 캐릭터 그림 (32x48 칸, 3열 x 4행 스프라이트 시트)
@export var sprite_sheet: Texture2D

@export_group("공격")
## 공격 한 번의 피해량
@export var attack_damage := 1
## 다음 공격까지 기다려야 하는 시간 (초)
@export var attack_cooldown := 0.35

@export_group("피격")
## 맞은 뒤 무적 시간 (초)
@export var invincible_time := 1.0
## 맞았을 때 밀려나는 힘
@export var knockback_power := 180.0

## 바라보는 방향별로 조사 영역을 놓을 위치 (발 기준)
const INTERACT_OFFSETS := {
	CharacterSprite.Facing.DOWN: Vector2(0, 10),
	CharacterSprite.Facing.LEFT: Vector2(-14, -4),
	CharacterSprite.Facing.RIGHT: Vector2(14, -4),
	CharacterSprite.Facing.UP: Vector2(0, -14),
}
## 바라보는 방향별 공격 판정 위치
const ATTACK_OFFSETS := {
	CharacterSprite.Facing.DOWN: Vector2(0, 8),
	CharacterSprite.Facing.LEFT: Vector2(-18, -14),
	CharacterSprite.Facing.RIGHT: Vector2(18, -14),
	CharacterSprite.Facing.UP: Vector2(0, -34),
}
## 휘두르기 이펙트 회전 (그림은 오른쪽을 보고 있음)
const ATTACK_ROTATIONS := {
	CharacterSprite.Facing.DOWN: PI / 2,
	CharacterSprite.Facing.LEFT: PI,
	CharacterSprite.Facing.RIGHT: 0.0,
	CharacterSprite.Facing.UP: -PI / 2,
}
## 바라보는 방향의 반대쪽 (동료들이 줄 서는 방향)
const BEHIND := {
	CharacterSprite.Facing.DOWN: Vector2.UP,
	CharacterSprite.Facing.LEFT: Vector2.RIGHT,
	CharacterSprite.Facing.RIGHT: Vector2.LEFT,
	CharacterSprite.Facing.UP: Vector2.DOWN,
}
## 공격 판정이 살아 있는 시간 (초). 이 동안은 제자리에 멈춘다.
const ATTACK_ACTIVE := 0.15

## 발자취 점 사이의 간격 (픽셀)
const TRAIL_STEP := 1.0
## 발자취를 몇 개까지 기억할지. 동료가 많거나 간격이 넓으면 늘려야 한다.
const TRAIL_LENGTH := 120

## 지나온 위치들. 0번이 가장 최근 위치.
var trail: Array[Vector2] = []

var _attack_time := 0.0       # 남은 공격 시간
var _attack_cooldown := 0.0   # 다음 공격까지 남은 시간
var _hit_this_swing: Array[Node] = []
var _invincible := 0.0
var _knockback := Vector2.ZERO

@onready var sprite: CharacterSprite = $Sprite
@onready var interact_area: Area2D = $InteractArea
@onready var attack_area: Area2D = $AttackArea
@onready var slash: Sprite2D = $Slash


func _ready() -> void:
	if sprite_sheet:
		sprite.texture = sprite_sheet
	slash.visible = false
	reset_trail()


## 주인공을 특정 위치로 옮기고, 동료들도 바로 뒤에 줄 세운다.
func place_at(pos: Vector2, facing: CharacterSprite.Facing) -> void:
	global_position = pos
	sprite.facing = facing
	reset_trail()


## 동료들이 주인공 바로 뒤(바라보는 반대쪽)에 줄 서 있도록 발자취를 새로 채운다.
func reset_trail() -> void:
	var behind: Vector2 = BEHIND[sprite.facing]
	trail.clear()
	for i in TRAIL_LENGTH:
		trail.append(global_position + behind * i * TRAIL_STEP)


func _physics_process(delta: float) -> void:
	_attack_cooldown = maxf(_attack_cooldown - delta, 0.0)
	_update_invincible(delta)

	# 대화 중이나 방 이동 중에는 움직이지 않는다.
	if Dialogue.active or Transition.busy:
		velocity = Vector2.ZERO
		sprite.moving = false
		return

	var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	if _attack_time > 0.0:
		_update_attack(delta)
		input = Vector2.ZERO

	velocity = input * speed + _knockback
	_knockback = _knockback.move_toward(Vector2.ZERO, 900.0 * delta)
	move_and_slide()

	sprite.moving = input != Vector2.ZERO
	sprite.face_towards(input)
	interact_area.position = INTERACT_OFFSETS[sprite.facing]
	_record_trail(global_position)


## Z(확인)를 누르면 바라보는 쪽에 있는 물건을 조사하고, 없으면 공격한다.
func _unhandled_input(event: InputEvent) -> void:
	if Dialogue.active or Transition.busy:
		return
	if event.is_action_pressed("confirm"):
		for area in interact_area.get_overlapping_areas():
			if area is Interactable:
				# 같은 키 입력이 대화창에도 전달돼서 첫 줄을 건너뛰지 않도록 여기서 멈춘다.
				get_viewport().set_input_as_handled()
				area.interact()
				return
	if event.is_action_pressed("attack"):
		get_viewport().set_input_as_handled()
		_start_attack()


func _start_attack() -> void:
	if _attack_cooldown > 0.0 or _attack_time > 0.0:
		return
	_attack_cooldown = attack_cooldown
	_attack_time = ATTACK_ACTIVE
	_hit_this_swing.clear()
	attack_area.position = ATTACK_OFFSETS[sprite.facing]
	slash.position = attack_area.position
	slash.rotation = ATTACK_ROTATIONS[sprite.facing]
	slash.frame = 0
	slash.visible = true
	sprite.moving = false


func _update_attack(delta: float) -> void:
	_attack_time -= delta
	var progress := 1.0 - _attack_time / ATTACK_ACTIVE
	slash.frame = clampi(int(progress * 3), 0, 2)
	for body in attack_area.get_overlapping_bodies():
		if body.has_method("take_hit") and not body in _hit_this_swing:
			_hit_this_swing.append(body)
			body.take_hit(attack_damage, global_position)
	if _attack_time <= 0.0:
		slash.visible = false


## 몬스터에게 닿았을 때 불린다. from = 때린 쪽의 위치 (그 반대로 밀려난다)
func take_damage(amount: int, from: Vector2) -> void:
	if _invincible > 0.0 or Transition.busy or Dialogue.active:
		return
	GameState.hp -= amount
	_invincible = invincible_time
	_knockback = (global_position - from).normalized() * knockback_power
	if GameState.hp <= 0:
		_die()


func _update_invincible(delta: float) -> void:
	if _invincible <= 0.0:
		return
	_invincible -= delta
	# 무적 시간 동안 깜빡깜빡
	sprite.visible = _invincible <= 0.0 or fmod(_invincible, 0.16) < 0.1


## 쓰러지면 (지금은 임시로) 체력을 채우고 이 방을 처음부터 다시 시작한다.
func _die() -> void:
	GameState.hp = GameState.max_hp
	Transition.change_room(get_tree().current_scene.scene_file_path, "")


## 새 위치를 발자취에 추가한다. 1픽셀 간격으로 촘촘하게 채워서
## 동료들이 항상 같은 거리만큼 떨어져서 따라오게 한다.
func _record_trail(pos: Vector2) -> void:
	var last := trail[0]
	var steps := int(last.distance_to(pos) / TRAIL_STEP)
	for i in range(1, steps + 1):
		trail.push_front(last.move_toward(pos, TRAIL_STEP * i))
	while trail.size() > TRAIL_LENGTH:
		trail.pop_back()
